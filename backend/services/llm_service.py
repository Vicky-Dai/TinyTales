"""
LLM service for story generation
Handles prompt engineering and Azure OpenAI API calls
"""
import os
import json
import logging
from typing import Dict, List, Optional
from openai import OpenAI
from fastapi import HTTPException
from services.moderation import ModerationService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy initialization of OpenAI client
_client: Optional[OpenAI] = None

def get_azure_openai_client() -> Optional[OpenAI]:
    """Get or create Azure OpenAI client (lazy initialization)"""
    global _client
    if _client is None:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        logger.info(f"Initializing Azure OpenAI client:")
        logger.info(f"  Endpoint: {endpoint}")
        logger.info(f"  API Key configured: {'Yes' if api_key else 'No'}")
        
        if endpoint and api_key:
            _client = OpenAI(
                base_url=endpoint,
                api_key=api_key
            )
            logger.info("Azure OpenAI client initialized successfully")
        else:
            logger.error("Azure OpenAI client initialization failed - missing endpoint or API key")
    return _client


class LLMService:
    """Service for generating stories using Azure OpenAI LLM"""
    
    @staticmethod
    def build_story_prompt(request_data: Dict) -> str:
        """
        Build structured prompt for story generation
        
        Args:
            request_data: Story generation request data
        
        Returns:
            Formatted prompt string
        """
        age_range = request_data.get("age_range", "4-7")
        moral = request_data.get("moral", "")
        characters = ", ".join(request_data.get("characters", []))
        setting = request_data.get("setting", "")
        tone = request_data.get("tone", "warm")
        pages = request_data.get("pages", 5)
        
        # Extract min age for vocabulary guidance
        try:
            min_age = int(age_range.split("-")[0])
        except:
            min_age = 4
        
        # Build vocabulary guidance
        if min_age <= 5:
            vocab = "very simple words (3-5 letters, common words like 'cat', 'dog', 'happy')"
        elif min_age <= 7:
            vocab = "simple words (4-7 letters, common vocabulary like 'friend', 'together', 'beautiful')"
        else:
            vocab = "age-appropriate vocabulary suitable for children"
        
        prompt = f"""Create a {pages}-page children's story with the following requirements:

**Target Audience:** Ages {age_range}
**Vocabulary Level:** Use {vocab}
**Moral/Lesson:** {moral}
**Characters:** {characters}
**Setting:** {setting}
**Tone:** {tone}

**Story Requirements:**
1. Each page should have 2-3 sentences of simple, engaging text
2. The story should teach the moral "{moral}" naturally
3. Use positive, warm language throughout
4. No violence, fear, or scary elements
5. Age-appropriate content only
6. Engaging and fun for children

**Output Format (JSON):**
{{
  "title": "Story Title",
  "pages": [
    {{
      "page": 1,
      "text": "First page text here...",
      "image_prompt": "Detailed image description for children's book illustration, kid-friendly, safe, warm style"
    }},
    {{
      "page": 2,
      "text": "Second page text here...",
      "image_prompt": "Detailed image description for children's book illustration, kid-friendly, safe, warm style"
    }}
    // ... continue for all {pages} pages
  ]
}}

Generate the complete story now. Return ONLY valid JSON, no additional text."""
        
        # Apply safety rules
        return ModerationService.enforce_prompt_rules(prompt, age_range)
    
    @staticmethod
    async def generate_story(request_data: Dict) -> Dict:
        """
        Generate a complete story using Azure OpenAI LLM
        
        Args:
            request_data: Story generation request data
        
        Returns:
            Generated story dictionary
        """
        client = get_azure_openai_client()
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not client:
            raise HTTPException(
                status_code=500,
                detail="Azure OpenAI client not configured. Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables."
            )
        
        if not deployment_name:
            raise HTTPException(
                status_code=500,
                detail="AZURE_OPENAI_DEPLOYMENT_NAME not configured. Please set the deployment name environment variable."
            )
        
        # Build prompt
        prompt = LLMService.build_story_prompt(request_data)
        
        # Check moderation on the prompt itself
        is_safe, moderation_result = await ModerationService.check_moderation(prompt)
        if not is_safe:
            raise HTTPException(
                status_code=400,
                detail="Story request failed moderation check",
                headers={"X-Moderation-Result": json.dumps(moderation_result)}
            )
        
        try:
            # Call Azure OpenAI API
            # Note: In Azure OpenAI, we use the deployment name instead of model name
            logger.info(f"Making Azure OpenAI API call:")
            logger.info(f"  Deployment: {deployment_name}")
            logger.info(f"  Max completion tokens: 4000")
            
            response = client.chat.completions.create(
                model=deployment_name,  # Azure OpenAI uses deployment name
                messages=[
                    {
                        "role": "system",
                        "content": "You are a children's book author specializing in age-appropriate, educational stories."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "story_response",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "The story title"
                                },
                                "pages": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "page": {
                                                "type": "integer",
                                                "description": "Page number"
                                            },
                                            "text": {
                                                "type": "string",
                                                "description": "The story text for this page"
                                            },
                                            "image_prompt": {
                                                "type": "string",
                                                "description": "Detailed image description for illustration"
                                            }
                                        },
                                        "required": ["page", "text", "image_prompt"],
                                        "additionalProperties": False
                                    },
                                    "description": "Array of story pages"
                                }
                            },
                            "required": ["title", "pages"],
                            "additionalProperties": False
                        }
                    }
                },
                max_completion_tokens=4000
            )
            logger.info("Azure OpenAI API call successful")
        except Exception as api_error:
            logger.error(f"Azure OpenAI API error: {str(api_error)}")
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
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Azure OpenAI API error: {str(api_error)}"
                )
        
        # Parse response (only reached if API call succeeded)
        try:
            content = response.choices[0].message.content
            logger.info(f"Raw API response content: {content[:500] if content else 'NONE/EMPTY'}")
            
            if not content:
                raise HTTPException(
                    status_code=500,
                    detail="Model returned empty response. This may indicate the model hit a token limit or content filter."
                )
            
            content = content.strip()
            
            # Clean JSON (remove markdown code blocks if present)
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            try:
                story_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error. Content length: {len(content)}, Content: {content[:500]}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse story JSON: {str(e)}. Response: {content[:200]}"
                )
            
            # Validate story structure
            if "title" not in story_data or "pages" not in story_data:
                raise HTTPException(
                    status_code=500,
                    detail="Generated story missing required fields (title, pages)"
                )
            
            # Validate and check each page
            pages = story_data.get("pages", [])
            if len(pages) != request_data.get("pages", 5):
                raise HTTPException(
                    status_code=500,
                    detail=f"Story has {len(pages)} pages, expected {request_data.get('pages', 5)}"
                )
            
            # Validate each page content
            for i, page in enumerate(pages):
                logger.info(f"Validating page {i+1}: {page}")
                if "text" not in page or "image_prompt" not in page:
                    logger.error(f"Page {i+1} structure: {list(page.keys())}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Story page {i+1} missing required fields (text, image_prompt). Found fields: {list(page.keys())}"
                    )
                
                # Check page text for safety
                is_safe, error_msg = ModerationService.validate_story_content(page["text"])
                if not is_safe:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Story page {page.get('page', 'unknown')} failed safety check: {error_msg}"
                    )
                
                # Ensure image prompts are kid-safe
                if not page["image_prompt"].startswith(("kid-friendly", "children's book", "safe", "warm")):
                    page["image_prompt"] = f"kid-friendly, safe, warm children's book illustration, {page['image_prompt']}"
            
            if story_data is None:
                raise HTTPException(
                    status_code=500,
                    detail="Story generation returned None. This should not happen."
                )
            return story_data
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Story generation failed: {str(e)}"
            )

