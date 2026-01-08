"""
Agentic service for intelligent story generation
Handles multi-step LLM reasoning to understand user intent and generate appropriate stories
"""
import os
import json
import logging
from typing import Dict, Optional, Tuple
from openai import OpenAI
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy initialization of OpenAI client
_client: Optional[OpenAI] = None

def get_openai_client() -> Optional[OpenAI]:
    """Get or create OpenAI client (lazy initialization)"""
    global _client
    if _client is None:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if endpoint and api_key:
            _client = OpenAI(
                base_url=endpoint,
                api_key=api_key
            )
    return _client


class AgenticService:
    """Service for agentic story generation with multi-step reasoning"""
    
    @staticmethod
    async def gate_analyze_prompt(user_prompt: str) -> Dict:
        """
        LLM Call 1: Gate - Analyze if user needs emotional support or just wants a story
        
        Args:
            user_prompt: Raw user input
            
        Returns:
            Dict with 'needs_support' (bool) and 'reason' (str)
        """
        client = get_openai_client()
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not client or not deployment_name:
            raise HTTPException(status_code=500, detail="OpenAI client not configured")
        
        gate_prompt = f"""Analyze this user message and determine if they need emotional support or just want a story.

User message: "{user_prompt}"

Look for signs of:
- Sadness, depression, anxiety, stress
- Loneliness or feeling down
- Difficult emotions or situations
- Need for comfort or cheering up"""

        try:
            logger.info("[GATE] LLM Call 1: Analyzing user intent...")
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an empathetic AI assistant that can detect when someone needs emotional support."
                    },
                    {
                        "role": "user",
                        "content": gate_prompt
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "gate_analysis",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "needs_support": {
                                    "type": "boolean",
                                    "description": "Whether the user needs emotional support"
                                },
                                "reason": {
                                    "type": "string",
                                    "description": "Brief explanation of the analysis"
                                }
                            },
                            "required": ["needs_support", "reason"],
                            "additionalProperties": False
                        }
                    }
                },
                max_completion_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            logger.info(f"[GATE] Result: needs_support={result.get('needs_support')}, reason={result.get('reason')}")
            return result
            
        except Exception as e:
            logger.error(f"[GATE] Error: {str(e)}")
            # Default to no support needed on error
            return {"needs_support": False, "reason": "Error in analysis"}
    
    @staticmethod
    async def extract_story_parameters(user_prompt: str, needs_support: bool) -> Dict:
        """
        LLM Call 2: Extract story parameters from prompt, adjust for emotional support if needed
        
        Args:
            user_prompt: Raw user input
            needs_support: Whether user needs emotional support
            
        Returns:
            Dict with story parameters (age_range, moral, characters, setting, tone, pages)
        """
        client = get_openai_client()
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not client or not deployment_name:
            raise HTTPException(status_code=500, detail="OpenAI client not configured")
        
        if needs_support:
            extraction_prompt = f"""The user is going through a difficult time. Extract story parameters from their message and adjust the moral and tone to be uplifting and supportive.

User message: "{user_prompt}"

Create a story that will cheer them up with:
- An uplifting, encouraging moral (focus on hope, strength, friendship, overcoming challenges)
- A warm, gentle, comforting tone
- Positive, relatable characters
- A beautiful, peaceful setting

IMPORTANT: age_range must be one of: "4-7", "6-9", or "8-12" (children's story format).
If user mentions adults or other ages, map to the most appropriate children's range.

Extract or create parameters. If any parameter is missing, use sensible defaults."""
        else:
            extraction_prompt = f"""Extract story parameters from this user request.

User message: "{user_prompt}"

IMPORTANT: age_range must be one of: "4-7", "6-9", or "8-12" (children's story format).
If user mentions adults, teens, or other ages, automatically map to the most appropriate children's range:
- Adults/complex topics → "8-12" (older children)
- General/unknown → "6-9" (middle range)
- Toddlers/simple → "4-7" (younger children)

Adapt the story content, vocabulary, and complexity to match the selected children's age range.
If any parameter is missing, use sensible defaults."""

        try:
            logger.info(f"[EXTRACT] LLM Call 2: Extracting parameters (support_mode={needs_support})...")
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts story parameters. Always map age ranges to valid children's ranges: 4-7, 6-9, or 8-12."
                    },
                    {
                        "role": "user",
                        "content": extraction_prompt
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "story_parameters",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "age_range": {
                                    "type": "string",
                                    "description": "Age range for the story. Must be one of: '4-7', '6-9', or '8-12'"
                                },
                                "moral": {
                                    "type": "string",
                                    "description": "The moral or lesson of the story"
                                },
                                "characters": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of character names"
                                },
                                "setting": {
                                    "type": "string",
                                    "description": "Story setting or location"
                                },
                                "tone": {
                                    "type": "string",
                                    "description": "Story tone (e.g., warm, playful, gentle)"
                                },
                                "pages": {
                                    "type": "integer",
                                    "description": "Number of pages (3-8)"
                                },
                                "language": {
                                    "type": "string",
                                    "description": "Language code (default: 'en')"
                                }
                            },
                            "required": ["age_range", "moral", "characters", "setting", "tone", "pages", "language"],
                            "additionalProperties": False
                        }
                    }
                },
                max_completion_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            params = json.loads(content)
            logger.info(f"[EXTRACT] Extracted: {params}")
            
            return params
            
        except Exception as e:
            logger.error(f"[EXTRACT] Error: {str(e)}")
            # Return safe defaults
            return {
                "age_range": "6-9",
                "moral": "Be kind to others",
                "characters": ["Hero", "Friend"],
                "setting": "A magical place",
                "tone": "warm",
                "pages": 5,
                "language": "en"
            }
    
    @staticmethod
    async def generate_clarification_question(user_prompt: str, validation_error: str) -> str:
        """
        LLM Call: Generate a clarifying question when user input is unclear or invalid
        
        Args:
            user_prompt: Original user input
            validation_error: The validation error message
            
        Returns:
            A friendly clarifying question to ask the user
        """
        client = get_openai_client()
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not client or not deployment_name:
            return "Could you please provide more details about the story you'd like me to create?"
        
        clarification_prompt = f"""The user's request needs clarification.

User's original request: "{user_prompt}"
Issue: {validation_error}

Generate a friendly, helpful question to ask the user to clarify their request. Keep it conversational and specific to their issue."""

        try:
            logger.info("[CLARIFY] Generating clarification question...")
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that asks clarifying questions when user requests are unclear."
                    },
                    {
                        "role": "user",
                        "content": clarification_prompt
                    }
                ],
                max_completion_tokens=200
            )
            
            question = response.choices[0].message.content.strip()
            logger.info(f"[CLARIFY] Generated question: {question}")
            return question
            
        except Exception as e:
            logger.error(f"[CLARIFY] Error: {str(e)}")
            return f"I need some clarification: {validation_error}. Could you provide more details?"
