from utils.gemini_client import GeminiClient
from config import Config

class StoryGenerator:
    """Handles the story generation logic."""
    
    def __init__(self):
        """Initialize the story generator with a Gemini client."""
        self.gemini_client = GeminiClient()
        self.max_story_parts = Config.MAX_STORY_PARTS
    
    def get_story_starters(self, genre):
        """Get three story starters for a given genre.
        
        Args:
            genre (str): The genre for the story starters.
            
        Returns:
            list: A list of three story starters.
        """
        return self.gemini_client.generate_story_starters(genre)
    
    def get_story_from_idea(self, idea):
        """Get a story starter from a custom user idea.
        
        Args:
            idea (str): The user's custom story idea.
            
        Returns:
            str: A story starter based on the user's idea.
        """
        return self.gemini_client.generate_story_from_custom_idea(idea)
    
    def get_story_options(self, story_so_far):
        """Get three options for continuing the story.
        
        Args:
            story_so_far (str): The story content up to this point.
            
        Returns:
            list: A list of three options for continuing the story.
        """
        return self.gemini_client.generate_story_options(story_so_far)
    
    def continue_story(self, story_so_far, selected_option):
        """Get the next part of the story based on the selected option.
        
        Args:
            story_so_far (str): The story content up to this point.
            selected_option (str): The option selected by the user.
            
        Returns:
            str: The next part of the story.
        """
        return self.gemini_client.continue_story(story_so_far, selected_option)
    
    def get_story_ending(self, story_so_far):
        """Get a satisfying ending for the story.
        
        Args:
            story_so_far (str): The story content up to this point.
            
        Returns:
            str: The ending of the story.
        """
        return self.gemini_client.generate_story_ending(story_so_far)
    
    def is_story_too_long(self, story_parts):
        """Check if the story has reached the maximum number of parts.
        
        Args:
            story_parts (list): The list of story parts.
            
        Returns:
            bool: True if the story has reached the maximum number of parts, False otherwise.
        """
        return len(story_parts) >= self.max_story_parts
