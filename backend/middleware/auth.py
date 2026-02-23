"""
Authentication Middleware
JWT token creation, verification, and user extraction.
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from pathlib import Path

import jwt
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

logger = logging.getLogger(__name__)

security = HTTPBearer()

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7  # Default expiration

def get_jwt_secret() -> str:
    """Get JWT_SECRET from environment with validation."""
    secret = os.environ.get('JWT_SECRET')
    if not secret:
        logger.error("JWT_SECRET not configured in environment")
        raise RuntimeError("JWT_SECRET not configured")
    return secret

def get_jwt_expire_days() -> int:
    """Parse JWT_EXPIRE environment variable."""
    expire_str = os.environ.get('JWT_EXPIRE', '7d')
    try:
        if expire_str.endswith('d'):
            return int(expire_str[:-1])
        elif expire_str.endswith('h'):
            return int(expire_str[:-1]) / 24
        return int(expire_str)
    except ValueError:
        return 7

def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing user data (sub, email, name, role)
    
    Returns:
        Encoded JWT token string
    """
    jwt_secret = get_jwt_secret()
    
    to_encode = data.copy()
    expire_days = get_jwt_expire_days()
    expire = datetime.now(timezone.utc) + timedelta(days=expire_days)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })
    
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=JWT_ALGORITHM)
    logger.debug(f"Created token for user: {data.get('email')}")
    return encoded_jwt

def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        jwt_secret = get_jwt_secret()
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Authentication service not configured")
    
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from request
    
    Returns:
        Decoded user payload from token
    
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    # Validate required fields
    if not payload.get('sub'):
        logger.warning("Token missing 'sub' field")
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    return payload

async def get_optional_user(request: Request) -> Optional[dict]:
    """
    Get the current user if authenticated, otherwise return None.
    Used for routes that work for both authenticated and anonymous users.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Decoded user payload or None
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        return decode_token(token)
    except HTTPException:
        return None
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Require the current user to have admin role.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user if they are admin
    
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != "admin":
        logger.warning(f"Non-admin user {current_user.get('email')} attempted admin action")
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
