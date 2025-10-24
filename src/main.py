"""
FastAPI application entry point for Web Content Analysis Agent.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from src.api.endpoints import router
from src.config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Web Content Analysis Agent...")
    yield
    logger.info("Shutting down Web Content Analysis Agent...")

# Create FastAPI application
app = FastAPI(
    title="Web Content Analysis Agent",
    description="Advanced semantic analysis and categorization of web content using Azure OpenAI GPT-4o",
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    lifespan=lifespan
)

# Add CORS middleware
allowed_origins = ["*"] if settings.environment == "development" else [
    "https://your-domain.com",  # Replace with your actual domain
    "https://web-content-analyzer-production-88c3.up.railway.app",  # Railway domain
    "https://web-content-analyzer.onrender.com",  # Example: Render domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Add bulk upload interface route (without prefix for easy access)
from fastapi.responses import FileResponse
from pathlib import Path

@app.get("/bulk-upload", response_class=FileResponse)
async def get_bulk_upload_interface():
    """Serve the bulk upload HTML interface."""
    html_path = Path(__file__).parent.parent / "bulk_upload_interface.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Bulk upload interface not found")
    return FileResponse(html_path)

# Add exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    from fastapi.responses import JSONResponse
    from src.models.responses import ErrorResponse
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_ERROR",
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    from fastapi.responses import JSONResponse
    from src.models.responses import ErrorResponse
    
    logger.error(f"Unhandled exception: {str(exc)}")
    
    # Create error response with proper serialization
    error_response = ErrorResponse(
        error="INTERNAL_ERROR",
        message=str(exc) if str(exc) else "An internal error occurred",
        details={"exception_type": type(exc).__name__}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(mode='json')
    )

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Web Content Analysis Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "web-content-analysis-agent",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )