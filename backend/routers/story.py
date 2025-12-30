"""
Story router - handles story generation and retrieval endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
from models.story import StoryGenerateRequest, StoryResponse, Story
from services.llm_service import LLMService
from services.moderation import ModerationService
from services.storage import StorageService

router = APIRouter(prefix="/api/story", tags=["story"])


@router.post("/generate", response_model=StoryResponse)
async def generate_story(request: StoryGenerateRequest):
    """
    Generate a new children's story
    
    - Validates input
    - Runs moderation checks
    - Generates story using LLM
    - Saves story to JSON storage
    - Returns story with storyId
    """
    # Convert request to dict for validation
    request_dict = request.model_dump()
    
    # Validate input
    is_valid, error_msg = ModerationService.validate_input(request_dict)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Check moderation on input
    input_text = f"{request.moral} {request.setting} {' '.join(request.characters)}"
    is_safe, moderation_result = await ModerationService.check_moderation(input_text)
    if not is_safe:
        raise HTTPException(
            status_code=400,
            detail="Input failed moderation check. Please use kid-friendly content."
        )
    
    # Generate story using LLM
    try:
        story_data = await LLMService.generate_story(request_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Story generation failed: {str(e)}"
        )
    
    # Validate story_data was returned
    if story_data is None:
        raise HTTPException(
            status_code=500,
            detail="Story generation returned no data. Please check your OpenAI API key and quota."
        )
    
    # Prepare story for storage
    full_story = {
        "storyId": StorageService.generate_story_id(),
        "title": story_data["title"],
        "pages": story_data["pages"],
        "age_range": request.age_range,
        "language": request.language,
        "moral": request.moral,
        "characters": request.characters,
        "setting": request.setting,
        "tone": request.tone
    }
    
    # Save story to JSON file
    story_id = StorageService.save_story(full_story)
    full_story["storyId"] = story_id
    
    # Return response
    return StoryResponse(
        storyId=story_id,
        title=full_story["title"],
        pages=full_story["pages"],
        age_range=full_story["age_range"],
        moral=full_story["moral"],
        created_at=full_story.get("created_at")
    )


@router.get("/{storyId}", response_model=Story)
async def get_story(storyId: str):
    """
    Retrieve a saved story by ID
    
    - Looks up story in JSON storage
    - Returns full story data
    """
    story = StorageService.get_story(storyId)
    
    if story is None:
        raise HTTPException(
            status_code=404,
            detail=f"Story with ID '{storyId}' not found"
        )
    
    return Story(**story)

