"""
Image generation service using Azure OpenAI DALL-E
Handles image generation for story pages
"""
import os
import httpx
from typing import Optional, Tuple
from openai import AzureOpenAI
from fastapi import HTTPException

# Lazy initialization of Azure OpenAI client
_image_client: Optional[AzureOpenAI] = None

def get_azure_openai_image_client() -> Optional[AzureOpenAI]:
    """Get or create Azure OpenAI client for image generation (lazy initialization)"""
    global _image_client
    if _image_client is None:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if endpoint and api_key:
            _image_client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
    return _image_client


class ImageService:
    """Service for generating images using Azure OpenAI DALL-E"""
    
    @staticmethod
    async def generate_image(image_prompt: str, size: str = "1024x1024") -> Tuple[bytes, str]:
        """
        Generate an image using Azure OpenAI DALL-E
        
        Args:
            image_prompt: Text prompt describing the image to generate
            size: Image size (1024x1024, 1792x1024, or 1024x1792 for DALL-E 3)
        
        Returns:
            Tuple of (image_bytes, image_url) where image_url is the temporary URL from Azure
        
        Raises:
            HTTPException: If image generation fails
        """
        client = get_azure_openai_image_client()
        # Get DALL-E deployment name (defaults to 'dall-e-3' if not set)
        # Uses the same endpoint as text generation, but needs DALL-E deployment name
        deployment_name = os.getenv("AZURE_OPENAI_DALL_E_DEPLOYMENT_NAME", "dall-e-3")
        
        if not client:
            raise HTTPException(
                status_code=500,
                detail="Azure OpenAI client not configured. Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables."
            )
        
        try:
            # Use DALL-E 3 model (or DALL-E 2 if specified)
            model = "dall-e-3"  # Default to DALL-E 3
            dall_e_model = os.getenv("AZURE_OPENAI_DALL_E_MODEL", "dall-e-3")
            if dall_e_model in ["dall-e-2", "dall-e-3"]:
                model = dall_e_model
            
            # Validate size based on model
            if model == "dall-e-3":
                valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
                if size not in valid_sizes:
                    size = "1024x1024"  # Default for DALL-E 3
            else:  # DALL-E 2
                valid_sizes = ["256x256", "512x512", "1024x1024"]
                if size not in valid_sizes:
                    size = "1024x1024"  # Default for DALL-E 2
            
            # Generate image using Azure OpenAI
            if model == "dall-e-3":
                response = client.images.generate(
                    model=deployment_name,  # Azure OpenAI uses deployment name
                    prompt=image_prompt,
                    size=size,
                    n=1,
                    quality="standard",
                    style="vivid"
                )
            else:  # DALL-E 2
                response = client.images.generate(
                    model=deployment_name,  # Azure OpenAI uses deployment name
                    prompt=image_prompt,
                    size=size,
                    n=1
                )
            
            # Get image URL from response
            image_url = response.data[0].url
            
            # Download the image
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                image_response = await http_client.get(image_url)
                image_response.raise_for_status()
                image_bytes = image_response.content
            
            return image_bytes, image_url
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download generated image: {str(e)}"
            )
        except Exception as api_error:
            error_str = str(api_error)
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

