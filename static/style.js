// Global state management
const appState = {
    story_id: crypto.randomUUID(),
    current_text: "",
    choices_made: [],
    path_taken: [],
    genre: "",
    character_name: "",
    character_trait: "",
    stage: "welcome",  // welcome, setup, story, ending
    story_turns: 0,
    word_count: 0,
    audio_enabled: true
};

// API endpoint (will be replaced with actual backend URL)
const API_ENDPOINT = 'https://tale-weaver-ai-ca866b586bec.herokuapp.com/api';

// DOM ready handler
document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI based on app state
    showScreen(appState.stage);
    setupEventListeners();
    
    // Set up genre selection
    populateGenreSelection();
});

// Screen management
function showScreen(screenName) {
    // Hide all screens
    document.querySelectorAll('#welcome-screen, #setup-screen, #story-screen, #ending-screen, #loading-spinner').forEach(screen => {
        screen.classList.add('d-none');
    });
    
    // Show requested screen
    const screenToShow = document.getElementById(`${screenName}-screen`);
    if (screenToShow) {
        screenToShow.classList.remove('d-none');
    }
    
    // Update sidebar based on current screen
    updateSidebar();
}

// Set up all event listeners
function setupEventListeners() {
    // Welcome screen buttons
    document.getElementById('begin-journey').addEventListener('click', () => {
        appState.stage = 'setup';
        showScreen('setup');
    });
    
    document.getElementById('load-saved').addEventListener('click', () => {
        loadSavedStories();
    });
    
    // Setup screen - character creation
    document.getElementById('generate-starters').addEventListener('click', () => {
        const characterName = document.getElementById('character-name').value;
        const characterTrait = document.getElementById('character-trait').value;
        
        appState.character_name = characterName;
        appState.character_trait = characterTrait;
        
        generateStoryStarters();
    });
    
    // Story screen buttons
    document.getElementById('save-story').addEventListener('click', () => {
        saveStory();
        showToast('Story saved successfully!');
    });
    
    document.getElementById('end-story').addEventListener('click', () => {
        appState.stage = 'ending';
        generateStoryEnding();
    });
    
    document.getElementById('new-story').addEventListener('click', () => {
        if (appState.story_turns > 0) {
            saveStory();
        }
        resetStory();
        appState.stage = 'welcome';
        showScreen('welcome');
    });
    
    // Ending screen buttons
    document.getElementById('new-adventure').addEventListener('click', () => {
        resetStory();
        appState.stage = 'welcome';
        showScreen('welcome');
    });
    
    document.getElementById('view-saved-stories').addEventListener('click', () => {
        resetStory();
        appState.stage = 'welcome';
        loadSavedStories();
    });
    
    document.getElementById('copy-clipboard').addEventListener('click', () => {
        const cleanText = appState.current_text.replace(/<[^>]*>/g, '');
        navigator.clipboard.writeText(cleanText)
            .then(() => showToast('Story copied to clipboard!'))
            .catch(err => showToast('Failed to copy text: ' + err));
    });
    
    document.getElementById('download-text').addEventListener('click', () => {
        const cleanText = appState.current_text.replace(/<[^>]*>/g, '');
        const filename = `${appState.genre}_${new Date().toISOString().split('T')[0]}.txt`;
        downloadTextFile(cleanText, filename);
    });
    
    // Audio settings
    document.getElementById('audioEnabled').addEventListener('change', (e) => {
        appState.audio_enabled = e.target.checked;
    });
}

// Genre selection setup
function populateGenreSelection() {
    const genreContainer = document.getElementById('genre-selection');
    if (!genreContainer) return;
    
    const genres = [
        { name: "Fantasy", description: "Magical worlds, mythical creatures, and heroic quests" },
        { name: "Science Fiction", description: "Future technology, space exploration, and scientific possibilities" },
        { name: "Mystery", description: "Puzzles, investigations, and secrets waiting to be uncovered" },
        { name: "Adventure", description: "Exploration, discovery, and overcoming challenges" },
        { name: "Horror", description: "Fear, suspense, and encounters with the unknown" },
        { name: "Romance", description: "Relationships, emotional connections, and matters of the heart" },
        { name: "Historical", description: "Stories set in the past, often based on real events or periods" },
        { name: "Comedy", description: "Humor, wit, and light-hearted situations" }
    ];
    
    let html = '';
    
    genres.forEach(genre => {
        html += `
            <div class="col-md-6 mb-3">
                <div class="story-option">
                    <span class="genre-badge">${genre.name}</span><br>
                    <small>${genre.description}</small>
                </div>
                <button class="btn btn-primary w-100 mt-2 genre-button" 
                        data-genre="${genre.name}">Select ${genre.name}</button>
            </div>
        `;
    });
    
    genreContainer.innerHTML = html;
    
    // Add event listeners to genre buttons
    document.querySelectorAll('.genre-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const selectedGenre = e.target.dataset.genre;
            appState.genre = selectedGenre;
            
            // Show character creation
            document.getElementById('character-creation').classList.remove('d-none');
            
            // Update sidebar
            updateSidebar();
        });
    });
}

