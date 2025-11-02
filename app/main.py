"""Flow Manager FastAPI Application.

This is the main entry point for the Flow Manager microservice.
It initializes the FastAPI application, sets up logging, registers
routes, and configures middleware including security features.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config.settings import settings
from app.utils.logger import setup_logging
from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.tasks import sample_tasks  # Import to register tasks

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address) if settings.rate_limit_enabled else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events.
    
    Handles startup and shutdown events for the application.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("Security features enabled: Authentication, Rate Limiting, CORS")
    logger.info("Registered tasks: " + ", ".join(
        ["task1", "task2", "task3", "validate_data", "send_notification"]
    ))
    logger.info("Default users: admin/admin123, user/user123, viewer/viewer123")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Flow Manager Microservice - A sophisticated flow execution engine
    that manages sequential task execution with conditional branching.
    
    ## Features
    
    * 🔐 **Secure**: JWT authentication and API key support
    * 🚀 **Fast**: Async execution with FastAPI
    * 📊 **Track**: Execution state and history
    * 🔄 **Flexible**: Conditional branching based on task outcomes
    
    ## Authentication
    
    The API supports two authentication methods:
    
    1. **JWT Bearer Token**: Login at `/api/v1/auth/login` to get a token
    2. **API Key**: Pass API key in `X-API-Key` header
    
    ### Default Users
    
    - **Admin**: username=`admin`, password=`admin123`, API key=`fm_admin_key_12345`
    - **User**: username=`user`, password=`user123`, API key=`fm_user_key_67890`
    - **Viewer**: username=`viewer`, password=`viewer123` (read-only)
    
    ## User Roles
    
    - **ADMIN**: Full access including user management
    - **USER**: Can execute flows and view executions
    - **VIEWER**: Read-only access to executions
    
    ## How it works
    
    1. Authenticate to get a token or use an API key
    2. Define a flow with tasks and conditions
    3. Submit the flow via the `/api/v1/flows/execute` endpoint
    4. Tasks are executed sequentially
    5. Conditions evaluate task results and determine the next step
    6. Flow continues until completion or failure
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting if enabled
if settings.rate_limit_enabled and limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    if settings.enable_security_headers:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


# Include API routes
app.include_router(auth_router)  # Authentication routes
app.include_router(router)  # Flow management routes


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An error occurred"
        }
    )


@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "api_prefix": "/api/v1",
        "authentication": {
            "methods": ["JWT Bearer Token", "API Key"],
            "login_endpoint": "/api/v1/auth/login",
            "api_key_header": "X-API-Key"
        },
        "security_features": {
            "authentication": "enabled",
            "rate_limiting": settings.rate_limit_enabled,
            "security_headers": settings.enable_security_headers
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
