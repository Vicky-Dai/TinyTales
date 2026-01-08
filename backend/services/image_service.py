"""
Image generation service using Azure OpenAI with FLUX model
Handles image generation for story pages
"""
import os
import base64
from typing import Optional, Tuple
from openai import OpenAI
from fastapi import HTTPException

# Lazy initialization of Azure OpenAI client
_image_client: Optional[OpenAI] = None

def get_azure_openai_image_client() -> Optional[OpenAI]:
    """Get or create Azure OpenAI client for image generation (lazy initialization)"""
    global _image_client
    if _image_client is None:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if endpoint and api_key:
            _image_client = OpenAI(
                base_url=endpoint,
                api_key=api_key
            )
    return _image_client


class ImageService:
    """Service for generating images using Azure OpenAI FLUX model"""
    
    @staticmethod
    async def generate_image(image_prompt: str, size: str = "1024x1024") -> Tuple[bytes, str]:
        """
        Generate an image using Azure OpenAI FLUX model
        
        Args:
            image_prompt: Text prompt describing the image to generate
            size: Image size (default: "1024x1024")
        
        Returns:
            Tuple of (image_bytes, "base64") - second value is placeholder for compatibility
        
        Raises:
            HTTPException: If image generation fails
        """
        client = get_azure_openai_image_client()
        # Get FLUX deployment name from env (defaults to 'FLUX.1-Kontext-pro')
        deployment_name = os.getenv("AZURE_OPENAI_IMAGE_DEPLOYMENT_NAME", "FLUX.1-Kontext-pro")
        
        if not client:
            raise HTTPException(
                status_code=500,
                detail="Azure OpenAI client not configured. Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables."
            )
        
        try:
            # Generate image using FLUX model
            response = client.images.generate(
                model=deployment_name,
                prompt=image_prompt,
                n=1,
                size=size
            )
            
            # Decode base64 image data
            image_bytes = base64.b64decode(response.data[0].b64_json)
            
            return image_bytes, "base64"
            
        except Exception as api_error:
            error_str = str(api_error)
            print(f"Image generation error details: {error_str}")  # Add detailed logging
            if "429" in error_str or "rate limit" in error_str.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Azure OpenAI API rate limit exceeded. Please try again in a few minutes."
                )
            elif "insufficient_quota" in error_str or "quota" in error_str.lower():
                raise HTTPException(
                    status_code=402,
                    detail="Azure OpenAI quota exceeded. Please check your Azure account billing and add credits."
                )
            elif "401" in error_str or "403" in error_str or "unauthorized" in error_str.lower():
                raise HTTPException(
                    status_code=401,
                    detail="Azure OpenAI authentication failed. Please check your AZURE_OPENAI_API_KEY and endpoint configuration."
                )
            elif "content_policy_violation" in error_str.lower() or "safety" in error_str.lower():
                raise HTTPException(
                    status_code=400,
                    detail="Image generation failed content safety check. Please use kid-friendly prompts."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Azure OpenAI image generation error: {str(api_error)}"
                )
    
    @staticmethod
    def save_image(image_bytes: bytes, story_id: str, page_number: int) -> str:
        """
        Save image bytes to disk
        
        Args:
            image_bytes: Image data as bytes
            story_id: Story identifier
            page_number: Page number (1-indexed)
        
        Returns:
            Relative path to the saved image file
        """
        # Create images directory structure: stories/images/{story_id}/
        images_dir = os.path.join("stories", "images", story_id)
        os.makedirs(images_dir, exist_ok=True)
        
        # Save image as PNG
        image_filename = f"{page_number}.png"
        image_path = os.path.join(images_dir, image_filename)
        
        try:
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            return os.path.join("images", story_id, image_filename)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save image: {str(e)}"
            )

