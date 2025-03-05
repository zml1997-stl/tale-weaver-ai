/**
 * TextToSpeech class for handling text-to-speech functionality
 */
class TextToSpeech {
    constructor() {
        this.synth = window.speechSynthesis;
        this.utterance = null;
        this.audio = null;
        this.useServerTTS = true; // Set to true to use server-side TTS
        this.voiceType = 'enhanced'; // 'enhanced' or 'standard'
        
        // Try to load voice preference from localStorage
        const savedVoiceType = localStorage.getItem('preferredVoiceType');
        if (savedVoiceType) {
            this.voiceType = savedVoiceType;
        }
    }
    
    /**
     * Set the voice type
     * @param {string} voiceType - 'enhanced' or 'standard'
     */
    setVoiceType(voiceType) {
        this.voiceType = voiceType;
        localStorage.setItem('preferredVoiceType', voiceType);
    }
    
    /**
     * Speak the provided text
     * @param {string} text - The text to speak
     * @param {Object} options - Options for speech
     * @param {number} options.rate - Speech rate (default: 1)
     * @param {string} options.voice - Voice name (default: system default)
     * @param {Function} options.onEnd - Callback when speech ends
     */
    speak(text, options = {}) {
        // Stop any current speech
        this.stop();
        
        if (this.useServerTTS) {
            this._speakWithServer(text, options);
        } else {
            this._speakWithBrowser(text, options);
        }
    }
    
    /**
     * Speak using server-side TTS
     * @private
     */
    _speakWithServer(text, options) {
        // Create a new audio element
        this.audio = new Audio();
        
        // Set onended callback
        if (options.onEnd && typeof options.onEnd === 'function') {
            this.audio.onended = options.onEnd;
        }
        
        // Show loading indicator for TTS
        const ttsLoadingIndicator = document.getElementById('tts-loading');
        if (ttsLoadingIndicator) {
            ttsLoadingIndicator.classList.remove('hidden');
        }
        
        // Call the server to generate audio
        fetch('/generate-audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                speed: options.rate || 1.15,
                voice_type: this.voiceType
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            if (ttsLoadingIndicator) {
                ttsLoadingIndicator.classList.add('hidden');
            }
            
            if (data.success) {
                // Set the audio source to the base64 encoded audio
                this.audio.src = 'data:audio/mp3;base64,' + data.audio_data;
                // Play the audio
                this.audio.play();
            } else {
                console.error('Error generating audio:', data.error);
                // Fall back to browser TTS
                this._speakWithBrowser(text, options);
            }
        })
        .catch(error => {
            // Hide loading indicator
            if (ttsLoadingIndicator) {
                ttsLoadingIndicator.classList.add('hidden');
            }
            
            console.error('Error calling TTS API:', error);
            // Fall back to browser TTS
            this._speakWithBrowser(text, options);
        });
    }
    
    /**
     * Speak using browser's Web Speech API
     * @private
     */
    _speakWithBrowser(text, options) {
        // Create a new utterance
        this.utterance = new SpeechSynthesisUtterance(text);
        
        // Set options
        this.utterance.rate = options.rate || 1;
        
        // Get all available voices
        const voices = this.synth.getVoices();
        
        // Try to find a natural-sounding voice
        // Priority list of good voices available in most browsers
        const preferredVoices = [
            'Google UK English Female',
            'Microsoft Libby Online (Natural)',
            'Samantha',
            'Google US English',
            'Daniel'
        ];
        
        for (const preferredVoice of preferredVoices) {
            const voice = voices.find(v => v.name === preferredVoice);
            if (voice) {
                this.utterance.voice = voice;
                break;
            }
        }
        
        // Set end callback if provided
        if (options.onEnd && typeof options.onEnd === 'function') {
            this.utterance.onend = options.onEnd;
        }
        
        // Start speaking
        this.synth.speak(this.utterance);
    }
    
    /**
     * Stop the current speech
     */
    stop() {
        // Stop browser TTS
        this.synth.cancel();
        this.utterance = null;
        
        // Stop audio element if it exists
        if (this.audio) {
            this.audio.pause();
            this.audio.currentTime = 0;
            this.audio = null;
        }
    }
    
    /**
     * Pause the current speech
     */
    pause() {
        if (this.audio) {
            this.audio.pause();
        } else {
            this.synth.pause();
        }
    }
    
    /**
     * Resume the current speech
     */
    resume() {
        if (this.audio) {
            this.audio.play();
        } else {
            this.synth.resume();
        }
    }
    
    /**
     * Check if the speech synthesis is speaking
     * @returns {boolean} True if speaking, false otherwise
     */
    isSpeaking() {
        if (this.audio) {
            return !this.audio.paused;
        } else {
            return this.synth.speaking;
        }
    }
    
    /**
     * Get available voices
     * @returns {Array} Array of available voices
     */
    getVoices() {
        return this.synth.getVoices();
    }
}
