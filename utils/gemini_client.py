# utils/gemini_client.py
import google.generativeai as genai
from typing import List, Dict

class GeminiClient:
    def __init__(self, api_key: str):
        """Initialize the Gemini client with the API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.genres = ['fantasy', 'sci-fi', 'mystery', 'romance']
        self.instructions = {
            'starter': "Generate a 2-3 sentence story starter in the {genre} genre. Make it engaging and open-ended.",
            'custom_starter': "Generate a 2-3 sentence story starter based on this idea: {idea}",
            'next_part': """Given this story part:
{previous_part}

And this user choice:
{selected_option}

Generate the next part of the story (3-4 sentences). Make it engaging and end with a cliffhanger.""",
            'options': """Given this story part:
{story_part}

Generate 3 distinct options for how the story could continue. Each option should be 1 sentence long and lead to different story directions.""",
            'ending': """Given this story so far:
{story_parts}

Generate a satisfying ending to the story (3-4 sentences)."""
        }

    def generate_story_starters(self, genre: str) -> List[str]:
        """Generate 3 story starters for a given genre."""
        if genre not in self.genres:
            raise ValueError(f"Invalid genre. Choose from: {', '.join(self.genres)}")
        
        prompt = self.instructions['starter'].format(genre=genre)
        response = self.model.generate_content(prompt)
        return self._split_response(response.text, 3)

    def generate_custom_starter(self, idea: str) -> str:
        """Generate a story starter based on a custom idea."""
        prompt = self.instructions['custom_starter'].format(idea=idea)
        response = self.model.generate_content(prompt)
        return response.text

    def generate_next_story_part(self, previous_part: str, selected_option: str) -> str:
        """Generate the next part of the story based on the previous part and user choice."""
        prompt = self.instructions['next_part'].format(
            previous_part=previous_part,
            selected_option=selected_option
        )
        response = self.model.generate_content(prompt)
        return response.text

    def generate_options(self, story_part: str) -> List[str]:
        """Generate 3 options for continuing the story."""
        prompt = self.instructions['options'].format(story_part=story_part)
        response = self.model.generate_content(prompt)
        return self._split_response(response.text, 3)

    def generate_ending(self, story_parts: List[str]) -> str:
        """Generate a final ending for the story."""
        full_story = "\n".join(story_parts)
        prompt = self.instructions['ending'].format(story_parts=full_story)
        response = self.model.generate_content(prompt)
        return response.text

    def _split_response(self, text: str, count: int) -> List[str]:
        """Helper method to split response into multiple parts."""
        parts = text.split("\n")
        return [part.strip() for part in parts[:count] if part.strip()]
