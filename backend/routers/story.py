"""
Story router - handles story generation and retrieval endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
from models.story import StoryGenerateRequest, StoryResponse, Story
from services.llm_service import LLMService
from services.moderation import ModerationService
from services.storage import StorageService
from services.image_service import ImageService

router = APIRouter(prefix="/api/story", tags=["story"])


async def generate_images_for_story(story_id: str):
    """
    Background task to generate images for all pages in a story
    
    Args:
        story_id: Story identifier
    """
    try:
        # Reload story from storage to get current state
        story = StorageService.get_story(story_id)
        if not story:
            print(f"Story {story_id} not found for image generation")
            return
        
        pages = story.get("pages", [])
        updated = False
        
        for page in pages:
            page_number = page.get("page")
            image_prompt = page.get("image_prompt", "")
            
            # Skip if image already exists or no prompt
            if not image_prompt or page.get("image_url"):
                continue
            
            try:
                # Generate image using Azure OpenAI DALL-E
                image_bytes, image_url = await ImageService.generate_image(image_prompt)
                
                # Save image to disk
                image_path = ImageService.save_image(image_bytes, story_id, page_number)
                
                # Update page with image path
                page["image_url"] = image_path
                updated = True
                print(f"Generated image for story {story_id}, page {page_number}")
            except Exception as img_error:
                print(f"Warning: Failed to generate image for page {page_number}: {str(img_error)}")
                page["image_url"] = None
        
        # Save updated story if any images were generated
        if updated:
            story["pages"] = pages
            StorageService.save_story(story)
            print(f"Successfully updated story {story_id} with generated images")
    except Exception as e:
        print(f"Error generating images for story {story_id}: {str(e)}")


@router.post("/generate", response_model=StoryResponse)
async def generate_story(request: StoryGenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate a new children's story
    
    - Validates input
    - Runs moderation checks
    - Generates story using LLM
    - Saves story to JSON storage (with image_url = None initially)
    - Starts background task to generate images
    - Returns story with storyId immediately (images will be generated in background)
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
            detail="Story generation returned no data. Please check your Azure OpenAI configuration and quota."
        )
    
    # Prepare story for storage (with image_url = None initially)
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
    
    # Initialize image_url to None for all pages (images will be generated in background)
    for page in full_story["pages"]:
        page["image_url"] = None
    
    # Get story_id for background image generation
    story_id = full_story["storyId"]
    
    # Save story to JSON file immediately (without images)
    story_id = StorageService.save_story(full_story)
    full_story["storyId"] = story_id
    
    # Add background task to generate images
    # This will run after the response is sent to the client
    background_tasks.add_task(generate_images_for_story, story_id)
    
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


@router.get("/{storyId}/images/status")
async def get_image_status(storyId: str):
    """
    Check image generation status for a story
    
    Returns information about which images have been generated
    Useful for polling to know when all images are ready
    """
    story = StorageService.get_story(storyId)
    
    if story is None:
        raise HTTPException(
            status_code=404,
            detail=f"Story with ID '{storyId}' not found"
        )
    
    pages = story.get("pages", [])
    total_pages = len(pages)
    generated_count = sum(1 for page in pages if page.get("image_url") is not None)
    all_generated = generated_count == total_pages
    
    return {
        "storyId": storyId,
        "total_pages": total_pages,
        "generated_count": generated_count,
        "all_generated": all_generated,
        "pages": [
            {
                "page": page.get("page"),
                "image_url": page.get("image_url"),
                "has_image": page.get("image_url") is not None
            }
            for page in pages
        ]
    }

