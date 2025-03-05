/**
 * TextToSpeech class for handling text-to-speech functionality
 */
class TextToSpeech {
    constructor() {
        this.synth = window.speechSynthesis;
        this.utterance = null;
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
        this.synth.cancel();
        this.utterance = null;
    }
    
    /**
     * Pause the current speech
     */
    pause() {
        this.synth.pause();
    }
    
    /**
     * Resume the current speech
     */
    resume() {
        this.synth.resume();
    }
    
    /**
     * Check if the speech synthesis is speaking
     * @returns {boolean} True if speaking, false otherwise
     */
    isSpeaking() {
        return this.synth.speaking;
    }
    
    /**
     * Get available voices
     * @returns {Array} Array of available voices
     */
    getVoices() {
        return this.synth.getVoices();
    }
}
