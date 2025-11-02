"""Authentication routes for login, registration, and API key management."""

import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.auth import Token, LoginRequest, User, UserCreate
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_active_user, require_admin
from app.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(login_request: LoginRequest):
    user = AuthService.authenticate_user(
        login_request.username,
        login_request.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes
    )
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User '{user.username}' logged in successfully")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    current_user: User = Depends(require_admin)
):
    try:
        user = AuthService.create_user(
            username=user_create.username,
            email=user_create.email,
            password=user_create.password,
            full_name=user_create.full_name,
            role=user_create.role
        )
        
        logger.info(
            f"Admin '{current_user.username}' created new user: "
            f"{user.username}"
        )
        
        return User(**user.model_dump())
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/users", response_model=list[User])
async def list_users(current_user: User = Depends(require_admin)):
    from app.services.auth_service import fake_users_db
    
    users = [User(**user.model_dump()) for user in fake_users_db.values()]
    return users
