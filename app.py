import json, os
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'plottwist_2026_devops_secret_key_xyz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plottwist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_DURATION'] = 86400  # 1 day

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to continue.'

login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load story data
try:
    with open("stories.json") as f:
        story_data = json.load(f)
except FileNotFoundError:
    story_data = {}

# Git repo management (optional - graceful fallback if git not available)
def get_user_repo(username):
    repo_path = f'./game_saves/{username}'
    try:
        from git import Repo, InvalidGitRepositoryError
        if not os.path.exists(repo_path):
            os.makedirs(repo_path, exist_ok=True)
            repo = Repo.init(repo_path)
            progress_file = os.path.join(repo_path, 'progress.txt')
            with open(progress_file, 'w') as f:
                f.write("Game Progress Log\n=================\n")
            repo.index.add(['progress.txt'])
            repo.index.commit("Initial commit - game started")
        return Repo(repo_path)
    except Exception:
        os.makedirs(repo_path, exist_ok=True)
        return None

def log_choice(username, story_id, choice_id):
    """Log choice to file, with optional git commit"""
    repo_path = f'./game_saves/{username}'
    os.makedirs(repo_path, exist_ok=True)
    progress_file = os.path.join(repo_path, 'progress.txt')
    with open(progress_file, 'a') as f:
        f.write(f"Story: {story_id}, Choice: {choice_id}\n")
    try:
        from git import Repo
        repo = Repo(repo_path)
        branch_name = f"{story_id}_{choice_id}"[:50]
        try:
            if branch_name not in [h.name for h in repo.heads]:
                repo.create_head(branch_name).checkout()
            else:
                repo.git.checkout(branch_name)
        except Exception:
            pass
        repo.index.add(['progress.txt'])
        repo.index.commit(f"Choice: {choice_id} in {story_id}")
    except Exception:
        pass  # Git is optional

# ============== ROUTES ==============

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken. Try another.', 'error')
            return render_template('register.html')

        try:
            hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            get_user_repo(username)
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration error: {str(e)}', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not username or not password:
            flash('Please enter username and password.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            user.update_last_login()
            # Redirect to 'next' page if set, else dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', stories=story_data, current_user=current_user)

@app.route('/play/<story_id>', methods=['GET', 'POST'])
@login_required
def play(story_id):
    if story_id not in story_data:
        flash(f'Story "{story_id}" not found.', 'error')
        return redirect(url_for('dashboard'))

    story = story_data[story_id]

    if request.method == 'POST':
        choice_id = request.form.get('choice')
        if choice_id:
            # Store current node in session
            session[f'node_{story_id}'] = choice_id
            log_choice(current_user.username, story_id, choice_id)
            return redirect(url_for('play', story_id=story_id))
        return redirect(url_for('play', story_id=story_id))

    # GET: determine which node to show
    current_node_id = session.get(f'node_{story_id}', 'start')

    # Navigate to correct node
    current_node = story.get(current_node_id, story.get('start', {}))
    if not current_node:
        current_node = story.get('start', {})

    # Count discovered paths from session
    discovered_paths = sum(1 for k in session if k.startswith(f'node_'))

    # Calculate a rough progress %
    total_nodes = len([k for k in story.keys() if k not in ('title', 'emoji', 'genre', 'description', 'atmosphere')])
    progress = min(int((discovered_paths / max(total_nodes, 1)) * 100), 95)

    return render_template(
        'game.html',
        story_title=story.get('title', 'Untitled'),
        node=current_node,
        story_id=story_id,
        discovered_paths=discovered_paths,
        progress=progress,
        current_user=current_user
    )

@app.route('/restart/<story_id>')
@login_required
def restart(story_id):
    session.pop(f'node_{story_id}', None)
    return redirect(url_for('play', story_id=story_id))

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(error):
    return render_template('login.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('login.html'), 500

# ============== INIT ==============

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")
        print(f"✅ Loaded {len(story_data)} stories: {list(story_data.keys())}")
    app.run(debug=True, port=5000)