// Story starters generation
async function generateStoryStarters() {
    showLoading('Crafting your adventure beginnings...');
    
    try {
        const response = await fetch(`${API_ENDPOINT}/generate-starters`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                genre: appState.genre,
                character_name: appState.character_name,
                character_trait: appState.character_trait
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate story starters');
        }
        
        const data = await response.json();
        displayStoryStarters(data.starters);
    } catch (error) {
        console.error('Error generating starters:', error);
        // Fallback starters
        const fallbackStarters = [
            "You find yourself standing at the edge of a mysterious forest with a map that seems to lead to a hidden treasure.",
            "The spaceship's alarm blares as you wake up from cryosleep, the rest of the crew is missing.",
            "The old mansion you just inherited contains a locked room that nobody has entered for over a century."
        ];
        displayStoryStarters(fallbackStarters);
    } finally {
        hideLoading();
    }
}

// Display story starters
function displayStoryStarters(starters) {
    const startersContainer = document.getElementById('starters-container');
    document.getElementById('story-starters').classList.remove('d-none');
    
    let html = '';
    starters.forEach((starter, index) => {
        html += `
            <div class="story-option mb-3">
                ${starter}
            </div>
            <button class="btn btn-primary w-100 mb-4 starter-button" 
                    data-index="${index}" data-text="${encodeURIComponent(starter)}">Begin This Story</button>
        `;
    });
    
    startersContainer.innerHTML = html;
    
    // Add event listeners to starter buttons
    document.querySelectorAll('.starter-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const index = e.target.dataset.index;
            const starterText = decodeURIComponent(e.target.dataset.text);
            
            // Save selections and move to story stage
            appState.current_text = starterText;
            appState.path_taken.push({type: "beginning", text: starterText});
            appState.word_count = starterText.split(' ').length;
            appState.story_turns = 0;
            appState.stage = 'story';
            
            // Generate audio for starter if enabled
            if (appState.audio_enabled) {
                generateAudio(starterText);
            }
            
            // Move to story screen
            showScreen('story');
            updateStoryDisplay();
            generateChoices();
        });
    });
}

// Update story display
function updateStoryDisplay() {
    // Update story header
    const characterName = appState.character_name ? `${appState.character_name}'s` : 'Your';
    document.getElementById('story-header').innerHTML = `
        <span class='genre-badge'>${appState.genre}</span> ${characterName} Adventure
    `;
    
    // Update story progress
    const stats = calculateStoryStats();
    document.getElementById('story-progress').innerHTML = `
        <strong>Story Progress:</strong> Turn ${appState.story_turns} | 
        <strong>Words:</strong> ${stats.word_count} | 
        <strong>Reading Time:</strong> ~${stats.reading_time} min | 
        <strong>Choices Made:</strong> ${stats.choices_made}
    `;
    
    // Format and display current story
    let formattedStory = appState.current_text;
    // Process for better display - convert dialog
    formattedStory = formattedStory.replace(/"([^"]*)"/g, '<span class="dialog">"$1"</span>');
    
    document.getElementById('story-text').innerHTML = formattedStory;
}

// Generate choices for the current story state
async function generateChoices() {
    showLoading('Determining possible paths...');
    
    try {
        const response = await fetch(`${API_ENDPOINT}/generate-choices`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                story_so_far: appState.current_text,
                genre: appState.genre,
                character_name: appState.character_name,
                character_trait: appState.character_trait,
                num_choices: 3
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate choices');
        }
        
        const data = await response.json();
        displayChoices(data.choices);
    } catch (error) {
        console.error('Error generating choices:', error);
        // Fallback choices
        const fallbackChoices = [
            "Continue forward cautiously.",
            "Turn back and seek another path.",
            "Call out to see if anyone responds."
        ];
        displayChoices(fallbackChoices);
    } finally {
        hideLoading();
    }
}

