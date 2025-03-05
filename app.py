from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_session import Session
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from config import Config
from utils.story_generator import StoryGenerator
from utils.storage import StoryStorage

# Create Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize story generator and storage
story_generator = StoryGenerator()
story_storage = StoryStorage()

# Custom Jinja2 filters
@app.template_filter('format_date')
def format_date(value):
    """Format a date string."""
    try:
        date_obj = datetime.fromisoformat(value)
        return date_obj.strftime('%B %d, %Y at %I:%M %p')
    except (ValueError, TypeError):
        return value

@app.template_filter('truncate')
def truncate_text(text, length=100):
    """Truncate text to a specified length."""
    if not text or len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'

# Custom Jinja2 globals
@app.context_processor
def inject_now():
    """Inject current datetime into templates."""
    return {'now': datetime.now}

# Routes
@app.route('/')
def index():
    """Render the homepage."""
    # Get recent stories from session
    recent_stories = session.get('recent_stories', [])
    
    return render_template(
        'index.html',
        genres=Config.STORY_GENRES,
        recent_stories=recent_stories
    )

@app.route('/genre-starters', methods=['POST'])
def genre_starters():
    """Generate story starters for a selected genre."""
    genre = request.form.get('genre')
    
    if not genre:
        flash('Please select a genre.', 'error')
        return redirect(url_for('index'))
    
    # Generate story starters for the selected genre
    starters = story_generator.get_story_starters(genre)
    
    # Store the starters in the session
    session['starters'] = starters
    session['genre'] = genre
    
    return render_template(
        'story_starters.html',
        genre=genre,
        starters=starters
    )

@app.route('/custom-story', methods=['POST'])
def custom_story():
    """Generate a story from a custom idea."""
    story_idea = request.form.get('story_idea')
    
    if not story_idea:
        flash('Please enter a story idea.', 'error')
        return redirect(url_for('index'))
    
    # Generate a story starter from the custom idea
    starter = story_generator.get_story_from_idea(story_idea)
    
    # Generate initial options
    options = story_generator.get_story_options(starter)
    
    return render_template(
        'story.html',
        story_starter=starter,
        options=options,
        story_parts=[starter],
        story_ended=False
    )

@app.route('/start-story/<int:starter_id>', methods=['GET'])
def start_story(starter_id):
    """Start a story with a selected starter."""
    starters = session.get('starters')
    genre = session.get('genre')
    
    if not starters or starter_id >= len(starters):
        flash('Invalid story starter.', 'error')
        return redirect(url_for('index'))
    
    # Get the selected starter
    starter = starters[starter_id]
    
    # Generate initial options
    options = story_generator.get_story_options(starter)
    
    return render_template(
        'story.html',
        story_starter=starter,
        options=options,
        story_parts=[starter],
        story_ended=False
    )

@app.route('/continue-story', methods=['POST'])
def continue_story():
    """Continue a story based on a selected option."""
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided.'})
    
    story_id = data.get('story_id')
    story_parts = data.get('story_parts', [])
    selected_option = data.get('selected_option')
    
    if not story_parts or not selected_option:
        return jsonify({'success': False, 'error': 'Missing required data.'})
    
    # Join all story parts into a single string
    story_so_far = ' '.join(story_parts)
    
    # Generate the next part of the story
    new_part = story_generator.continue_story(story_so_far, selected_option)
    
    # Add the new part to the story
    story_parts.append(new_part)
    
    # Join all story parts into a single string again
    story_so_far = ' '.join(story_parts)
    
    # Generate new options
    new_options = story_generator.get_story_options(story_so_far)
    
    # Check if the story should end due to length
    should_end = story_generator.is_story_too_long(story_parts)
    
    return jsonify({
        'success': True,
        'new_part': new_part,
        'new_options': new_options,
        'should_end': should_end
    })

@app.route('/end-story', methods=['POST'])
def end_story():
    """End a story and generate a conclusion."""
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided.'})
    
    story_id = data.get('story_id')
    story_parts = data.get('story_parts', [])
    
    if not story_parts:
        return jsonify({'success': False, 'error': 'Missing required data.'})
    
    # Join all story parts into a single string
    story_so_far = ' '.join(story_parts)
    
    # Generate a conclusion for the story
    ending = story_generator.get_story_ending(story_so_far)
    
    return jsonify({
        'success': True,
        'ending': ending
    })

@app.route('/save-story', methods=['POST'])
def save_story():
    """Save a story."""
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided.'})
    
    title = data.get('title')
    story_parts = data.get('story_parts', [])
    ended = data.get('ended', False)
    
    if not title or not story_parts:
        return jsonify({'success': False, 'error': 'Missing required data.'})
    
    # Create a story data object
    story_data = {
        'title': title,
        'content': ' '.join(story_parts),
        'parts': story_parts,
        'ended': ended
    }
    
    # Save the story
    story_id = story_storage.save_story(story_data)
    
    # Add the story to recent stories in session
    recent_stories = session.get('recent_stories', [])
    
    # Add the new story to the beginning of the list
    recent_story = {
        'id': story_id,
        'title': title,
        'content': story_data['content'],
        'timestamp': datetime.now().isoformat()
    }
    
    recent_stories.insert(0, recent_story)
    
    # Keep only the 5 most recent stories
    recent_stories = recent_stories[:5]
    
    # Update the session
    session['recent_stories'] = recent_stories
    
    return jsonify({
        'success': True,
        'story_id': story_id
    })

@app.route('/view-story/<story_id>')
def view_story(story_id):
    """View a saved story."""
    story_data = story_storage.get_story(story_id)
    
    if not story_data:
        flash('Story not found.', 'error')
        return redirect(url_for('saved_stories'))
    
    return render_template(
        'story.html',
        story_id=story_id,
        title=story_data.get('title'),
        story_parts=story_data.get('parts', []),
        story_ended=story_data.get('ended', True),
        options=[]
    )

@app.route('/saved-stories')
def saved_stories():
    """View all saved stories."""
    stories = story_storage.get_all_stories()
    
    return render_template(
        'saved_stories.html',
        stories=stories
    )

@app.route('/delete-story/<story_id>', methods=['DELETE'])
def delete_story(story_id):
    """Delete a saved story."""
    success = story_storage.delete_story(story_id)
    
    if success:
        # Remove the story from recent stories in session
        recent_stories = session.get('recent_stories', [])
        recent_stories = [s for s in recent_stories if s.get('id') != story_id]
        session['recent_stories'] = recent_stories
        
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Story not found.'})

@app.route('/story_starters.html')
def story_starters_template():
    """Render the story starters template."""
    genre = session.get('genre', '')
    starters = session.get('starters', [])
    
    return render_template(
        'story_starters.html',
        genre=genre,
        starters=starters
    )

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', error_code=404, error_message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('error.html', error_code=500, error_message='Server error'), 500

if __name__ == '__main__':
    # Ensure the stories directory exists
    os.makedirs('stories', exist_ok=True)
    
    # Create the Flask-Session directory if it doesn't exist
    os.makedirs('flask_session', exist_ok=True)
    
    # Run the application
    app.run(debug=Config.DEBUG)
