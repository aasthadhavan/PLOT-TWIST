import json, os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from git import Repo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'plottwist_2026_devops'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plottwist.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to continue.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load story data
try:
    with open("stories.json") as f:
        story_data = json.load(f)
except FileNotFoundError:
    story_data = {}

# Git repo management
def get_user_repo(username):
    """Create and manage per-user Git repository for story tracking"""
    repo_path = f'./game_saves/{username}'
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
        repo = Repo.init(repo_path)
        with open(os.path.join(repo_path, 'progress.txt'), 'w') as f:
            f.write("Game Progress Log\n=================\n")
        repo.index.add(['progress.txt'])
        repo.index.commit("Initial commit - game started")
    return Repo(repo_path)

# ============== ROUTES ==============

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password required', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        try:
            hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            
            # Initialize user repo
            get_user_repo(username)
            
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.update_last_login()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", stories=story_data, current_user=current_user)

@app.route("/play/<story_id>", methods=["GET", "POST"])
@login_required
def play(story_id):
    """Story gameplay with Git branching and choice tracking"""
    if story_id not in story_data:
        flash(f'Story "{story_id}" not found', 'error')
        return redirect(url_for('dashboard'))
    
    repo = get_user_repo(current_user.username)
    story = story_data[story_id]
    
    # Handle choice submission
    if request.method == "POST":
        choice_id = request.form.get("choice")
        
        if choice_id:
            # Create or checkout branch for this choice
            branch_name = f"{story_id}_{choice_id}"
            if branch_name not in [h.name for h in repo.heads]:
                new_branch = repo.create_head(branch_name)
                new_branch.checkout()
            else:
                repo.git.checkout(branch_name)
            
            # Log the choice
            with open(os.path.join(repo.working_dir, 'progress.txt'), 'a') as f:
                f.write(f"Story: {story_id}, Choice: {choice_id}\n")
            
            repo.index.add(['progress.txt'])
            repo.index.commit(f"Choice: {choice_id} in {story_id}")
            
            current_branch = choice_id
        else:
            current_branch = repo.active_branch.name
    else:
        current_branch = repo.active_branch.name
    
    # Get current node
    current_node = story.get('start', {})
    
    # Navigate through choices to find current node
    # (In a real app, you'd track this in the database)
    if current_branch != 'master' and current_branch != 'main':
        # Try to find the node matching the branch name
        for node_id, node_data in story.items():
            if node_id == current_branch:
                current_node = node_data
                break
    
    discovered_paths = len([h.name for h in repo.heads if h.name != 'master' and h.name != 'main'])
    
    return render_template(
        "game.html",
        story_title=story.get('title', 'Untitled'),
        node=current_node,
        story_id=story_id,
        discovered_paths=discovered_paths,
        current_user=current_user
    )

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# ============== INITIALIZATION ==============

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)