// Display choices
function displayChoices(choices) {
    const choicesContainer = document.getElementById('choices-container');
    
    let html = '';
    choices.forEach((choice, index) => {
        html += `
            <button class="btn btn-primary mb-2 choice-button" 
                    data-choice="${encodeURIComponent(choice)}">
                ${choice}
            </button>
        `;
    });
    
    choicesContainer.innerHTML = html;
    
    // Add event listeners to choice buttons
    document.querySelectorAll('.choice-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const chosenAction = decodeURIComponent(e.target.dataset.choice);
            makeChoice(chosenAction);
        });
    });
}

// Process user's choice
async function makeChoice(chosenAction) {
    // Record choice
    appState.choices_made.push(chosenAction);
    appState.path_taken.push({type: "choice", text: chosenAction});
    
    showLoading('The story unfolds...');
    
    try {
        const response = await fetch(`${API_ENDPOINT}/continue-story`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                story_so_far: appState.current_text,
                chosen_action: chosenAction,
                genre: appState.genre,
                character_name: appState.character_name,
                character_trait: appState.character_trait
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to continue story');
        }
        
        const data = await response.json();
        
        // Update story text with user's choice and next part
        appState.current_text += `\n\n<div class='choice-marker'>You chose: ${chosenAction}</div>\n\n${data.next_part}`;
        
        // Generate audio for the next part if enabled
        if (appState.audio_enabled) {
            generateAudio(data.next_part);
        }
        
        // Update word count
        appState.word_count = appState.current_text.split(' ').length;
        
        // Increment turn counter
        appState.story_turns += 1;
        
        // Save automatically
        saveStory();
        
        // Check if we should end story based on turns
        if (appState.story_turns >= 10) {
            appState.stage = 'ending';
            showScreen('ending');
            generateStoryEnding();
        } else {
            // Update display and generate new choices
            updateStoryDisplay();
            generateChoices();
        }
    } catch (error) {
        console.error('Error continuing story:', error);
        showToast('Something went wrong with the story generation. Please try again.');
        
        // Fallback continuation
        const fallbackContinuation = "The story continues, but the path ahead is unclear. You must make another choice to proceed.";
        appState.current_text += `\n\n<div class='choice-marker'>You chose: ${chosenAction}</div>\n\n${fallbackContinuation}`;
        updateStoryDisplay();
        generateChoices();
    } finally {
        hideLoading();
    }
}

// Generate story ending
async function generateStoryEnding() {
    showLoading('Crafting your story\'s conclusion...');
    
    try {
        const response = await fetch(`${API_ENDPOINT}/generate-ending`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                story_so_far: appState.current_text,
                genre: appState.genre,
                character_name: appState.character_name,
                character_trait: appState.character_trait
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate story ending');
        }
        
        const data = await response.json();
        const endingText = data.ending;
        
        // Update story with ending
        appState.current_text += `\n\n<div class='section-header'>The Conclusion</div>\n\n${endingText}`;
        appState.path_taken.push({type: "ending", text: endingText});
        
        // Generate audio for the ending if enabled
        if (appState.audio_enabled) {
            generateAudio(endingText);
        }
        
        // Update word count
        appState.word_count = appState.current_text.split(' ').length;
        
        // Save story with ending
        saveStory();
        
        // Display ending
        displayEnding(endingText);
    } catch (error) {
        console.error('Error generating ending:', error);
        
        // Fallback ending
        const fallbackEnding = "And so, the adventure came to an end, leaving many questions unanswered but many memories to cherish.";
        appState.current_text += `\n\n<div class='section-header'>The Conclusion</div>\n\n${fallbackEnding}`;
        displayEnding(fallbackEnding);
    } finally {
        hideLoading();
    }
}

