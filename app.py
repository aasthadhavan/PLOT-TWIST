import os
import json
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import git

app = Flask(__name__)
app.config['SECRET_KEY'] = 'plottwist_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plottwist.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Git Engine Initialization
REPO_PATH = os.getcwd()
try:
    repo = git.Repo(REPO_PATH)
except:
    repo = git.Repo.init(REPO_PATH)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

login_manager.login_message = 'Please log in to continue.'

login_manager.login_message_category = 'info'




# Git Engine Initialization
REPO_PATH = os.getcwd()
try:
    repo = git.Repo(REPO_PATH)
except:
    repo = git.Repo.init(REPO_PATH)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_story_data():
    # Ensure stories.json is in your root folder
    with open('stories.json', 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid Credentials')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    data = get_story_data()
    # Pulling episodes list from your JSON
    stories = data.get('episodes', [])
    return render_template('dashboard.html', stories=stories)

@app.route('/play/<episode_id>/<node_id>')
@login_required
def play(episode_id, node_id):
    data = get_story_data()
    episode = next((e for e in data['episodes'] if e['id'] == episode_id), None)
    
    if not episode:
        return redirect(url_for('dashboard'))
        
    node = episode['nodes'].get(node_id)

    # SCM LOGIC: Create/Switch to a branch for this specific choice
    branch_name = f"path-{current_user.username}-{node_id}"
    try:
        repo.git.checkout('-b', branch_name)
    except:
        repo.git.checkout(branch_name)

    # FIX: If 'choices' is empty or missing, it's an ending.
    is_ending = not node.get('choices')

    return render_template('game.html', 
                           node=node, 
                           episode_id=episode_id, 
                           is_ending=is_ending)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)


        print("✅ Database initialized")
        print(f"✅ Loaded {len(story_data)} stories: {list(story_data.keys())}")
    app.run(debug=True, port=5000)

    app.run(debug=True)

