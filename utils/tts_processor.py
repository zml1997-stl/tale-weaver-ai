import os
import uuid
import base64
from gtts import gTTS
from pydub import AudioSegment
import subprocess
import tempfile

class TTSProcessor:
    """Process text-to-speech with custom speed using multiple engines."""
    
    def __init__(self):
        """Initialize the TTS processor."""
        # Create a temp directory if it doesn't exist
        os.makedirs('temp_audio', exist_ok=True)
    
    def generate_audio(self, text, speed=1.15, voice_type="enhanced"):
        """Generate audio from text with specified speed.
        
        Args:
            text (str): The text to convert to speech.
            speed (float): The speed factor (1.0 is normal speed).
            voice_type (str): The type of voice to use ("enhanced" or "standard").
            
        Returns:
            str: Base64 encoded audio data.
        """
        # Generate a unique filename
        filename = f"temp_audio/{uuid.uuid4()}.mp3"
        
        try:
            if voice_type == "enhanced":
                # Try to use edge-tts if available (better quality)
                try:
                    return self._generate_edge_tts_audio(text, speed, filename)
                except Exception as e:
                    print(f"Edge TTS failed, falling back to gTTS: {e}")
                    return self._generate_gtts_audio(text, speed, filename)
            else:
                return self._generate_gtts_audio(text, speed, filename)
        except Exception as e:
            print(f"Error generating audio: {e}")
            # Fallback to standard TTS if enhanced fails
            try:
                return self._generate_gtts_audio(text, speed, filename)
            except:
                return None
    
    def _generate_edge_tts_audio(self, text, speed, filename):
        """Generate audio using Microsoft Edge TTS (via subprocess)."""
        # Create a temporary file for the text
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            text_file = f.name
            f.write(text)
        
        try:
            # Use edge-tts command line tool (must be installed via pip)
            # Install with: pip install edge-tts
            voice = "en-US-AriaNeural"  # One of the best Microsoft voices
            
            # Execute edge-tts command
            cmd = [
                "edge-tts",
                "--voice", voice,
                "--file", text_file,
                "--write-media", filename
            ]
            
            # Run the command
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Load audio file with pydub for speed adjustment
            audio = AudioSegment.from_file(filename)
            
            # Adjust speed by modifying the frame rate
            if speed != 1.0:
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
                    os.remove(text_file)
                except:
                    pass
            else:
                # Read the file and encode to base64
                with open(filename, "rb") as audio_file:
                    audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
                
                # Clean up temporary files
                try:
                    os.remove(filename)
                    os.remove(text_file)
                except:
                    pass
            
            return audio_data
            
        except Exception as e:
            print(f"Error generating Edge TTS audio: {e}")
            # Clean up temporary files
            try:
                os.remove(text_file)
            except:
                pass
            # If Edge TTS fails, fall back to gTTS
            raise e
    
    def _generate_gtts_audio(self, text, speed, filename):
        """Generate audio using Google Text-to-Speech."""
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