// Display story ending
function displayEnding(endingText) {
    // Display story stats
    const stats = calculateStoryStats();
    document.getElementById('ending-stats').innerHTML = `
        <strong>Final Statistics:</strong><br>
        <strong>Story Length:</strong> ${stats.word_count} words<br>
        <strong>Reading Time:</strong> ~${stats.reading_time} minutes<br>
        <strong>Choices Made:</strong> ${stats.choices_made}<br>
        <strong>Story Turns:</strong> ${appState.story_turns}
    `;
    
    // Generate and display summary/recap
    generateRecap().then(recap => {
        document.getElementById('story-summary').innerHTML = recap;
    });
    
    // Display full story with ending
    let formattedStory = appState.current_text;
    // Process for better display - convert dialog
    formattedStory = formattedStory.replace(/"([^"]*)"/g, '<span class="dialog">"$1"</span>');
    document.getElementById('full-story').innerHTML = formattedStory;
    
    // Show ending screen
    showScreen('ending');
}

// Generate recap of the story
async function generateRecap() {
    try {
        const response = await fetch(`${API_ENDPOINT}/generate-recap`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                choices_made: appState.choices_made,
                genre: appState.genre,
                character_name: appState.character_name
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate recap');
        }
        
        const data = await response.json();
        return data.recap;
    } catch (error) {
        console.error('Error generating recap:', error);
        return 'Your adventure was filled with choices and consequences, leading to this conclusion.';
    }
}

// Calculate story statistics
function calculateStoryStats() {
    // Count words in current story
    const wordCount = appState.current_text.split(' ').length;
    
    // Estimate reading time (avg 200-250 wpm)
    let readingTime = Math.round(wordCount / 225);
    if (readingTime < 1) readingTime = "< 1";
    
    // Count choices made
    const choicesMade = appState.choices_made.length;
    
    return {
        word_count: wordCount,
        reading_time: readingTime,
        choices_made: choicesMade
    };
}

// Save story to localStorage
function saveStory() {
    try {
        const timestamp = new Date().toISOString();
        const storyData = {
            ...appState,
            timestamp: timestamp
        };
        
        // Save to localStorage
        localStorage.setItem(`tale_weaver_${appState.story_id}`, JSON.stringify(storyData));
        
        // Also send to server if API is available
        fetch(`${API_ENDPOINT}/save-story`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(storyData)
        }).catch(err => console.log('Server save optional, using localStorage:', err));
        
        return true;
    } catch (error) {
        console.error('Error saving story:', error);
        return false;
    }
}

// Load saved stories
function loadSavedStories() {
    try {
        // Get all saved stories from localStorage
        const savedStories = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('tale_weaver_')) {
                try {
                    const storyData = JSON.parse(localStorage.getItem(key));
                    
                    // Format date
                    const date = new Date(storyData.timestamp);
                    const formattedDate = date.toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                    });
                    
                    savedStories.push({
                        filename: key,
                        date: formattedDate,
                        genre: storyData.genre || 'Unknown',
                        character: storyData.character_name || 'Unknown',
                        choices: storyData.choices_made.length,
                        story_id: storyData.story_id,
                        word_count: storyData.word_count || 0
                    });
                } catch (e) {
                    console.error('Error parsing saved story:', e);
                }
            }
        }
        
        // Sort by date (newest first)
        savedStories.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        // Display saved stories
        displaySavedStories(savedStories);
    } catch (error) {
        console.error('Error loading saved stories:', error);
        showToast('Error loading saved stories');
    }
}

// Display saved stories
function displaySavedStories(stories) {
    const savedStoriesList = document.getElementById('saved-stories-list');
    document.getElementById('saved-stories').classList.remove('d-none');
    
    if (stories.length === 0) {
        savedStoriesList.innerHTML = '<div class="alert alert-info">No saved stories found. Start a new adventure!</div>';
        return;
    }
    
    let html = '';
    stories.forEach(story => {
        html += `
            <div class="row mb-3">
                <div class="col-md-8">
                    <div class="story-option">
                        <strong>${story.character}'s ${story.genre} Adventure</strong><br>
                        <small>Saved on ${story.date} • ${story.choices} choices made • ${story.word_count} words</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <button class="btn btn-primary w-100 load-story-btn" 
                            data-story-id="${story.story_id}" 
                            data-filename="${story.filename}">Continue</button>
                </div>
            </div>
        `;
    });
    
    savedStoriesList.innerHTML = html;
    
    // Add event listeners to load story buttons
    document.querySelectorAll('.load-story-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const filename = e.target.dataset.filename;
            loadStory(filename);
        });
    });
}

