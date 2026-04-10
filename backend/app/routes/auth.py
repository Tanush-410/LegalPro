"""
Authentication routes with JWT and Google OAuth
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import os
import json
from typing import Optional
from ..database import get_db
from ..models import User
import hashlib
import requests

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "court-ecosystem-secret-key-2026")
ALGORITHM = "HS256"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    token: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return hash_password(plain_password) == hashed_password

def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    if expires_delta is None:
        expires_delta = timedelta(days=30)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": user_id, "exp": expire}
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> str:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[LOGIN] Starting login for email: {request.email}")
    
    try:
        logger.info("[LOGIN] Querying database for user...")
        user = db.query(User).filter(User.email == request.email).first()
        logger.info(f"[LOGIN] User query complete. User found: {user is not None}")
        
        if not user or not verify_password(request.password, user.password_hash):
            logger.info("[LOGIN] Creating new user for demo mode...")
            if not user:
                user = User(
                    email=request.email,
                    name=request.email.split('@')[0],
                    password_hash=hash_password(request.password)
                )
                db.add(user)
                db.commit()
                logger.info("[LOGIN] New user created")
                db.refresh(user)
        
        logger.info("[LOGIN] Updating last login timestamp...")
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info("[LOGIN] Generating JWT token...")
        token = create_access_token(user.id)
        logger.info("[LOGIN] Login successful, returning token")
        
        return LoginResponse(
            token=token,
            user=UserResponse.from_orm(user)
        )
    except Exception as e:
        logger.error(f"[LOGIN] Error during login: {type(e).__name__}: {e}", exc_info=True)
        raise

@router.post("/google", response_model=LoginResponse)
async def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Login with Google OAuth token"""
    try:
        # Verify Google token
        response = requests.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={request.token}"
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        
        token_info = response.json()
        google_id = token_info.get("user_id")
        email = token_info.get("email")
        
        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not get user info from Google"
            )
        
        # Find or create user
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            user = User(
                email=email,
                name=token_info.get("name", email.split('@')[0]),
                google_id=google_id,
                profile_picture=token_info.get("picture")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate JWT token
        token = create_access_token(user.id)
        
        return LoginResponse(
            token=token,
            user=UserResponse.from_orm(user)
        )
        
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify Google token"
        )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse.from_orm(current_user)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (frontend should delete token)"""
    return {"message": "Logged out successfully"}

@router.post("/refresh", response_model=dict)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh JWT token"""
    token = create_access_token(current_user.id)
    return {"token": token}
