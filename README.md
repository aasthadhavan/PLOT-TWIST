# PLOT-TWIST — Branching Story Engine

PLOT-TWIST is an interactive story game where your choices don't just affect the narrative—they affect the repository itself. Built with Flask and Git integration, it's a "meta" gaming experience for developers.

## 👥 Meet the Team
- **Aastha Dhavan**: Lead Developer & SDLC Manager
- **Taniya Bisht**: UI/UX Designer & Frontend Engineer
- **Janvi**: Database Architect & Backend Logic

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- Git installed on your system

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/aasthadhavan/PLOT-TWIST.git
cd PLOT-TWIST

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize your environment
cp .env.example .env
# Edit .env and add a secret key
```

### 3. Running the Game
```bash
python app.py
```
Visit `http://127.0.0.1:5000` to start your journey.

---

## 🛠 Collaboration Guidelines

To keep our repository healthy between 3 teammates, please follow this workflow:

1.  **Main Branch**: `develop` (Always merge feature branches here).
2.  **Feature Branches**: Create branches like `feature/your-feature-name`.
3.  **Conflict Resolution**: Use `git fetch` and `git rebase develop` before submitting a Pull Request.
4.  **Story Branches**: Note that the game engine creates branches in the `story/` namespace. These are for gameplay state and should NOT be merged into `develop`.

---

## 🏗 Architecture
- **Backend**: Flask
- **Database**: SQLite (via Flask-SQLAlchemy)
- **Auth**: Flask-Login with password hashing
- **SCM Engine**: GitPython (Story branching logic)
- **Public API**: Gutendex (Internal library archive)

---

## 📝 Roadmap
- [ ] Add more local branching stories to `stories.json`.
- [ ] Implement a global leaderboard.
- [ ] Connect to PostgreSQL for shared team testing.