// Load a specific story
function loadStory(filename) {
    try {
        const storyData = JSON.parse(localStorage.getItem(filename));
        
        // Update app state with loaded story
        Object.assign(appState, storyData);
        
        // Set stage to story
        appState.stage = 'story';
        
        // Show story screen
        showScreen('story');
        updateStoryDisplay();
        generateChoices();
    } catch (error) {
        console.error('Error loading story:', error);
        showToast('Error loading story');
    }
}

// Reset story state
function resetStory() {
    appState.story_id = crypto.randomUUID();
    appState.current_text = "";
    appState.choices_made = [];
    appState.path_taken = [];
    appState.genre = "";
    appState.character_name = "";
    appState.character_trait = "";
    appState.stage = "welcome";
    appState.story_turns = 0;
    appState.word_count = 0;
}

// Update sidebar based on current state
function updateSidebar() {
    const storyInfo = document.getElementById('story-info');
    const storyDetails = document.getElementById('story-details');
    const journeyChoices = document.getElementById('journey-choices');
    
    if (appState.stage === 'welcome') {
        storyInfo.classList.add('d-none');
        return;
    }
    
    storyInfo.classList.remove('d-none');
    
    // Update story details
    let detailsHtml = '';
    if (appState.genre) {
        detailsHtml += `<p><strong>Genre:</strong> ${appState.genre}</p>`;
    }
    if (appState.character_name) {
        detailsHtml += `<p><strong>Protagonist:</strong> ${appState.character_name}</p>`;
    }
    if (appState.character_trait) {
        detailsHtml += `<p><strong>Character Trait:</strong> ${appState.character_trait}</p>`;
    }
    storyDetails.innerHTML = detailsHtml;
    
    // Update journey choices
    if (appState.choices_made.length > 0) {
        let choicesHtml = '<ol>';
        appState.choices_made.forEach(choice => {
            choicesHtml += `<li>${choice}</li>`;
        });
        choicesHtml += '</ol>';
        journeyChoices.innerHTML = choicesHtml;
    } else {
        journeyChoices.innerHTML = '<p>No choices made yet.</p>';
    }
}

// Text to speech functionality
async function generateAudio(text) {
    if (!appState.audio_enabled) return;
    
    try {
        const response = await fetch(`${API_ENDPOINT}/text-to-speech`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate audio');
        }
        
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Create and play audio element
        const audioPlayer = document.getElementById('audio-player');
        audioPlayer.innerHTML = `
            <audio controls autoplay style="width: 100%;">
                <source src="${audioUrl}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        `;
    } catch (error) {
        console.error('Error generating audio:', error);
    }
}

// Show loading spinner
function showLoading(message = 'Loading...') {
    const spinner = document.getElementById('loading-spinner');
    const loadingMessage = document.getElementById('loading-message');
    
    loadingMessage.textContent = message;
    spinner.classList.remove('d-none');
}

// Hide loading spinner
function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    spinner.classList.add('d-none');
}

// Show toast notification
function showToast(message, title = 'Tale Weaver') {
    const toastEl = document.getElementById('toast-notification');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');
    
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// Download text file
function downloadTextFile(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Clean story text by removing embedded AI choices and formatting artifacts
function cleanStoryText(text) {
    // Remove patterns like "Option A: ...", "1. ...", "Choice: ..." etc.
    const patterns = [
        /(?:Option|Choice)\s+[A-Za-z0-9]+\s*:\s*.*?(?=(?:Option|Choice)|$)/g,
        /\d+\.\s+.*?(?=\d+\.|$)/g,
        /•\s+.*?(?=•|$)/g
    ];
    
    let cleanedText = text;
    for (const pattern of patterns) {
        cleanedText = cleanedText.replace(pattern, '');
    }
    
    // Remove any remaining numbered list markers
    cleanedText = cleanedText.replace(/^\s*\d+\.\s+/gm, '');
    
    // Remove any "What will you do?" or similar prompts
    const promptsToRemove = [
        /What will you do\?/g,
        /What do you do next\?/g,
        /What happens next\?/g,
        /What choice will you make\?/g,
        /Choose your next action./g,
        /What would you like to do\?/g
    ];
    
    for (const prompt of promptsToRemove) {
        cleanedText = cleanedText.replace(prompt, '');
    }
    
    return cleanedText.trim();
}
