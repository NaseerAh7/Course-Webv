import uuid
from fastapi import APIRouter, HTTPException, Depends, Request
from models.purchase import PaymentTransactionInDB
from middleware.auth import get_current_user
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, 
    CheckoutSessionResponse, 
    CheckoutStatusResponse, 
    CheckoutSessionRequest
)
from typing import Callable
from datetime import datetime, timezone
import os
import logging

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)

# Database dependency
db_dependency: Callable = None

def set_db_dependency(dep: Callable):
    global db_dependency
    db_dependency = dep

def get_db():
    if db_dependency is None:
        logger.error("Database dependency not configured")
        raise HTTPException(status_code=500, detail="Database not configured")
    return db_dependency()

def get_stripe_checkout(request: Request) -> StripeCheckout:
    """Initialize Stripe checkout with proper error handling."""
    api_key = os.environ.get('STRIPE_API_KEY')
    if not api_key:
        logger.error("STRIPE_API_KEY not configured in environment")
        raise HTTPException(status_code=500, detail="Payment service not configured")
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    return StripeCheckout(api_key=api_key, webhook_url=webhook_url)

@router.post("/checkout/{course_id}")
async def create_checkout_session(
    course_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Create a Stripe checkout session for course purchase."""
    db = get_db()
    
    try:
        # Get course
        course = await db.courses.find_one({"id": course_id}, {"_id": 0})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if already purchased
        user_doc = await db.users.find_one({"id": current_user['sub']}, {"_id": 0})
        if user_doc and course_id in user_doc.get('purchased_courses', []):
            raise HTTPException(status_code=400, detail="Course already purchased")
        
        # Get host URL from request for dynamic URLs
        host_url = str(request.base_url).rstrip('/')
        
        # Build URLs dynamically - NEVER hardcode these
        success_url = f"{host_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{host_url}/payment/cancel"
        
        # Initialize Stripe
        stripe_checkout = get_stripe_checkout(request)
        
        # Create checkout session metadata
        metadata = {
            "user_id": current_user['sub'],
            "user_email": current_user['email'],
            "course_id": course_id,
            "course_title": course['title']
        }
        
        # Amount must be float for Stripe
        checkout_request = CheckoutSessionRequest(
            amount=float(course['price']),
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        logger.info(f"Creating checkout session for user {current_user['email']}, course {course_id}")
        
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record BEFORE redirecting to Stripe
        transaction_id = str(uuid.uuid4())
        transaction = PaymentTransactionInDB(
            id=transaction_id,
            user_id=current_user['sub'],
            user_email=current_user['email'],
            course_id=course_id,
            amount=float(course['price']),
            currency="usd",
            session_id=session.session_id,
            payment_status="initiated",
            metadata=metadata
        )
        
        transaction_dict = transaction.model_dump()
        transaction_dict['created_at'] = transaction_dict['created_at'].isoformat()
        transaction_dict['updated_at'] = transaction_dict['updated_at'].isoformat()
        
        try:
            await db.payment_transactions.insert_one(transaction_dict)
            logger.info(f"Payment transaction {transaction_id} created for session {session.session_id}")
        except Exception as db_error:
            logger.error(f"Failed to create payment transaction: {db_error}", exc_info=True)
            # Don't fail the checkout - user can still complete payment
            # Transaction will be created on webhook/status check
        
        return {"checkout_url": session.url, "session_id": session.session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")

@router.get("/status/{session_id}")
async def get_payment_status(
    session_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Poll payment status and update database atomically."""
    db = get_db()
    
    try:
        # Get transaction
        transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
        if not transaction:
            logger.warning(f"Transaction not found for session {session_id}")
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Verify user owns this transaction
        if transaction['user_id'] != current_user['sub']:
            logger.warning(f"Unauthorized access attempt to transaction {session_id} by user {current_user['sub']}")
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Check with Stripe
        stripe_checkout = get_stripe_checkout(request)
        
        status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        logger.info(f"Payment status for session {session_id}: {status.payment_status}")
        
        # Determine new status
        new_status = "pending"
        if status.payment_status == "paid":
            new_status = "paid"
        elif status.status == "expired":
            new_status = "expired"
        
        # Only process if status changed to paid and not already processed
        if new_status == "paid" and transaction['payment_status'] != "paid":
            logger.info(f"Processing successful payment for session {session_id}")
            
            try:
                # Update transaction status first
                await db.payment_transactions.update_one(
                    {"session_id": session_id, "payment_status": {"$ne": "paid"}},
                    {"$set": {
                        "payment_status": new_status,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                # Atomic update: Add course to user's purchased courses using $addToSet
                user_update_result = await db.users.update_one(
                    {"id": current_user['sub']},
                    {
                        "$addToSet": {"purchased_courses": transaction['course_id']},
                        "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                    }
                )
                
                if user_update_result.modified_count > 0:
                    # Only increment enrolled count if user was actually updated (not duplicate)
                    await db.courses.update_one(
                        {"id": transaction['course_id']},
                        {"$inc": {"enrolled_count": 1}}
                    )
                    
                    # Create initial progress record
                    progress_id = str(uuid.uuid4())
                    progress_doc = {
                        "id": progress_id,
                        "user_id": current_user['sub'],
                        "course_id": transaction['course_id'],
                        "completed_lessons": [],
                        "progress_percentage": 0.0,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    try:
                        await db.user_progress.insert_one(progress_doc)
                        logger.info(f"Created progress record {progress_id} for user {current_user['sub']}")
                    except Exception as progress_error:
                        logger.error(f"Failed to create progress record: {progress_error}", exc_info=True)
                    
                    logger.info(f"Course {transaction['course_id']} added to user {current_user['sub']}")
                else:
                    logger.info(f"Course {transaction['course_id']} already owned by user {current_user['sub']}")
                    
            except Exception as db_error:
                logger.error(f"Database error during payment processing: {db_error}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to process payment")
        
        elif new_status != "paid" and transaction['payment_status'] != new_status:
            # Update status for non-paid states
            try:
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {
                        "payment_status": new_status,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
            except Exception as db_error:
                logger.error(f"Failed to update transaction status: {db_error}", exc_info=True)
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency,
            "course_id": transaction['course_id']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error checking payment status: {str(e)}")

@router.get("/history")
async def get_payment_history(current_user: dict = Depends(get_current_user)):
    """Get payment history for current user (last 50 transactions)."""
    db = get_db()
    
    try:
        transactions = await db.payment_transactions.find(
            {"user_id": current_user['sub']},
            {"_id": 0}
        ).sort("created_at", -1).limit(50).to_list(50)
        
        logger.info(f"Retrieved {len(transactions)} transactions for user {current_user['sub']}")
        return transactions
        
    except Exception as e:
        logger.error(f"Failed to get payment history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve payment history")
