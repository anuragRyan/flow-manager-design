"""Security dependencies for authentication and authorization.

This module provides FastAPI dependencies for securing endpoints.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.models.auth import User, TokenData, UserRole
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = AuthService.decode_token(token)
    
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    user_db = AuthService.get_user(username=token_data.username)
    if user_db is None:
        raise credentials_exception
    
    if user_db.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return User(**user_db.model_dump())


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


class RoleChecker:
    def __init__(self, required_role: UserRole):
        self.required_role = required_role
    
    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if not AuthService.has_permission(current_user, self.required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {self.required_role.value}"
            )
        return current_user


require_admin = RoleChecker(UserRole.ADMIN)
require_user = RoleChecker(UserRole.USER)
require_viewer = RoleChecker(UserRole.VIEWER)
