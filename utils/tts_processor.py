from gtts import gTTS
from pydub import AudioSegment
import os
import uuid
import base64

class TTSProcessor:
    """Process text-to-speech with custom speed using pydub."""
    
    def __init__(self):
        """Initialize the TTS processor."""
        # Create a temp directory if it doesn't exist
        os.makedirs('temp_audio', exist_ok=True)
    
    def generate_audio(self, text, speed=1.15):
        """Generate audio from text with specified speed.
        
        Args:
            text (str): The text to convert to speech.
            speed (float): The speed factor (1.0 is normal speed).
            
        Returns:
            str: Base64 encoded audio data.
        """
        # Generate a unique filename
        filename = f"temp_audio/{uuid.uuid4()}.mp3"
        
        try:
            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filename)
            
            # Load audio file with pydub
            audio = AudioSegment.from_file(filename)
            
            # Adjust speed by modifying the frame rate
            # Speed up = higher frame rate
            new_frame_rate = int(audio.frame_rate * speed)
            audio_speed_adjusted = audio._spawn(audio.raw_data, overrides={
                "frame_rate": new_frame_rate
            })
            
            # Export the modified audio to a new file
            speed_adjusted_filename = f"temp_audio/{uuid.uuid4()}_speed.mp3"
            audio_speed_adjusted.export(speed_adjusted_filename, format="mp3")
            
            # Read the file and encode to base64
            with open(speed_adjusted_filename, "rb") as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # Clean up temporary files
            try:
                os.remove(filename)
                os.remove(speed_adjusted_filename)
            except:
                pass
            
            return audio_data
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None
