from fastapi import APIRouter, HTTPException, Depends
from models.user import UserCreate, UserLogin, UserInDB, UserResponse, TokenResponse
from middleware.auth import create_access_token, get_current_user
from passlib.context import CryptContext
from typing import Callable
from datetime import datetime, timezone
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database dependency will be injected
db_dependency: Callable = None

def set_db_dependency(dep: Callable):
    global db_dependency
    db_dependency = dep

def get_db():
    if db_dependency is None:
        logger.error("Database dependency not configured")
        raise HTTPException(status_code=500, detail="Database not configured")
    return db_dependency()

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """Register a new user."""
    db = get_db()
    
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        password_hash = pwd_context.hash(user_data.password)
        
        # Create user
        user = UserInDB(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash,
            role="student"
        )
        
        # Convert to dict for MongoDB
        user_dict = user.model_dump()
        user_dict['created_at'] = user_dict['created_at'].isoformat()
        user_dict['updated_at'] = user_dict['updated_at'].isoformat()
        
        try:
            await db.users.insert_one(user_dict)
            logger.info(f"New user registered: {user.email}")
        except Exception as db_error:
            logger.error(f"Failed to insert user: {db_error}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create token
        token_data = {
            "sub": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
        access_token = create_access_token(token_data)
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            purchased_courses=user.purchased_courses,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return TokenResponse(access_token=access_token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user and return JWT token."""
    db = get_db()
    
    try:
        # Find user
        user_doc = await db.users.find_one({"email": credentials.email}, {"_id": 0})
        if not user_doc:
            logger.warning(f"Login attempt with non-existent email: {credentials.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not pwd_context.verify(credentials.password, user_doc['password_hash']):
            logger.warning(f"Failed login attempt for email: {credentials.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Parse datetime if string
        created_at = user_doc['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = user_doc.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        # Update last login
        try:
            await db.users.update_one(
                {"id": user_doc['id']},
                {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
            )
        except Exception as update_error:
            logger.warning(f"Failed to update last login: {update_error}")
        
        # Create token
        token_data = {
            "sub": user_doc['id'],
            "email": user_doc['email'],
            "name": user_doc['name'],
            "role": user_doc['role']
        }
        access_token = create_access_token(token_data)
        
        logger.info(f"User logged in: {credentials.email}")
        
        user_response = UserResponse(
            id=user_doc['id'],
            email=user_doc['email'],
            name=user_doc['name'],
            role=user_doc['role'],
            purchased_courses=user_doc.get('purchased_courses', []),
            created_at=created_at,
            updated_at=updated_at
        )
        
        return TokenResponse(access_token=access_token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user."""
    db = get_db()
    
    try:
        user_doc = await db.users.find_one({"id": current_user['sub']}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Parse datetime
        created_at = user_doc['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = user_doc.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return UserResponse(
            id=user_doc['id'],
            email=user_doc['email'],
            name=user_doc['name'],
            role=user_doc['role'],
            purchased_courses=user_doc.get('purchased_courses', []),
            created_at=created_at,
            updated_at=updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get user")
