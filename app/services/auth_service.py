"""Authentication and security service.

This module provides JWT token generation, password hashing,
and user authentication functionality.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from app.models.auth import User, UserInDB, TokenData, UserRole
from app.config.settings import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: Dict[str, UserInDB] = {
    "admin": UserInDB(
        username="admin",
        email="admin@flowmanager.com",
        full_name="System Administrator",
        role=UserRole.ADMIN,
        hashed_password=pwd_context.hash("admin123"),
        disabled=False
    ),
    "user": UserInDB(
        username="user",
        email="user@flowmanager.com",
        full_name="Regular User",
        role=UserRole.USER,
        hashed_password=pwd_context.hash("user123"),
        disabled=False
    ),
    "viewer": UserInDB(
        username="viewer",
        email="viewer@flowmanager.com",
        full_name="Read Only User",
        role=UserRole.VIEWER,
        hashed_password=pwd_context.hash("viewer123"),
        disabled=False
    )
}


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def get_user(username: str) -> Optional[UserInDB]:
        if username in fake_users_db:
            return fake_users_db[username]
        return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
        user = AuthService.get_user(username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        if user.disabled:
            return None
        return user
    
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            username: str = payload.get("sub")
            role: str = payload.get("role")
            
            if username is None:
                return None
            
            return TokenData(
                username=username,
                role=UserRole(role) if role else None
            )
        except JWTError as e:
            logger.error(f"JWT decode error: {e}")
            return None
    
    @staticmethod
    def create_user(
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER
    ) -> UserInDB:
        if username in fake_users_db:
            raise ValueError(f"Username '{username}' already exists")
        
        user = UserInDB(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            hashed_password=AuthService.get_password_hash(password),
            disabled=False
        )
        
        fake_users_db[username] = user
        logger.info(f"Created new user: {username}")
        
        return user
    
    @staticmethod
    def has_permission(user: User, required_role: UserRole) -> bool:
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.USER: 2,
            UserRole.ADMIN: 3
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
