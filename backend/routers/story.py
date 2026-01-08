"""
Story router - handles story generation and retrieval endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
from pydantic import BaseModel
from models.story import StoryGenerateRequest, StoryResponse, Story
from services.llm_service import LLMService
from services.moderation import ModerationService
from services.storage import StorageService
from services.image_service import ImageService
from services.tts_service import TTSService
from services.agentic_service import AgenticService

router = APIRouter(prefix="/api/story", tags=["story"])


class AgenticStoryRequest(BaseModel):
    """Request model for agentic story generation with natural language prompt"""
    prompt: str


async def generate_images_for_story(story_id: str):
    """
    Background task to generate images for all pages in a story
    
    Args:
        story_id: Story identifier
    """
    print(f"[IMAGE GEN] Starting image generation for story {story_id}")
    try:
        # Reload story from storage to get current state
        story = StorageService.get_story(story_id)
        if not story:
            print(f"[IMAGE GEN] ERROR: Story {story_id} not found for image generation")
            return
        
        pages = story.get("pages", [])
        print(f"[IMAGE GEN] Found {len(pages)} pages to process")
        updated = False
        
        for page in pages:
            page_number = page.get("page")
            image_prompt = page.get("image_prompt", "")
            
            print(f"[IMAGE GEN] Page {page_number}: prompt='{image_prompt[:50]}...', has_url={bool(page.get('image_url'))}")
            
            # Skip if image already exists or no prompt
            if not image_prompt or page.get("image_url"):
                print(f"[IMAGE GEN] Skipping page {page_number} (already has image or no prompt)")
                continue
            
            try:
                print(f"[IMAGE GEN] Generating image for page {page_number}...")
                # Generate image using Azure OpenAI FLUX
                image_bytes, image_url = await ImageService.generate_image(image_prompt)
                
                # Save image to disk
                image_path = ImageService.save_image(image_bytes, story_id, page_number)
                
                # Update page with image path
                page["image_url"] = image_path
                updated = True
                print(f"[IMAGE GEN] SUCCESS: Generated image for story {story_id}, page {page_number} at {image_path}")
            except Exception as img_error:
                error_str = str(img_error)
                print(f"[IMAGE GEN] ERROR: Failed to generate image for page {page_number}: {error_str}")
                
                # If content filter triggered, try with a simplified generic prompt
                if "blocklist" in error_str.lower() or "content rejected" in error_str.lower():
                    print(f"[IMAGE GEN] Retrying page {page_number} with simplified prompt...")
                    try:
                        # Use a very simple, generic prompt
                        simple_prompt = f"A cheerful children's book illustration in warm colors, suitable for ages 4-7"
                        image_bytes, image_url = await ImageService.generate_image(simple_prompt)
                        image_path = ImageService.save_image(image_bytes, story_id, page_number)
                        page["image_url"] = image_path
                        updated = True
                        print(f"[IMAGE GEN] SUCCESS (retry): Generated generic image for page {page_number}")
                    except Exception as retry_error:
                        print(f"[IMAGE GEN] Retry also failed for page {page_number}: {str(retry_error)}")
                        page["image_url"] = None
                else:
                    page["image_url"] = None
        
        # Save updated story if any images were generated
        if updated:
            story["pages"] = pages
            StorageService.save_story(story)
            print(f"[IMAGE GEN] Successfully updated story {story_id} with generated images")
        else:
            print(f"[IMAGE GEN] No images were generated for story {story_id}")
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
    
    # Initialize image_url and audio_url to None for all pages (will be generated in background)
    for page in full_story["pages"]:
        page["image_url"] = None
        page["audio_url"] = None
    
    # Get story_id for background image generation
    story_id = full_story["storyId"]
    
    # Save story to JSON file immediately (without images)
    story_id = StorageService.save_story(full_story)
    full_story["storyId"] = story_id
    
    # Add background task to generate images
    # This will run after the response is sent to the client
    background_tasks.add_task(generate_images_for_story, story_id)
    
    # Add background task to generate audio
    background_tasks.add_task(generate_audio_for_story, story_id)
    
    # Return response
    return StoryResponse(
        storyId=story_id,
        title=full_story["title"],
        pages=full_story["pages"],
        age_range=full_story["age_range"],
        moral=full_story["moral"],
        created_at=full_story.get("created_at")
    )


@router.post("/generate-agentic", response_model=StoryResponse)
async def generate_story_agentic(request: AgenticStoryRequest):
    """
    🤖 Agentic Story Generation - Natural language prompt processing
    
    Multi-step LLM process:
    1. LLM Call 1 (Gate): Analyzes if user needs emotional support or just wants a story
    2. LLM Call 2 (Extract): Extracts story parameters, adjusts moral/tone if support needed
    3. LLM Call 3 (Generate): Creates the actual story with text and image prompts
    4. Generates images and audio synchronously before returning
    
    Example prompts:
    - "I'm feeling sad today, can you make me a story?"
    - "Create a story about a brave lion for a 6 year old"
    - "My kid loves dinosaurs, make something fun"
    """
    print(f"\n[AGENTIC] Starting agentic story generation...")
    print(f"[AGENTIC] User prompt: '{request.prompt}'")
    
    try:
        # LLM Call 1: Gate - Analyze user intent
        gate_result = await AgenticService.gate_analyze_prompt(request.prompt)
        needs_support = gate_result.get("needs_support", False)
        
        print(f"[AGENTIC] Gate analysis: needs_support={needs_support}")
        if needs_support:
            print(f"[AGENTIC] 💙 User needs emotional support - creating uplifting story")
        
        # LLM Call 2: Extract story parameters (adjusted if support needed)
        story_params = await AgenticService.extract_story_parameters(request.prompt, needs_support)
        
        print(f"[AGENTIC] Extracted parameters:")
        print(f"  - Age range: {story_params.get('age_range')}")
        print(f"  - Moral: {story_params.get('moral')}")
        print(f"  - Characters: {story_params.get('characters')}")
        print(f"  - Setting: {story_params.get('setting')}")
        print(f"  - Tone: {story_params.get('tone')}")
        print(f"  - Pages: {story_params.get('pages')}")
        
        # Validate extracted parameters
        is_valid, error_msg = ModerationService.validate_input(story_params)
        if not is_valid:
            # Generate a clarifying question instead of throwing error
            print(f"[AGENTIC] Validation failed: {error_msg}")
            print(f"[AGENTIC] Generating clarification question...")
            clarification = await AgenticService.generate_clarification_question(request.prompt, error_msg)
            raise HTTPException(
                status_code=400, 
                detail=f"I need some clarification: {clarification}"
            )
        
        # LLM Call 3: Generate the actual story
        print(f"[AGENTIC] LLM Call 3: Generating story...")
        story_data = await LLMService.generate_story(story_params)
        
        if story_data is None:
            raise HTTPException(
                status_code=500,
                detail="Story generation returned no data."
            )
        
        # Prepare full story for storage
        full_story = {
            "storyId": StorageService.generate_story_id(),
            "title": story_data["title"],
            "pages": story_data["pages"],
            "age_range": story_params["age_range"],
            "language": story_params.get("language", "en"),
            "moral": story_params["moral"],
            "characters": story_params["characters"],
            "setting": story_params["setting"],
            "tone": story_params["tone"],
            "needs_support": needs_support  # Track if this was a support story
        }
        
        # Initialize image_url and audio_url to None (will be generated)
        for page in full_story["pages"]:
            page["image_url"] = None
            page["audio_url"] = None
        
        # Save story
        story_id = StorageService.save_story(full_story)
        full_story["storyId"] = story_id
        
        print(f"[AGENTIC] Story saved with ID: {story_id}")
        
        # Generate images and audio synchronously (wait for completion)
        print(f"[AGENTIC] Generating images and audio...")
        await generate_images_for_story(story_id)
        await generate_audio_for_story(story_id)
        
        # Reload story to get updated image_url and audio_url
        updated_story = StorageService.get_story(story_id)
        
        print(f"[AGENTIC] ✅ Story fully generated with all media!\n")
        
        # Return response with complete story including media
        return StoryResponse(
            storyId=story_id,
            title=updated_story["title"],
            pages=updated_story["pages"],
            age_range=updated_story["age_range"],
            moral=updated_story["moral"],
            created_at=updated_story.get("created_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AGENTIC] ❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Agentic story generation failed: {str(e)}"
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


async def generate_audio_for_story(story_id: str):
    """
    Background task to generate audio for all pages in a story
    
    Args:
        story_id: Story identifier
    """
    print(f"[AUDIO GEN] Starting audio generation for story {story_id}")
    try:
        # Reload story from storage to get current state
        story = StorageService.get_story(story_id)
        if not story:
            print(f"[AUDIO GEN] ERROR: Story {story_id} not found for audio generation")
            return
        
        pages = story.get("pages", [])
        language = story.get("language", "en")
        print(f"[AUDIO GEN] Found {len(pages)} pages, language={language}")
        updated = False
        
        for page in pages:
            page_number = page.get("page")
            text = page.get("text", "")
            
            print(f"[AUDIO GEN] Page {page_number}: text length={len(text)}, has_audio={bool(page.get('audio_url'))}")
            
            # Skip if audio already exists or no text
            if not text or page.get("audio_url"):
                print(f"[AUDIO GEN] Skipping page {page_number} (already has audio or no text)")
                continue
            
            try:
                print(f"[AUDIO GEN] Generating audio for page {page_number}...")
                # Generate audio using Azure Speech Services
                audio_bytes = TTSService.synthesize_text(text, language)
                
                # Save audio to disk
                audio_path = TTSService.save_audio(audio_bytes, story_id, page_number)
                
                # Update page with audio path
                page["audio_url"] = audio_path
                updated = True
                print(f"[AUDIO GEN] SUCCESS: Generated audio for story {story_id}, page {page_number} at {audio_path}")
            except Exception as audio_error:
                print(f"[AUDIO GEN] ERROR: Failed to generate audio for page {page_number}")
                print(f"[AUDIO GEN] Error type: {type(audio_error).__name__}")
                print(f"[AUDIO GEN] Error details: {repr(audio_error)}")
                import traceback
                print(f"[AUDIO GEN] Traceback: {traceback.format_exc()}")
                page["audio_url"] = None
        
        # Save updated story if any audio was generated
        if updated:
            story["pages"] = pages
            StorageService.save_story(story)
            print(f"[AUDIO GEN] Successfully updated story {story_id} with generated audio")
        else:
            print(f"[AUDIO GEN] No audio was generated for story {story_id}")
    except Exception as e:
        print(f"[AUDIO GEN] CRITICAL ERROR: {str(e)}")
        import traceback
        print(f"[AUDIO GEN] Traceback: {traceback.format_exc()}")


@router.post("/{storyId}/audio/generate")
async def generate_story_audio(storyId: str, background_tasks: BackgroundTasks):
    """
    Generate audio for all pages in a story
    
    - Generates TTS audio for each page in the background
    - Updates story with audio URLs as they're generated
    - Returns immediately (audio generation happens in background)
    """
    story = StorageService.get_story(storyId)
    
    if story is None:
        raise HTTPException(
            status_code=404,
            detail=f"Story with ID '{storyId}' not found"
        )
    
    # Start background task to generate audio
    background_tasks.add_task(generate_audio_for_story, storyId)
    
    return {
        "message": "Audio generation started",
        "storyId": storyId,
        "status": "processing"
    }


@router.post("/{storyId}/audio/page/{pageNumber}")
async def generate_page_audio(storyId: str, pageNumber: int):
    """
    Generate audio for a specific page in a story
    
    - Generates TTS audio for the specified page
    - Updates story with audio URL
    - Returns the audio file path
    """
    story = StorageService.get_story(storyId)
    
    if story is None:
        raise HTTPException(
            status_code=404,
            detail=f"Story with ID '{storyId}' not found"
        )
    
    pages = story.get("pages", [])
    
    # Find the page
    page = None
    for p in pages:
        if p.get("page") == pageNumber:
            page = p
            break
    
    if page is None:
        raise HTTPException(
            status_code=404,
            detail=f"Page {pageNumber} not found in story {storyId}"
        )
    
    text = page.get("text", "")
    if not text:
        raise HTTPException(
            status_code=400,
            detail=f"Page {pageNumber} has no text to convert to speech"
        )
    
    # Check if audio already exists
    if page.get("audio_url"):
        return {
            "message": "Audio already exists",
            "storyId": storyId,
            "page": pageNumber,
            "audio_url": page.get("audio_url")
        }
    
    try:
        # Generate audio using Azure Speech Services
        language = story.get("language", "en")
        audio_bytes = TTSService.synthesize_text(text, language)
        
        # Save audio to disk
        audio_path = TTSService.save_audio(audio_bytes, storyId, pageNumber)
        
        # Update page with audio path
        page["audio_url"] = audio_path
        
        # Save updated story
        story["pages"] = pages
        StorageService.save_story(story)
        
        return {
            "message": "Audio generated successfully",
            "storyId": storyId,
            "page": pageNumber,
            "audio_url": audio_path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate audio: {str(e)}"
        )


@router.get("/{storyId}/audio/status")
async def get_audio_status(storyId: str):
    """
    Check audio generation status for a story
    
    Returns information about which audio files have been generated
    Useful for polling to know when all audio is ready
    """
    story = StorageService.get_story(storyId)
    
    if story is None:
        raise HTTPException(
            status_code=404,
            detail=f"Story with ID '{storyId}' not found"
        )
    
    pages = story.get("pages", [])
    total_pages = len(pages)
    generated_count = sum(1 for page in pages if page.get("audio_url") is not None)
    all_generated = generated_count == total_pages
    
    return {
        "storyId": storyId,
        "total_pages": total_pages,
        "generated_count": generated_count,
        "all_generated": all_generated,
        "pages": [
            {
                "page": page.get("page"),
                "audio_url": page.get("audio_url"),
                "has_audio": page.get("audio_url") is not None
            }
            for page in pages
        ]
    }

