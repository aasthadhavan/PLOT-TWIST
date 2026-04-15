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

    # Ensure DB schema is ready (Safe for both local and Vercel /tmp)
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- SCM ENGINE (CI/CD READY) ---
    def get_repo():
        try:
            return git.Repo(app.root_path, search_parent_directories=True)
        except Exception:
            return None

    def checkout_story_branch(username, node_id):
        repo = get_repo()
        if not repo: return # Graceful fallback for read-only / serverless

        # Sanitization for CI/CD safety
        clean_user = re.sub(r'[^a-zA-Z0-9_-]', '_', username)
        clean_node = re.sub(r'[^a-zA-Z0-9_-]', '_', node_id)
        branch_name = f"{app.config.get('GIT_STORY_NAMESPACE', 'story/')}{clean_user}-{clean_node}"
        
        try:
            if branch_name in [b.name for b in repo.branches]:
                repo.git.checkout(branch_name)
            else:
                repo.git.checkout('-b', branch_name)
        except Exception as e:
            app.logger.warning(f"Git Engine: Non-fatal transition error: {e}")

    # --- API GLOBAL CACHE ---
    _api_cache = {
        "stories": None,
        "expires_at": 0,
        "books_db": {}
    }
    CACHE_EXPIRY = 3600 # 1 Hour

    # --- STORY ARCHIVE ENGINE ---
    def get_stories():
        # Load local archives with absolute pathing for Vercel
        local_path = os.path.join(app.root_path, 'stories.json')
        try:
            with open(local_path, 'r') as f:
                stories = json.load(f)
        except Exception:
            stories = {}

        # Handle Gutendex API Caching
        now = time.time()
        if _api_cache["stories"] and now < _api_cache["expires_at"]:
            api_data = _api_cache["stories"]
        else:
            api_data = {}
            GUTEN_URL = "https://gutendex.com/books/?topic=mystery"
            try:
                r = requests.get(GUTEN_URL, timeout=9)
                if r.status_code == 200:
                    results = r.json().get('results', [])[:12]
                    for book in results:
                        sid = f"api_{book['id']}"
                        api_data[sid] = {
                            "title": book['title'],
                            "is_api": True,
                            "author": book['authors'][0]['name'] if book['authors'] else "Anonymous",
                            "text_url": book['formats'].get('text/plain; charset=utf-8') or book['formats'].get('text/plain'),
                            "start": {
                                "text": f"Initializing Archive Access: '{book['title']}'. Analysis suggests author origin: {book['authors'][0]['name'] if book['authors'] else 'Unknown'}.",
                                "choices": [{"label": "Synchronize Timeline", "id": "chunk_0"}]
                            }
                        }
                    _api_cache["stories"] = api_data
                    _api_cache["expires_at"] = now + CACHE_EXPIRY
                else:
                    raise Exception("API Status Error")
            except Exception:
                # Optimized Fallback for Demo Reliability
                api_data = {
                    "api_fallback_1": {
                        "title": "The Adventures of Sherlock Holmes",
                        "is_api": True,
                        "author": "Arthur Conan Doyle",
                        "text_url": "https://www.gutenberg.org/files/1661/1661-0.txt",
                        "start": {"text": "Accessing Archive: Sherlock Holmes. A consulting detective at 221B Baker Street.", "choices": [{"label": "Begin Investigation", "id": "chunk_0"}]}
                    },
                    "api_fallback_2": {
                        "title": "Dracula",
                        "is_api": True,
                        "author": "Bram Stoker",
                        "text_url": "https://www.gutenberg.org/files/345/345-0.txt",
                        "start": {"text": "Accessing Archive: Dracula. A journey into the Carpathian Mountains.", "choices": [{"label": "Accept Invitation", "id": "chunk_0"}]}
                    },
                    "api_fallback_3": {
                        "title": "The War of the Worlds",
                        "is_api": True,
                        "author": "H. G. Wells",
                        "text_url": "https://www.gutenberg.org/files/36/36-0.txt",
                        "start": {"text": "Accessing Archive: Martian Invasion. The cylinder pulsates on the heath.", "choices": [{"label": "Observe Crater", "id": "chunk_0"}]}
                    }
                }
                _api_cache["stories"] = api_data
                _api_cache["expires_at"] = now + 300 # Retry in 5 mins

        stories.update(api_data)
        return stories

    def fetch_book_chunks(story_id, url):
        if story_id in _api_cache["books_db"]:
            return _api_cache["books_db"][story_id]
        
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                full_text = r.text[:30000]
                raw = re.split(r'\n\s*\n', full_text)
                chunks = [c.strip() for c in raw if len(c.strip()) > 80]
                _api_cache["books_db"][story_id] = chunks
                return chunks
        except Exception: pass
        return ["Archive corrupted or inaccessible. Reconnecting..."]

    # --- ROUTES ---

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('landing.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        stories = get_stories()
        # Resume Tracking
        sessions = GameSession.query.filter_by(user_id=current_user.id).all()
        active_ids = {s.story_id: s.current_node for s in sessions}
        return render_template('dashboard.html', stories=stories, active_sessions=active_ids)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated: return redirect(url_for('dashboard'))
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                user.update_last_login()
                return redirect(url_for('dashboard'))
            flash('Unauthorized access: Invalid credentials.', 'error')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Invalid neural-link address format.', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
                flash('Identity already indexed in the registry.', 'error')
                return redirect(url_for('register'))
            
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Identity confirmed. You may now authenticate.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/play/<story_id>/<node_id>')
    @login_required
    def play(story_id, node_id):
        stories = get_stories()
        story = stories.get(story_id)
        if not story: return redirect(url_for('dashboard'))

        # Session persistence logic
        sess = GameSession.query.filter_by(user_id=current_user.id, story_id=story_id).first()
        if not sess:
            sess = GameSession(user_id=current_user.id, story_id=story_id)
            db.session.add(sess)
        
        if node_id == "resume": node_id = sess.current_node
        
        node = None
        if story.get('is_api') and node_id.startswith('chunk_'):
            idx = int(node_id.split('_')[1])
            chunks = fetch_book_chunks(story_id, story.get('text_url'))
            if idx < len(chunks):
                node = {
                    "text": chunks[idx],
                    "choices": [
                        {"label": "Maintain Sequence", "id": f"chunk_{idx+1}"},
                        {"label": "Alternate Branch", "id": f"chunk_{min(idx+3, len(chunks)-1)}"}
                    ]
                }
                if idx >= len(chunks) - 1: node["choices"] = []
            else: node_id = "start"

        if not node: node = story.get(node_id) or story.get('start')

        # Update History & State
        sess.current_node = node_id
        hist = sess.get_history()
        if node_id not in hist: hist.append(node_id)
        sess.set_history(hist)
        db.session.commit()

        # Git Engine Bridge
        if not story.get('is_api'):
            checkout_story_branch(current_user.username, node_id)

        # Robust index parsing for progress bar
        parts = node_id.split('_')
        current_idx = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0

        return render_template('game.html', 
                               node=node,
                               story_id=story_id,
                               story_title=story['title'],
                               current_idx=current_idx,
                               history=hist[-8:],
                               is_ending=len(node.get('choices', [])) == 0)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)