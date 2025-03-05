import os
import uuid
import base64
from gtts import gTTS
from pydub import AudioSegment
import torch
from TTS.api import TTS

class TTSProcessor:
    """Process text-to-speech with custom speed using Coqui TTS."""
    
    def __init__(self):
        """Initialize the TTS processor."""
        # Create a temp directory if it doesn't exist
        os.makedirs('temp_audio', exist_ok=True)
        
        # Initialize Coqui TTS
        try:
            self.coqui_available = torch.cuda.is_available()
            if self.coqui_available:
                # Use GPU if available
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                # Initialize TTS with a good English model
                self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False).to(self.device)
            else:
                # Initialize TTS with a smaller model for CPU
                self.device = "cpu"
                self.tts = TTS(model_name="tts_models/en/ljspeech/glow-tts", progress_bar=False)
            
            print(f"Coqui TTS initialized on {self.device}")
            self.coqui_available = True
        except Exception as e:
            print(f"Error initializing Coqui TTS: {e}")
            self.coqui_available = False
    
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
            if voice_type == "enhanced" and self.coqui_available:
                return self._generate_coqui_audio(text, speed, filename)
            else:
                return self._generate_gtts_audio(text, speed, filename)
        except Exception as e:
            print(f"Error generating audio: {e}")
            # Fallback to standard TTS if enhanced fails
            if voice_type == "enhanced":
                return self._generate_gtts_audio(text, speed, filename)
            return None
    
    def _generate_coqui_audio(self, text, speed, filename):
        """Generate audio using Coqui TTS."""
        try:
            # Generate speech using Coqui TTS
            # We'll use the wav file format for better quality
            wav_filename = filename.replace('.mp3', '.wav')
            
            # Generate the audio
            self.tts.tts_to_file(text=text, file_path=wav_filename)
            
            # Convert to MP3 and adjust speed using pydub
            audio = AudioSegment.from_file(wav_filename)
            
            # Adjust speed by modifying the frame rate
            if speed != 1.0:
                new_frame_rate = int(audio.frame_rate * speed)
                audio_speed_adjusted = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": new_frame_rate
                })
            else:
                audio_speed_adjusted = audio
            
            # Export to MP3
            audio_speed_adjusted.export(filename, format="mp3")
            
            # Read the file and encode to base64
            with open(filename, "rb") as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # Clean up temporary files
            try:
                os.remove(wav_filename)
                os.remove(filename)
            except:
                pass
            
            return audio_data
            
        except Exception as e:
            print(f"Error generating Coqui TTS audio: {e}")
            # If Coqui fails, fall back to gTTS
            return self._generate_gtts_audio(text, speed, filename)
    
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
