import json
import os
from datetime import datetime

class StoryStorage:
    """Handles the storage and retrieval of stories."""
    
    def __init__(self):
        """Initialize the story storage."""
        # Create a stories directory if it doesn't exist
        os.makedirs('stories', exist_ok=True)
    
    def save_story(self, story_data):
        """Save a story to storage.
        
        Args:
            story_data (dict): The story data to save.
            
        Returns:
            str: The ID of the saved story.
        """
        # Generate a unique ID for the story
        story_id = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Add the ID to the story data
        story_data['id'] = story_id
        
        # Add a timestamp to the story data
        story_data['timestamp'] = datetime.now().isoformat()
        
        # Save the story to a JSON file
        with open(f'stories/{story_id}.json', 'w') as f:
            json.dump(story_data, f, indent=2)
        
        return story_id
    
    def get_story(self, story_id):
        """Get a story from storage.
        
        Args:
            story_id (str): The ID of the story to retrieve.
            
        Returns:
            dict: The story data, or None if the story doesn't exist.
        """
        try:
            with open(f'stories/{story_id}.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def get_all_stories(self):
        """Get all stories from storage.
        
        Returns:
            list: A list of story data dictionaries.
        """
        stories = []
        
        # Get all JSON files in the stories directory
        for filename in os.listdir('stories'):
            if filename.endswith('.json'):
                try:
                    with open(f'stories/{filename}', 'r') as f:
                        story_data = json.load(f)
                        stories.append(story_data)
                except Exception as e:
                    print(f"Error loading story {filename}: {e}")
        
        # Sort stories by timestamp (newest first)
        stories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return stories
    
    def delete_story(self, story_id):
        """Delete a story from storage.
        
        Args:
            story_id (str): The ID of the story to delete.
            
        Returns:
            bool: True if the story was deleted, False otherwise.
        """
        try:
            os.remove(f'stories/{story_id}.json')
            return True
        except FileNotFoundError:
            return False
