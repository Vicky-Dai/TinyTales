"""
Story data models for StorySprout AI
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class StoryGenerateRequest(BaseModel):
    """Request model for story generation"""
    age_range: str = Field(..., description="Age range (e.g., '4-7', '6-9')")
    language: str = Field(default="en", description="Language code")
    moral: str = Field(..., description="Moral or lesson of the story")
    characters: List[str] = Field(..., description="List of characters")
    setting: str = Field(..., description="Story setting")
    tone: str = Field(default="warm", description="Story tone (warm, playful, gentle, etc.)")
    pages: int = Field(default=5, ge=3, le=8, description="Number of pages (3-8)")


class StoryPage(BaseModel):
    """Individual page of a story"""
    page: int = Field(..., description="Page number")
    text: str = Field(..., description="Story text for this page")
    image_prompt: str = Field(..., description="Image generation prompt for this page")


class StoryResponse(BaseModel):
    """Response model for generated story"""
    storyId: str = Field(..., description="Unique story identifier")
    title: str = Field(..., description="Story title")
    pages: List[StoryPage] = Field(..., description="List of story pages")
    age_range: str = Field(..., description="Target age range")
    moral: str = Field(..., description="Story moral")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class Story(BaseModel):
    """Complete story model for storage"""
    storyId: str
    title: str
    pages: List[StoryPage]
    age_range: str
    language: str
    moral: str
    characters: List[str]
    setting: str
    tone: str
    created_at: str

