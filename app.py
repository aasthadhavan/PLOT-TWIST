import os
import json
import requests
import git
import time
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

# Local imports
from config import Config
from models import db, User

# --- GLOBAL CACHE ---
STORY_CACHE = {
    "data": {},
    "last_updated": 0,
    "expiry": 600  # 10 minutes
}

def get_stories():
    """
    Combines local JSON stories with Public API data with caching.
    """
    current_time = time.time()
    
    # Return cache if valid
    if STORY_CACHE["data"] and (current_time - STORY_CACHE["last_updated"] < STORY_CACHE["expiry"]):
        return STORY_CACHE["data"]

    # 1. Local Stories
    try:
        with open('stories.json', 'r') as f:
            stories = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stories = {}

    # 2. Public API - Gutendex (Mystery Topic)
    GUTENBERG_API = "https://gutendex.com/books/?topic=mystery"
    try:
        # Lower timeout for better performance
        response = requests.get(GUTENBERG_API, timeout=2.0)
        if response.status_code == 200:
            books = response.json().get('results', [])[:6]
            for book in books:
                b_id = f"api_{book['id']}"
                stories[b_id] = {
                    "title": f"[ARCHIVE] {book['title']}",
                    "is_api": True,
                    "start": {
                        "text": f"You discover an ancient digital manuscript. Author: {book['authors'][0]['name'] if book['authors'] else 'Unknown'}. This is a read-only historical archive.",
                        "choices": [] # Terminal nodes for API books
                    },
                    # Ensure the 'start' node is accessible directly for the game engine
                    "start_node": {
                        "text": f"You discover an ancient digital manuscript. Author: {book['authors'][0]['name'] if book['authors'] else 'Unknown'}. This is a read-only historical archive.",
                        "choices": []
                    }
                }
    except Exception as e:
        print(f"API Fetch Error: {e}")
    
    # Update Cache
    STORY_CACHE["data"] = stories
    STORY_CACHE["last_updated"] = current_time
    return stories

def checkout_story_branch(repo, username, node_id):
    # Namespace branches to keep dev environment clean
    branch_name = f"{Config.GIT_STORY_NAMESPACE}{username}-{node_id}"
    try:
        if branch_name in [b.name for b in repo.branches]:
            repo.git.checkout(branch_name)
        else:
            repo.git.checkout('-b', branch_name)
    except Exception as e:
        print(f"Git Story Engine Warning: {e}")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def get_repo():
        try:
            return git.Repo(os.getcwd())
        except Exception:
            return git.Repo.init(os.getcwd())

    # --- ROUTES ---

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                user.update_last_login()
                return redirect(url_for('dashboard'))
            
            flash('Invalid identity or access key.', 'error')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if User.query.filter_by(username=username).first():
                flash('Identity already exists in the system.', 'error')
                return redirect(url_for('register'))
            
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Identity verified. You may now authenticate.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        stories = get_stories()
        return render_template('dashboard.html', stories=stories)

    @app.route('/play/<story_id>/<node_id>')
    @login_required
    def play(story_id, node_id):
        all_stories = get_stories()
        story = all_stories.get(story_id)
        
        if not story:
            flash("Story timeline lost.", "error")
            return redirect(url_for('dashboard'))
        
        # Mapping fix: API stories have 'start' node defined inside 'start' key usually,
        # but our engine expects story.get(node_id).
        node = story.get(node_id)
        
        # Fallback for API stories if node_id is 'start'
        if not node and node_id == 'start':
            node = story.get('start_node') or story.get('start')

        if not node:
            flash("Fragment not found.", "error")
            return redirect(url_for('dashboard'))

        # Git Engine Integration
        if not story.get('is_api'):
            checkout_story_branch(get_repo(), current_user.username, node_id)

        # Ensure choices exist
        choices = node.get('choices', []) if isinstance(node, dict) else []
        is_ending = len(choices) == 0

        return render_template('game.html', 
                               node=node, 
                               story_id=story_id, 
                               is_ending=is_ending)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)