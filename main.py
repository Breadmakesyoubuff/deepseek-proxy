"""
FastAPI proxy server for DeepSeek API with OpenAI compatibility
Designed for Janitor AI integration
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from config import settings
from proxy import DeepSeekProxy
from models import ChatCompletionRequest, ChatCompletionResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize proxy
deepseek_proxy = DeepSeekProxy()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting DeepSeek OpenAI-compatible proxy server...")
    logger.info(f"DeepSeek API URL: {settings.DEEPSEEK_API_URL}")
    logger.info(f"API Key configured: {'Yes' if settings.DEEPSEEK_API_KEY != 'your-deepseek-api-key' else 'No'}")
    yield
    logger.info("Shutting down proxy server...")

# Initialize FastAPI app
app = FastAPI(
    title="DeepSeek OpenAI-Compatible Proxy",
    description="FastAPI proxy server providing OpenAI-compatible endpoints for DeepSeek API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for web-based applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "DeepSeek OpenAI-Compatible Proxy Server",
        "version": "1.0.0",
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "health": "/health",
            "docs": "/docs"
        },
        "supported_models": [
            "deepseek-chat",
            "deepseek-reasoner",
            "deepseek-ai/DeepSeek-V3-0324-Free"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Basic connectivity check
        is_healthy = await deepseek_proxy.health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "deepseek_api": "accessible" if is_healthy else "inaccessible",
            "proxy_version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest, raw_request: Request):
    """
    OpenAI-compatible chat completions endpoint
    Proxies requests to DeepSeek API with proper formatting
    """
    try:
        # Log incoming request for debugging
        logger.info(f"Chat completion request - Model: {request.model}, Messages: {len(request.messages)}, Stream: {request.stream}")
        
        # Validate model
        supported_models = ["deepseek-chat", "deepseek-reasoner", "deepseek-ai/DeepSeek-V3-0324-Free"]
        if request.model not in supported_models:
            logger.warning(f"Invalid model requested: {request.model}")
            raise HTTPException(
                status_code=400,
                detail=f"Model '{request.model}' is not supported. Use one of: {', '.join(supported_models)}"
            )
        
        # Check if streaming is requested
        if request.stream:
            # Return streaming response
            return StreamingResponse(
                deepseek_proxy.stream_chat_completion(request),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
        else:
            # Return regular JSON response
            response = await deepseek_proxy.chat_completion(request)
            return response
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with OpenAI-compatible error format"""
    from models import ErrorDetail
    error_response = ErrorResponse(
        error=ErrorDetail(
            message=exc.detail,
            type="invalid_request_error" if exc.status_code == 400 else "api_error",
            code=exc.status_code
        )
    )
    
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unexpected errors"""
    logger.error(f"Unhandled exception: {str(exc)}")
    
    from models import ErrorDetail
    error_response = ErrorResponse(
        error=ErrorDetail(
            message="An unexpected error occurred",
            type="api_error",
            code=500
        )
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )

if __name__ == "__main__":
    # Railway sets PORT environment variable
    import os
    port = int(os.environ.get("PORT", 5000))
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False
    )
