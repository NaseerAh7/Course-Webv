from fastapi import APIRouter, HTTPException, Depends, Request
from models.purchase import PurchaseCreate, PaymentTransactionInDB
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
        raise HTTPException(status_code=500, detail="Database not configured")
    return db_dependency()

@router.post("/checkout/{course_id}")
async def create_checkout_session(
    course_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    
    # Get course
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already purchased
    user_doc = await db.users.find_one({"id": current_user['sub']}, {"_id": 0})
    if user_doc and course_id in user_doc.get('purchased_courses', []):
        raise HTTPException(status_code=400, detail="Course already purchased")
    
    # Get host URL from request
    host_url = str(request.base_url).rstrip('/')
    
    # Build URLs dynamically
    success_url = f"{host_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url}/payment/cancel"
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    # Initialize Stripe
    api_key = os.environ.get('STRIPE_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    # Create checkout session
    metadata = {
        "user_id": current_user['sub'],
        "user_email": current_user['email'],
        "course_id": course_id,
        "course_title": course['title']
    }
    
    checkout_request = CheckoutSessionRequest(
        amount=float(course['price']),
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata
    )
    
    try:
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = PaymentTransactionInDB(
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
        
        await db.payment_transactions.insert_one(transaction_dict)
        
        return {"checkout_url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")

@router.get("/status/{session_id}")
async def get_payment_status(
    session_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    
    # Get transaction
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Verify user owns this transaction
    if transaction['user_id'] != current_user['sub']:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Get host URL for webhook
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    # Check with Stripe
    api_key = os.environ.get('STRIPE_API_KEY')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    try:
        status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction status
        new_status = "pending"
        if status.payment_status == "paid":
            new_status = "paid"
        elif status.status == "expired":
            new_status = "expired"
        
        # Only process if status changed to paid and not already processed
        if new_status == "paid" and transaction['payment_status'] != "paid":
            # Update transaction
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "payment_status": new_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Add course to user's purchased courses
            await db.users.update_one(
                {"id": current_user['sub']},
                {"$addToSet": {"purchased_courses": transaction['course_id']}}
            )
            
            # Increment course enrolled count
            await db.courses.update_one(
                {"id": transaction['course_id']},
                {"$inc": {"enrolled_count": 1}}
            )
            
            # Create initial progress record
            progress_doc = {
                "id": str(__import__('uuid').uuid4()),
                "user_id": current_user['sub'],
                "course_id": transaction['course_id'],
                "completed_lessons": [],
                "progress_percentage": 0.0,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.user_progress.insert_one(progress_doc)
        
        elif new_status != "paid" and transaction['payment_status'] != new_status:
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "payment_status": new_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency,
            "course_id": transaction['course_id']
        }
        
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking payment status: {str(e)}")

@router.get("/history")
async def get_payment_history(current_user: dict = Depends(get_current_user)):
    db = get_db()
    
    transactions = await db.payment_transactions.find(
        {"user_id": current_user['sub']},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return transactions
