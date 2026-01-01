"""
FastAPI main application for StorySprout AI
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing other modules
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import story

# Create FastAPI app
app = FastAPI(
    title="StorySprout AI",
    description="AI-powered children's story generator",
    version="1.0.0"
)

# Configure CORS
# Get allowed origins from environment variable or use wildcard for development
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # In production, set ALLOWED_ORIGINS env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(story.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StorySprout AI API",
        "version": "1.0.0",
        "endpoints": {
            "generate_story": "POST /api/story/generate",
            "get_story": "GET /api/story/{storyId}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

