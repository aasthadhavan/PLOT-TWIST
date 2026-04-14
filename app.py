import os
import json
import requests
import git
import time
import re
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

# Local imports
from config import Config
from models import db, User, GameSession

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- SCM ENGINE (GIT INTEGRATION) ---
    def get_repo():
        try:
            return git.Repo(app.root_path, search_parent_directories=True)
        except Exception:
            app.logger.warning(f"Git Engine: Repository not found at {app.root_path}. Initializing...")
            try:
                if not os.path.exists(app.root_path):
                    os.makedirs(app.root_path)
                return git.Repo.init(app.root_path)
            except Exception as e:
                app.logger.error(f"Git Engine Critical Failure: {e}")
                return None

    def checkout_story_branch(username, node_id):
        repo = get_repo()
        if not repo: return

        clean_user = re.sub(r'[^a-zA-Z0-9_-]', '_', username)
        clean_node = re.sub(r'[^a-zA-Z0-9_-]', '_', node_id)
        branch_name = f"{app.config.get('GIT_STORY_NAMESPACE', 'story/')}{clean_user}-{clean_node}"
        
        try:
            existing_branches = [b.name for b in repo.branches]
            if branch_name in existing_branches:
                repo.git.checkout(branch_name)
            else:
                repo.git.checkout('-b', branch_name)
        except Exception as e:
            app.logger.warning(f"Git Engine: Could not switch to branch {branch_name}: {e}")

    # --- API CACHING SETUP ---
    _api_cache = {
        "data": None,
        "timestamp": 0,
        "books_content": {} 
    }
    CACHE_DURATION = 3600 

    # --- DATA LAYER (API & LOCAL) ---
    def get_stories():
        stories_path = os.path.join(app.root_path, 'stories.json')
        try:
            with open(stories_path, 'r') as f:
                stories = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            stories = {}

        current_time = time.time()
        if _api_cache["data"] and (current_time - _api_cache["timestamp"] < CACHE_DURATION):
            api_stories = _api_cache["data"]
        else:
            api_stories = {}
            GUTENDEX_API_URL = "https://gutendex.com/books/?topic=mystery"
            try:
                response = requests.get(GUTENDEX_API_URL, timeout=10)
                if response.status_code == 200:
                    books = response.json().get('results', [])[:10]
                    for book in books:
                        b_id = f"guten_{book['id']}"
                        api_stories[b_id] = {
                            "title": book['title'],
                            "is_api": True,
                            "author": book['authors'][0]['name'] if book['authors'] else "Unknown",
                            "text_url": book['formats'].get('text/plain; charset=utf-8') or book['formats'].get('text/plain') or book['formats'].get('text/html'),
                            "start": {
                                "text": f"You opening the volume '{book['title']}'. The air smells of digitized parchment. Author: {book['authors'][0]['name'] if book['authors'] else 'Unknown'}.",
                                "choices": [
                                    {"label": "Begin Investigation", "id": "chunk_0"}
                                ]
                            }
                        }
                    _api_cache["data"] = api_stories
                    _api_cache["timestamp"] = current_time
            except Exception:
                if _api_cache["data"]: api_stories = _api_cache["data"]
        
        stories.update(api_stories)
        return stories

    def get_book_chunks(story_id, url):
        if story_id in _api_cache["books_content"]:
            return _api_cache["books_content"][story_id]
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                full_text = response.text[:20000]
                raw_chunks = re.split(r'\r\n\r\n|\n\n', full_text)
                chunks = [c.strip() for c in raw_chunks if len(c.strip()) > 50]
                _api_cache["books_content"][story_id] = chunks
                return chunks
        except Exception: pass
        return []

    # --- ROUTES ---

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        stories = get_stories()
        active_sessions = {s.story_id: s.current_node for s in GameSession.query.filter_by(user_id=current_user.id).all()}
        return render_template('dashboard.html', stories=stories, active_sessions=active_sessions)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
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

    @app.route('/play/<story_id>/<node_id>')
    @login_required
    def play(story_id, node_id):
        all_stories = get_stories()
        story = all_stories.get(story_id)
        if not story:
            return redirect(url_for('dashboard'))

        game_session = GameSession.query.filter_by(user_id=current_user.id, story_id=story_id).first()
        if not game_session:
            game_session = GameSession(user_id=current_user.id, story_id=story_id)
            db.session.add(game_session)
        
        if node_id == "resume":
            node_id = game_session.current_node

        node = None
        if story.get('is_api') and node_id.startswith('chunk_'):
            idx = int(node_id.split('_')[1])
            chunks = get_book_chunks(story_id, story.get('text_url'))
            if idx < len(chunks):
                node = {
                    "text": chunks[idx],
                    "choices": [
                        {"label": "Continue the path", "id": f"chunk_{idx+1}"},
                        {"label": "Branch elsewhere", "id": f"chunk_{min(idx+5, len(chunks)-1)}"}
                    ]
                }
                if idx >= len(chunks) - 1: node["choices"] = []
            else: node_id = "start"

        if not node: node = story.get(node_id)
        if not node:
            node = story.get('start')
            node_id = 'start'

        game_session.current_node = node_id
        history = game_session.get_history()
        if node_id not in history: history.append(node_id)
        game_session.set_history(history)
        db.session.commit()

        if not story.get('is_api'):
            checkout_story_branch(current_user.username, node_id)

        is_ending = len(node.get('choices', [])) == 0

        return render_template('game.html', 
                               node=node, 
                               story_id=story_id, 
                               story_title=story.get('title', 'Unknown Simulation'),
                               history=history[-8:],
                               current_idx=int(node_id.split('_')[1]) if '_' in node_id else 0,
                               is_ending=is_ending)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)