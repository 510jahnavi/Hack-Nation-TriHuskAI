from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from config import settings
from app.api import critique, generate, brand_kit

# Create necessary directories
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.brand_kit_dir, exist_ok=True)
os.makedirs(settings.generated_ads_dir, exist_ok=True)

app = FastAPI(
    title="BrandAI - AI Ad Critique System",
    description="Automated critique and improvement of AI-generated advertisements",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(critique.router, prefix="/api", tags=["Critique"])
app.include_router(generate.router, prefix="/api", tags=["Generate"])
app.include_router(brand_kit.router, prefix="/api", tags=["Brand Kit"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "BrandAI API",
        "version": "1.0.0",
        "description": "AI-powered ad critique and improvement system",
        "endpoints": {
            "critique": "/api/critique-ad",
            "generate": "/api/generate-ad",
            "improve": "/api/improve-ad",
            "brand_kit": "/api/brand-kit",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BrandAI"}


if __name__ == "__main__":
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                       BrandAI                            ║
    ║          AI-Powered Ad Critique System                   ║
    ╚══════════════════════════════════════════════════════════╝
    
    🚀 Server starting on http://{settings.app_host}:{settings.app_port}
    📚 API Documentation: http://{settings.app_host}:{settings.app_port}/docs
    🎯 Focus: AI Critique Engine (Hero Feature)
    """)
    
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
