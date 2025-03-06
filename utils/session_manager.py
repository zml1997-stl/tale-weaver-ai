# utils/session_manager.py
from typing import Dict, List
import uuid
import json
import os

class SessionManager:
    def __init__(self):
        self.storage_path = "user_stories"
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def update_story(self, session: Dict, new_part: str) -> None:
        """Update the current story in session with a new part."""
        if 'current_story' not in session:
            raise ValueError("No active story in session")
        
        session['current_story']['story_parts'].append(new_part)
        session.modified = True

    def save_story(self, session: Dict, ending: str) -> Dict:
        """Save the complete story with its ending."""
        if 'current_story' not in session:
            raise ValueError("No active story in session")
        
        story_data = {
            'id': str(uuid.uuid4()),
            'starters': session['current_story']['starters'],
            'story_parts': session['current_story']['story_parts'],
            'ending': ending,
            'full_story': "\n".join(session['current_story']['story_parts'] + [ending])
        }
        
        # Save story to file
        self._save_to_file(story_data)
        
        # Clear current story from session
        session.pop('current_story', None)
        
        return story_data

    def load_story(self, story_id: str) -> Dict:
        """Load a previously saved story."""
        file_path = os.path.join(self.storage_path, f"{story_id}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Story {story_id} not found")
        
        with open(file_path, 'r') as f:
            return json.load(f)

    def _save_to_file(self, story_data: Dict) -> None:
        """Save story data to a JSON file."""
        file_path = os.path.join(self.storage_path, f"{story_data['id']}.json")
        with open(file_path, 'w') as f:
            json.dump(story_data, f, indent=2)
