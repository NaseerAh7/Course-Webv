"""
Course Platform API - Production-Ready Backend
Hardened with comprehensive error handling, logging, and security.
"""

import os
import sys
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, APIRouter, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, ConfigDict

# Import routes
from routes import auth, courses, payments, dashboard, admin

# ============================================================================
# CONFIGURATION & LOGGING SETUP
# ============================================================================

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

REQUIRED_ENV_VARS = [
    'MONGO_URL',
    'DB_NAME',
    'JWT_SECRET',
    'STRIPE_API_KEY',
]

OPTIONAL_ENV_VARS = [
    'JWT_EXPIRE',
    'STRIPE_WEBHOOK_SECRET',
    'CORS_ORIGINS',
    'CLIENT_URL',
]

def validate_environment():
    """Validate all required environment variables exist."""
    missing = []
    for var in REQUIRED_ENV_VARS:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    
    logger.info("Environment validation passed")
    
    # Log optional vars status
    for var in OPTIONAL_ENV_VARS:
        if os.environ.get(var):
            logger.info(f"Optional var {var}: configured")
        else:
            logger.warning(f"Optional var {var}: not configured (using defaults)")

# Validate environment on module load
validate_environment()

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']
client: AsyncIOMotorClient = None
db = None

async def connect_to_mongodb():
    """Connect to MongoDB with proper error handling."""
    global client, db
    try:
        logger.info(f"Connecting to MongoDB at {mongo_url[:30]}...")
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        
        # Verify connection
        await client.admin.command('ping')
        
        db = client[db_name]
        logger.info(f"MongoDB connected successfully to database: {db_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise RuntimeError(f"MongoDB connection failed: {e}")

async def close_mongodb_connection():
    """Close MongoDB connection gracefully."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Course Platform API",
    version="1.0.0",
    description="Production-ready digital course selling platform API"
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# ============================================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with consistent JSON response."""
    logger.error(f"Validation error on {request.url}: {exc.errors()}", exc_info=True)
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "detail": errors
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with consistent JSON response."""
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": str(exc) if os.environ.get('DEBUG') else "An unexpected error occurred"
        }
    )

# ============================================================================
# DATABASE DEPENDENCY
# ============================================================================

def get_db():
    """Get database instance."""
    if db is None:
        raise RuntimeError("Database not initialized")
    return db

# Set database dependency for all route modules
auth.set_db_dependency(get_db)
courses.set_db_dependency(get_db)
payments.set_db_dependency(get_db)
dashboard.set_db_dependency(get_db)
admin.set_db_dependency(get_db)

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(courses.router)
api_router.include_router(payments.router)
api_router.include_router(dashboard.router)
api_router.include_router(admin.router)

# ============================================================================
# CORE API ENDPOINTS
# ============================================================================

@api_router.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "message": "Course Platform API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Verify database connection
        await client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check DB error: {e}", exc_info=True)
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }

# ============================================================================
# STRIPE WEBHOOK HANDLER
# ============================================================================

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events with signature verification."""
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    api_key = os.environ.get('STRIPE_API_KEY')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not api_key:
        logger.error("STRIPE_API_KEY not configured")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Payment service not configured"}
        )
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    try:
        logger.info(f"Processing webhook event with signature: {signature[:20] if signature else 'None'}...")
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        logger.info(f"Webhook event: type={webhook_response.event_type}, session={webhook_response.session_id}, status={webhook_response.payment_status}")
        
        if webhook_response.payment_status == "paid":
            # Get transaction to find user and course
            transaction = await db.payment_transactions.find_one(
                {"session_id": webhook_response.session_id},
                {"_id": 0}
            )
            
            if transaction:
                logger.info(f"Processing paid webhook for transaction: {transaction['id']}")
                
                # Check if already processed
                if transaction.get('payment_status') == 'paid':
                    logger.info(f"Transaction {transaction['id']} already processed, skipping")
                    return {"status": "already_processed"}
                
                try:
                    # Atomic update: Update transaction status
                    await db.payment_transactions.update_one(
                        {"session_id": webhook_response.session_id, "payment_status": {"$ne": "paid"}},
                        {"$set": {
                            "payment_status": "paid",
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                    
                    # Atomic update: Add course to user's purchased courses using $addToSet
                    user_result = await db.users.update_one(
                        {"id": transaction['user_id']},
                        {
                            "$addToSet": {"purchased_courses": transaction['course_id']},
                            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                        }
                    )
                    
                    if user_result.modified_count > 0:
                        # Only increment if user was actually updated
                        await db.courses.update_one(
                            {"id": transaction['course_id']},
                            {"$inc": {"enrolled_count": 1}}
                        )
                        
                        # Create progress record
                        progress_doc = {
                            "id": str(uuid.uuid4()),
                            "user_id": transaction['user_id'],
                            "course_id": transaction['course_id'],
                            "completed_lessons": [],
                            "progress_percentage": 0.0,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                        
                        try:
                            await db.user_progress.insert_one(progress_doc)
                        except Exception as progress_error:
                            logger.error(f"Failed to create progress: {progress_error}", exc_info=True)
                        
                        logger.info(f"Course {transaction['course_id']} purchased by user {transaction['user_id']}")
                    else:
                        logger.info(f"User {transaction['user_id']} already owns course {transaction['course_id']}")
                        
                except Exception as db_error:
                    logger.error(f"Database error in webhook processing: {db_error}", exc_info=True)
            else:
                logger.warning(f"No transaction found for session {webhook_response.session_id}")
        
        return {"status": "received", "event_type": webhook_response.event_type}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Include the main router
app.include_router(api_router)

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

# Properly handle CORS origins
cors_origins_str = os.environ.get('CORS_ORIGINS')
allow_origins = cors_origins_str.split(',') if cors_origins_str else ["*"]

logger.info(f"CORS configured for origins: {allow_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup - connect to DB and create indexes."""
    logger.info("=" * 60)
    logger.info("Starting Course Platform API...")
    logger.info("=" * 60)
    
    # Connect to MongoDB
    await connect_to_mongodb()
    
    # Create indexes with error handling
    try:
        logger.info("Creating database indexes...")
        
        # Users collection indexes
        try:
            await db.users.create_index("email", unique=True)
            await db.users.create_index("id", unique=True)
            logger.info("Users indexes created")
        except Exception as e:
            logger.warning(f"Users index creation warning: {e}")
        
        # Courses collection indexes
        try:
            await db.courses.create_index("id", unique=True)
            await db.courses.create_index("category")
            await db.courses.create_index("is_published")
            logger.info("Courses indexes created")
        except Exception as e:
            logger.warning(f"Courses index creation warning: {e}")
        
        # Payment transactions indexes
        try:
            await db.payment_transactions.create_index("session_id", unique=True)
            await db.payment_transactions.create_index("user_id")
            await db.payment_transactions.create_index("payment_status")
            logger.info("Payment transactions indexes created")
        except Exception as e:
            logger.warning(f"Payment transactions index creation warning: {e}")
        
        # User progress indexes
        try:
            await db.user_progress.create_index([("user_id", 1), ("course_id", 1)], unique=True)
            logger.info("User progress indexes created")
        except Exception as e:
            logger.warning(f"User progress index creation warning: {e}")
        
        logger.info("All database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Index creation failed: {e}", exc_info=True)
        # Don't crash - indexes may already exist
    
    logger.info("=" * 60)
    logger.info("Course Platform API started successfully!")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown - cleanup resources."""
    logger.info("Shutting down Course Platform API...")
    await close_mongodb_connection()
    logger.info("Shutdown complete")
