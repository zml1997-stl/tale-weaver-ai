/**
 * TextToSpeech class for handling text-to-speech functionality
 */
class TextToSpeech {
    constructor() {
        this.synth = window.speechSynthesis;
        this.utterance = null;
        this.audio = null;
        this.useServerTTS = true; // Set to true to use server-side TTS
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
        
        // Call the server to generate audio
        fetch('/generate-audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                speed: options.rate || 1.15
            })
        })
        .then(response => response.json())
        .then(data => {
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
        
        // Set voice if specified
        if (options.voice) {
            const voices = this.synth.getVoices();
            const voice = voices.find(v => v.name === options.voice);
            if (voice) {
                this.utterance.voice = voice;
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
