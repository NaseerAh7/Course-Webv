from fastapi import APIRouter, HTTPException, Depends
from models.user import UserCreate, UserLogin, UserInDB, UserResponse, TokenResponse
from middleware.auth import create_access_token, get_current_user
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Callable
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database dependency will be injected
db_dependency: Callable = None

def set_db_dependency(dep: Callable):
    global db_dependency
    db_dependency = dep

def get_db():
    if db_dependency is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    return db_dependency()

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    db = get_db()
    
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
    
    await db.users.insert_one(user_dict)
    
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
        created_at=user.created_at
    )
    
    return TokenResponse(access_token=access_token, user=user_response)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    db = get_db()
    
    # Find user
    user_doc = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not pwd_context.verify(credentials.password, user_doc['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Parse datetime if string
    if isinstance(user_doc['created_at'], str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    # Create token
    token_data = {
        "sub": user_doc['id'],
        "email": user_doc['email'],
        "name": user_doc['name'],
        "role": user_doc['role']
    }
    access_token = create_access_token(token_data)
    
    user_response = UserResponse(
        id=user_doc['id'],
        email=user_doc['email'],
        name=user_doc['name'],
        role=user_doc['role'],
        purchased_courses=user_doc.get('purchased_courses', []),
        created_at=user_doc['created_at']
    )
    
    return TokenResponse(access_token=access_token, user=user_response)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    
    user_doc = await db.users.find_one({"id": current_user['sub']}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user_doc['created_at'], str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return UserResponse(
        id=user_doc['id'],
        email=user_doc['email'],
        name=user_doc['name'],
        role=user_doc['role'],
        purchased_courses=user_doc.get('purchased_courses', []),
        created_at=user_doc['created_at']
    )
