from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import uuid
import time
from datetime import datetime
import re
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
from pydub import AudioSegment
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Ensure required folders exist
os.makedirs("saved_stories", exist_ok=True)
os.makedirs("audio_files", exist_ok=True)

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Helper functions for text-to-speech
def change_speed(sound, speed=1.15):
    """Adjusts the speed of an audio file."""
    return sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    }).set_frame_rate(sound.frame_rate)

def generate_audio_file(text):
    """Generates audio from text and returns the file path"""
    if not text:
        return None
    
    try:
        # Clean text for TTS (remove HTML tags and special markers)
        clean_text = re.sub(r'<[^>]*>', '', text)
        
        # Generate a unique filename
        filename = f"audio_{uuid.uuid4()}.mp3"
        file_path = os.path.join("audio_files", filename)
        
        # Generate the audio file
        tts = gTTS(text=clean_text, lang='en', slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        
        # Load the generated audio and change the speed
        audio = AudioSegment.from_file(temp_file.name)
        faster_audio = change_speed(audio, speed=1.15)
        faster_audio.export(file_path, format="mp3")
        
        # Remove temp file
        os.unlink(temp_file.name)
        
        return file_path
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        return None

def clean_story_text(text):
    """Clean story text by removing embedded AI choices and formatting artifacts"""
    # Remove patterns like "Option A: ...", "1. ...", "Choice: ..." etc.
    patterns = [
        r'(?:Option|Choice)\s+[A-Za-z0-9]+\s*:\s*.*?(?=(?:Option|Choice)|$)',
        r'\d+\.\s+.*?(?=\d+\.|$)',
        r'•\s+.*?(?=•|$)'
    ]
    
    cleaned_text = text
    for pattern in patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL)
    
    # Remove any remaining numbered list markers
    cleaned_text = re.sub(r'^\s*\d+\.\s+', '', cleaned_text, flags=re.MULTILINE)
    
    # Remove any "What will you do?" or similar prompts
    prompts_to_remove = [
        r'What will you do\?',
        r'What do you do next\?',
        r'What happens next\?',
        r'What choice will you make\?',
        r'Choose your next action.',
        r'What would you like to do\?'
    ]
    
    for prompt in prompts_to_remove:
        cleaned_text = re.sub(prompt, '', cleaned_text)
    
    return cleaned_text.strip()

def generate_with_gemini(prompt, temperature=0.7, max_retries=3, retry_delay=2):
    """Generate content using Gemini API with error handling and retries"""
    attempt = 0
    while attempt < max_retries:
        try:
            # Add more detailed logging
            logger.info(f"Attempting to generate content. Attempt {attempt + 1}")
            logger.debug(f"Prompt: {prompt}")
            
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            
            # Log successful generation
            logger.info("Content generation successful")
            return response.text
        except Exception as e:
            attempt += 1
            logger.error(f"API call attempt {attempt} failed: {str(e)}")
            
            # More specific error logging
            if hasattr(e, 'response'):
                logger.error(f"Full error response: {e.response}")
            
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to generate content after {max_retries} attempts: {str(e)}")
                return "Once upon a time, there was an error in the storytelling machine..."

