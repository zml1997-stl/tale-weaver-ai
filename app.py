# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from utils.gemini_client import GeminiClient
from utils.session_manager import SessionManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Initialize Gemini client and session manager
gemini_client = GeminiClient(api_key=os.getenv('GEMINI_API_KEY'))
session_manager = SessionManager()

# Homepage route
@app.route('/')
def index():
    return render_template('index.html')

# Instructions route
@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

# Story generation route
@app.route('/generate-story', methods=['GET', 'POST'])
def generate_story():
    if request.method == 'POST':
        # Get user input (genre or custom idea)
        user_input = request.form.get('story_input')
        
        # Generate story starters
        if user_input in ['fantasy', 'sci-fi', 'mystery', 'romance']:
            # Genre selected
            starters = gemini_client.generate_story_starters(genre=user_input)
            session['current_story'] = {
                'starters': starters,
                'story_parts': []
            }
            return render_template('story_gen.html', starters=starters)
        else:
            # Custom idea
            starter = gemini_client.generate_custom_starter(user_input)
            session['current_story'] = {
                'starters': [starter],
                'story_parts': []
            }
            return redirect(url_for('story_page'))
    
    return render_template('story_gen.html')

# Interactive story page route
@app.route('/story-page')
def story_page():
    if 'current_story' not in session:
        return redirect(url_for('index'))
    
    return render_template('story_page.html')

# API endpoint for generating next story part
@app.route('/generate-next', methods=['POST'])
def generate_next():
    data = request.json
    previous_part = data.get('previous_part')
    selected_option = data.get('selected_option')
    
    next_part = gemini_client.generate_next_story_part(
        previous_part=previous_part,
        selected_option=selected_option
    )
    
    # Update session with new story part
    session_manager.update_story(session, next_part)
    
    return jsonify({
        'next_part': next_part,
        'options': gemini_client.generate_options(next_part)
    })

# End story route
@app.route('/end-story')
def end_story():
    if 'current_story' not in session:
        return redirect(url_for('index'))
    
    # Generate final ending
    final_ending = gemini_client.generate_ending(
        session['current_story']['story_parts']
    )
    
    # Save full story
    full_story = session_manager.save_story(session, final_ending)
    
    return render_template('story_page.html', final_ending=final_ending)

if __name__ == '__main__':
    app.run(debug=True)
