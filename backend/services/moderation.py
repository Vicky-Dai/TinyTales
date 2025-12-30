"""
Moderation and safety service for StorySprout AI
Handles input validation and OpenAI Moderation API checks
"""
import os
from typing import Dict, List, Tuple, Optional
from openai import OpenAI
from fastapi import HTTPException

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


class ModerationService:
    """Service for content moderation and safety checks"""
    
    # Hard rules for story content
    FORBIDDEN_WORDS = [
        "violence", "weapon", "gun", "knife", "fight", "attack",
        "scary", "frightening", "terrifying", "horror", "monster",
        "death", "kill", "murder", "blood", "gore",
        "adult", "mature", "inappropriate"
    ]
    
    FORBIDDEN_THEMES = [
        "violence", "fear", "horror", "adult themes",
        "conflict", "danger", "threat"
    ]
    
    @staticmethod
    def validate_input(request_data: Dict) -> Tuple[bool, str]:
        """
        Validate story generation request input
        
        Returns:
            (is_valid, error_message)
        """
        # Check required fields
        required_fields = ["age_range", "moral", "characters", "setting"]
        for field in required_fields:
            if field not in request_data or not request_data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate age range format
        age_range = request_data.get("age_range", "")
        if not isinstance(age_range, str) or "-" not in age_range:
            return False, "age_range must be in format 'X-Y' (e.g., '4-7')"
        
        try:
            min_age, max_age = map(int, age_range.split("-"))
            if min_age < 0 or max_age > 12 or min_age >= max_age:
                return False, "age_range must be between 0-12 and min < max"
        except ValueError:
            return False, "age_range must be in format 'X-Y' with numbers"
        
        # Validate characters
        characters = request_data.get("characters", [])
        if not isinstance(characters, list) or len(characters) == 0:
            return False, "characters must be a non-empty list"
        
        # Validate pages
        pages = request_data.get("pages", 5)
        if not isinstance(pages, int) or pages < 3 or pages > 8:
            return False, "pages must be an integer between 3 and 8"
        
        # Check for forbidden words in input
        input_text = " ".join([
            request_data.get("moral", ""),
            request_data.get("setting", ""),
            " ".join(characters)
        ]).lower()
        
        for word in ModerationService.FORBIDDEN_WORDS:
            if word in input_text:
                return False, f"Input contains inappropriate content: '{word}'"
        
        return True, ""
    
    @staticmethod
    async def check_moderation(text: str) -> Tuple[bool, Dict]:
        """
        Check text using OpenAI Moderation API
        
        Returns:
            (is_safe, moderation_result)
        """
        client = get_openai_client()
        if not client or not os.getenv("OPENAI_API_KEY"):
            # If no API key, skip moderation (for development)
            return True, {"flagged": False, "categories": {}}
        
        try:
            response = client.moderations.create(input=text)
            result = response.results[0]
            
            if result.flagged:
                return False, {
                    "flagged": True,
                    "categories": result.categories.model_dump(),
                    "category_scores": result.category_scores.model_dump()
                }
            
            return True, {
                "flagged": False,
                "categories": result.categories.model_dump()
            }
        except Exception as e:
            error_str = str(e)
            # If rate limited or API error, skip moderation but log warning
            if "429" in error_str or "rate limit" in error_str.lower() or "Too Many Requests" in error_str:
                # Rate limit - allow request but log warning
                print(f"Warning: Moderation API rate limited, skipping check: {error_str}")
                return True, {"flagged": False, "categories": {}, "warning": "Moderation skipped due to rate limit"}
            elif "401" in error_str or "403" in error_str or "Invalid" in error_str:
                # API key issue - skip moderation
                print(f"Warning: Moderation API key issue, skipping check: {error_str}")
                return True, {"flagged": False, "categories": {}, "warning": "Moderation skipped due to API key issue"}
            else:
                # Other errors - skip moderation but log
                print(f"Warning: Moderation check failed, skipping: {error_str}")
                return True, {"flagged": False, "categories": {}, "warning": f"Moderation skipped: {error_str}"}
    
    @staticmethod
    def enforce_prompt_rules(prompt: str, age_range: str) -> str:
        """
        Enforce hard rules in prompts to ensure kid-safe content
        
        Args:
            prompt: Original prompt
            age_range: Target age range (e.g., "4-7")
        
        Returns:
            Enhanced prompt with safety rules
        """
        # Extract min age for vocabulary level
        try:
            min_age = int(age_range.split("-")[0])
        except:
            min_age = 4
        
        # Add safety prefixes
        safety_prefix = (
            "Create a kid-friendly, safe, warm children's book story. "
            f"Use simple vocabulary appropriate for ages {age_range}. "
            "No violence, fear, or adult themes. "
            "Keep the tone positive and educational. "
        )
        
        # Add vocabulary guidance
        if min_age <= 5:
            vocab_guidance = "Use very simple words (3-5 letters, common words). "
        elif min_age <= 7:
            vocab_guidance = "Use simple words (4-7 letters, common vocabulary). "
        else:
            vocab_guidance = "Use age-appropriate vocabulary. "
        
        return safety_prefix + vocab_guidance + prompt
    
    @staticmethod
    def validate_story_content(story_text: str) -> Tuple[bool, str]:
        """
        Validate generated story content for safety
        
        Returns:
            (is_safe, error_message)
        """
        story_lower = story_text.lower()
        
        # Check for forbidden words
        for word in ModerationService.FORBIDDEN_WORDS:
            if word in story_lower:
                return False, f"Story contains inappropriate word: '{word}'"
        
        return True, ""

