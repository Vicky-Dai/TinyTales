"""
Storage service for saving and retrieving stories as JSON files
"""
import os
import json
import uuid
from datetime import datetime
from typing import Optional, Dict
from fastapi import HTTPException
from models.story import Story


class StorageService:
    """Service for JSON file-based story storage"""
    
    STORIES_DIR = "stories"
    
    @staticmethod
    def ensure_stories_dir():
        """Ensure stories directory exists"""
        os.makedirs(StorageService.STORIES_DIR, exist_ok=True)
    
    @staticmethod
    def generate_story_id() -> str:
        """Generate a unique story ID"""
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def save_story(story_data: Dict) -> str:
        """
        Save story to JSON file
        
        Args:
            story_data: Story data dictionary
        
        Returns:
            storyId
        """
        StorageService.ensure_stories_dir()
        
        # Generate story ID if not present
        story_id = story_data.get("storyId", StorageService.generate_story_id())
        story_data["storyId"] = story_id
        
        # Add timestamp if not present
        if "created_at" not in story_data:
            story_data["created_at"] = datetime.utcnow().isoformat()
        
        # Save to file
        file_path = os.path.join(StorageService.STORIES_DIR, f"{story_id}.json")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(story_data, f, indent=2, ensure_ascii=False)
            return story_id
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save story: {str(e)}"
            )
    
    @staticmethod
    def get_story(story_id: str) -> Optional[Dict]:
        """
        Retrieve story from JSON file
        
        Args:
            story_id: Story identifier
        
        Returns:
            Story data dictionary or None if not found
        """
        file_path = os.path.join(StorageService.STORIES_DIR, f"{story_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse story file: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read story: {str(e)}"
            )
    
    @staticmethod
    def story_exists(story_id: str) -> bool:
        """Check if story exists"""
        file_path = os.path.join(StorageService.STORIES_DIR, f"{story_id}.json")
        return os.path.exists(file_path)

