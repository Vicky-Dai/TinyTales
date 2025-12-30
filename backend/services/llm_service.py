"""
LLM service for story generation
Handles prompt engineering and OpenAI API calls
"""
import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from fastapi import HTTPException
from services.moderation import ModerationService

# Lazy initialization of OpenAI client
_client: Optional[OpenAI] = None

def get_openai_client() -> Optional[OpenAI]:
    """Get or create OpenAI client (lazy initialization)"""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            _client = OpenAI(api_key=api_key)
    return _client


class LLMService:
    """Service for generating stories using OpenAI LLM"""
    
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
        Generate a complete story using OpenAI LLM
        
        Args:
            request_data: Story generation request data
        
        Returns:
            Generated story dictionary
        """
        client = get_openai_client()
        if not client or not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured"
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
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for faster/cheaper generation
                messages=[
                    {
                        "role": "system",
                        "content": "You are a children's book author specializing in age-appropriate, educational stories. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
        except Exception as api_error:
            error_str = str(api_error)
            if "429" in error_str or "rate limit" in error_str.lower():
                raise HTTPException(
                    status_code=429,
                    detail="OpenAI API rate limit exceeded. Please try again in a few minutes."
                )
            elif "insufficient_quota" in error_str or "quota" in error_str.lower():
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI API quota exceeded. Please check your API key billing and add credits to your account."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"OpenAI API error: {str(api_error)}"
                )
        
        # Parse response (only reached if API call succeeded)
        try:
            content = response.choices[0].message.content.strip()
            
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
            for page in pages:
                if "text" not in page or "image_prompt" not in page:
                    raise HTTPException(
                        status_code=500,
                        detail="Story page missing required fields (text, image_prompt)"
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