def safe_json_parse(text):
    """Parse JSON safely with multiple fallback methods"""
    logger.debug("Attempting to parse JSON response")
    
    # First try direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.debug("Direct JSON parsing failed, trying alternative methods")
    
    # Try to find JSON array in the text using regex
    json_match = re.search(r'\[\s*".*"\s*\]', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            logger.debug("JSON array extraction failed")
    
    # Try to extract items with quotes
    items = re.findall(r'"([^"]*)"', text)
    if items and len(items) > 0:
        logger.debug(f"Extracted {len(items)} quoted items")
        return items
    
    # Fallback: split by newlines, numbers or bullets
    logger.debug("Using fallback text splitting method")
    fallback_items = re.split(r'\n\s*(?:\d+\.|\*)\s*', text)
    fallback_items = [s.strip() for s in fallback_items if s.strip()]
    return fallback_items

# API Routes
@app.route('/')
def index():
    """Serve the static index.html file"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/generate-starters', methods=['POST'])
def api_generate_starters():
    """Generate story starters based on genre and character information"""
    data = request.json
    genre = data.get('genre', '')
    character_name = data.get('character_name', '')
    character_trait = data.get('character_trait', '')
    
    try:
        prompt = """
        Generate 3 unique and engaging story starters for an interactive fiction game. 
        Each starter should be 3-4 sentences long and end with an intriguing situation 
        that sets up a choice, but DO NOT include the choices in the starter.
        """
        
        if genre:
            prompt += f" The genre is {genre}."
        
        if character_name:
            prompt += f" The main character's name is {character_name}."
        
        if character_trait:
            prompt += f" The character's defining trait is being {character_trait}."
        
        prompt += """
        Make each starter distinct and compelling. Format the response as a JSON array 
        with each starter as a string element. Example format: 
        ["Starter 1...", "Starter 2...", "Starter 3..."]
        
        DO NOT include any choices or options in the starters themselves.
        """
        
        response = generate_with_gemini(prompt)
        starters = safe_json_parse(response)
        
        # Ensure we only return 3 starters
        if len(starters) > 3:
            starters = starters[:3]
        
        # If we got fewer than 3 starters, add some generic ones
        while len(starters) < 3:
            starters.append(f"You find yourself in an unexpected situation that will test your {character_trait} nature.")
        
        return jsonify({"starters": starters})
    except Exception as e:
        logger.error(f"Error generating starters: {str(e)}")
        return jsonify({
            "error": "Failed to generate story starters",
            "starters": [
                "You find yourself standing at the edge of a mysterious forest with a map that seems to lead to a hidden treasure.",
                "The spaceship's alarm blares as you wake up from cryosleep, the rest of the crew is missing.",
                "The old mansion you just inherited contains a locked room that nobody has entered for over a century."
            ]
        }), 200  # Return 200 with fallback data

@app.route('/api/generate-choices', methods=['POST'])
def api_generate_choices():
    """Generate choices for the user based on the current story"""
    data = request.json
    story_so_far = data.get('story_so_far', '')
    genre = data.get('genre', '')
    character_name = data.get('character_name', '')
    character_trait = data.get('character_trait', '')
    num_choices = data.get('num_choices', 3)
    
    try:
        # Clean the story text to remove any embedded choices
        cleaned_story = clean_story_text(story_so_far)
        
        prompt = f"""
        Based on this story so far in the {genre} genre:
        
        {cleaned_story}
        
        Generate exactly {num_choices} interesting and distinct choices for what the character 
        {character_name if character_name else 'the protagonist'} could do next.
        """
        
        if character_trait:
            prompt += f" Remember that the character is {character_trait}, which may influence their options."
        
        prompt += """
        Each choice should:
        1. Be 1-2 sentences long
        2. Offer a clear and specific action
        3. Lead to different possible story directions
        4. Make sense given the current story situation
        5. NOT reference any options or choices that might be in the story text
        
        Format the response as a JSON array with each choice as a string element. Example format:
        ["Choice 1...", "Choice 2...", "Choice 3..."]
        
        IMPORTANT: DO NOT number the choices or add prefixes like "Option A" - just provide the plain choice text.
        """
        
        response = generate_with_gemini(prompt)
        choices = safe_json_parse(response)
        
        # Ensure we have the requested number of choices
        while len(choices) < num_choices:
            choices.append(f"Try something unexpected.")
        
        return jsonify({"choices": choices[:num_choices]})
    except Exception as e:
        logger.error(f"Error generating choices: {str(e)}")
        return jsonify({
            "error": "Failed to generate choices",
            "choices": [
                "Continue forward cautiously.",
                "Turn back and seek another path.",
                "Call out to see if anyone responds."
            ]
        }), 200  # Return 200 with fallback data

@app.route('/api/continue-story', methods=['POST'])
def api_continue_story():
    """Continue the story based on user choice"""
    data = request.json
    story_so_far = data.get('story_so_far', '')
    chosen_action = data.get('chosen_action', '')
    genre = data.get('genre', '')
    character_name = data.get('character_name', '')
    character_trait = data.get('character_trait', '')
    
    try:
        # Clean the story text first
        cleaned_story = clean_story_text(story_so_far)
        
        prompt = f"""
        Continue this {genre} story where the main character named 
        {character_name if character_name else 'the protagonist'} has chosen the following action:
        
        Story so far: {cleaned_story}
        
        Chosen action: {chosen_action}
        """
        
        if character_trait:
            prompt += f"\nRemember that the character is {character_trait}, which influences their approach and reactions."
        
        prompt += """
        Write the next part of the story (about 400-600 words) that follows from this choice. 
        End at a natural stopping point that creates anticipation for what might happen next.
        
        IMPORTANT:
        - DO NOT include any numbered choices, options, or decision points in your response
        - DO NOT end with phrases like "What will you do?" or "What happens next?"
        - DO NOT write anything like "Option A:" or "Choice 1:" in your response
        - Focus on vivid descriptions, character emotions, and advancing the plot
        - Use a mix of narration and dialog where appropriate
        """
        
        next_part = generate_with_gemini(prompt, temperature=0.8)
        next_part = clean_story_text(next_part)
        
        return jsonify({"next_part": next_part})
    except Exception as e:
        logger.error(f"Error continuing story: {str(e)}")
        return jsonify({
            "error": "Failed to continue story",
            "next_part": "The story continues, but the path ahead is unclear. You must make another choice to proceed."
        }), 200  # Return 200 with fallback data

@app.route('/api/generate-ending', methods=['POST'])
def api_generate_ending():
    """Generate a satisfying conclusion to the story"""
    data = request.json
    story_so_far = data.get('story_so_far', '')
    genre = data.get('genre', '')
    character_name = data.get('character_name', '')
    character_trait = data.get('character_trait', '')
    
    try:
        # Clean the story text first
        cleaned_story = clean_story_text(story_so_far)
        
        prompt = f"""
        Write a satisfying conclusion to this {genre} story featuring 
        {character_name if character_name else 'the protagonist'}:
        
        {cleaned_story}
        """
        
        if character_trait:
            prompt += f"\nRemember that the character is {character_trait}, which should be reflected in how they resolve the situation."
        
        prompt += """
        Create a meaningful and emotionally resonant ending (about 400-600 words) that:
        1. Resolves the main tension or conflict
        2. Provides closure for the character
        3. Reflects the tone and themes of the genre
        4. Leaves the reader with a final image or thought
        
        Make the ending feel earned and connected to the character's journey.
        """
        
        ending = generate_with_gemini(prompt, temperature=0.8)
        
        return jsonify({"ending": ending})
    except Exception as e:
        logger.error(f"Error generating ending: {str(e)}")
        return jsonify({
            "error": "Failed to generate ending",
            "ending": "And so, the adventure came to an end, leaving many questions unanswered but many memories to cherish."
        }), 200  # Return 200 with fallback data

@app.route('/api/generate-recap', methods=['POST'])
def api_generate_recap():
    """Generate a brief recap of the story so far"""
    data = request.json
    choices_made = data.get('choices_made', [])
    genre = data.get('genre', '')
    character_name = data.get('character_name', '')
    
    try:
        # If no choices made yet, return empty string
        if not choices_made:
            return jsonify({"recap": ""})
        
        prompt = f"""
        Create a brief recap (2-3 sentences) of this {genre} story so far featuring {character_name}.
        Focus on the key decisions and turning points.
        
        Here are the choices that were made: {', '.join(choices_made)}
        """
        
        recap = generate_with_gemini(prompt, temperature=0.7)
        
        return jsonify({"recap": recap})
    except Exception as e:
        logger.error(f"Error generating recap: {str(e)}")
        return jsonify({
            "error": "Failed to generate recap",
            "recap": "Your adventure was filled with choices and consequences, leading to this conclusion."
        }), 200  # Return 200 with fallback data

@app.route('/api/text-to-speech', methods=['POST'])
def api_text_to_speech():
    """Generate audio from text"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        audio_path = generate_audio_file(text)
        if audio_path and os.path.exists(audio_path):
            return send_from_directory(
                os.path.dirname(audio_path),
                os.path.basename(audio_path),
                as_attachment=True
            )
        else:
            return jsonify({"error": "Failed to generate audio"}), 500
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-story', methods=['POST'])
def api_save_story():
    """Save story to file"""
    data = request.json
    
    try:
        story_id = data.get("story_id", str(uuid.uuid4()))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saved_stories/{story_id}_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Story saved successfully: {filename}")
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        logger.error(f"Error saving story: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
