import google.generativeai as genai
from config import Config

class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini client with API key from config."""
        self.api_key = Config.GEMINI_API_KEY
        self.model = Config.GEMINI_MODEL
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Get the generative model
        self.model_instance = genai.GenerativeModel(self.model)
    
    def generate_story_starters(self, genre):
        """Generate three story starters for a given genre.
        
        Args:
            genre (str): The genre for the story starters.
            
        Returns:
            list: A list of three story starters.
        """
        prompt = f"""
        Generate three unique and engaging story starters (2-3 sentences each) for a {genre} story.
        Each starter should set up an interesting scenario that could lead to an interactive story.
        Format the output as a Python list of three strings, with no additional text or explanation.
        """
        
        response = self.model_instance.generate_content(prompt)
        
        # Parse the response to extract the three starters
        try:
            content = response.text
            # Clean up the response to extract just the list
            content = content.strip()
            if content.startswith("```python"):
                content = content.split("```python")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].strip()
                
            # Safe evaluation of the list
            starters = eval(content)
            
            # Ensure we have exactly three starters
            if not isinstance(starters, list) or len(starters) != 3:
                starters = [
                    f"In a world of {genre}, an unexpected adventure begins...",
                    f"The {genre} tale unfolds with a surprising twist...",
                    f"A {genre} story starts with an unusual discovery..."
                ]
            
            return starters
        except Exception as e:
            print(f"Error parsing story starters: {e}")
            # Fallback starters
            return [
                f"In a world of {genre}, an unexpected adventure begins...",
                f"The {genre} tale unfolds with a surprising twist...",
                f"A {genre} story starts with an unusual discovery..."
            ]
    
    def generate_story_from_custom_idea(self, idea):
        """Generate a story starter from a custom user idea.
        
        Args:
            idea (str): The user's custom story idea.
            
        Returns:
            str: A story starter based on the user's idea.
        """
        prompt = f"""
        Generate an engaging opening paragraph (2-3 sentences) for a story based on this idea: "{idea}".
        The paragraph should set up the scenario in an interesting way that can lead to an interactive story.
        Provide only the paragraph with no additional text or explanation.
        """
        
        response = self.model_instance.generate_content(prompt)
        
        # Return the generated starter
        try:
            return response.text.strip()
        except Exception as e:
            print(f"Error generating story from custom idea: {e}")
            return f"A story begins with {idea}..."
    
    def generate_story_options(self, story_so_far):
        """Generate three options for continuing the story.
        
        Args:
            story_so_far (str): The story content up to this point.
            
        Returns:
            list: A list of three options for continuing the story.
        """
        prompt = f"""
        Here's a story in progress:
        
        {story_so_far}
        
        Generate three distinct and interesting options for what could happen next in this story.
        Each option should be a brief phrase (5-10 words) that presents a clear direction.
        Format the output as a Python list of three strings, with no additional text or explanation.
        """
        
        response = self.model_instance.generate_content(prompt)
        
        # Parse the response to extract the three options
        try:
            content = response.text
            # Clean up the response to extract just the list
            content = content.strip()
            if content.startswith("```python"):
                content = content.split("```python")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].strip()
                
            # Safe evaluation of the list
            options = eval(content)
            
            # Ensure we have exactly three options
            if not isinstance(options, list) or len(options) != 3:
                options = [
                    "Continue the adventure",
                    "Take an unexpected turn",
                    "Face a new challenge"
                ]
            
            return options
        except Exception as e:
            print(f"Error parsing story options: {e}")
            # Fallback options
            return [
                "Continue the adventure",
                "Take an unexpected turn",
                "Face a new challenge"
            ]
    
    def continue_story(self, story_so_far, selected_option):
        """Generate the next part of the story based on the selected option.
        
        Args:
            story_so_far (str): The story content up to this point.
            selected_option (str): The option selected by the user.
            
        Returns:
            str: The next part of the story.
        """
        prompt = f"""
        Here's a story in progress:
        
        {story_so_far}
        
        The reader has chosen to: "{selected_option}"
        
        Continue the story with a new paragraph (3-5 sentences) based on this choice.
        Make it engaging and leave room for further choices.
        Provide only the new paragraph with no additional text or explanation.
        """
        
        response = self.model_instance.generate_content(prompt)
        
        # Return the generated continuation
        try:
            return response.text.strip()
        except Exception as e:
            print(f"Error continuing story: {e}")
            return f"The story continues as {selected_option}..."
    
    def generate_story_ending(self, story_so_far):
        """Generate a satisfying ending for the story.
        
        Args:
            story_so_far (str): The story content up to this point.
            
        Returns:
            str: The ending of the story.
        """
        prompt = f"""
        Here's a story that needs an ending:
        
        {story_so_far}
        
        Generate a satisfying conclusion (2-4 sentences) that wraps up the story.
        Provide only the ending paragraph with no additional text or explanation.
        """
        
        response = self.model_instance.generate_content(prompt)
        
        # Return the generated ending
        try:
            return response.text.strip()
        except Exception as e:
            print(f"Error generating story ending: {e}")
            return "And thus, the story came to its conclusion."