# PLOT-TWIST: The Git-Integrated Story Engine

## 1. Project Title
**PLOT-TWIST** — My DevOps-Enhanced Branching Narrative Experience.

---

## 2. Problem Statement
I realized that many interactive games feel disconnected from the underlying technology. For this project, I wanted to create a "meta" narrative where your choices directly manipulate a Git repository—effectively making the story a part of the development history. I also used this project to solve the challenge of automated deployments in a team setting by implementing a full CI/CD pipeline, ensuring that every update I make is automatically built, tested, and deployed.

---

## 3. Architecture Diagram
![PLOT-TWIST Architecture](C:\Users\aasth\.gemini\antigravity\brain\127a9d8c-adff-4329-936f-a3d3f790dcf7\plot_twist_architecture_1775986869004.png)

---

## 4. CI/CD Pipeline Explanation
I implemented a robust 3-stage pipeline using **GitHub Actions**:
1.  **Build Phase**: I set up a Python 3.10 environment to install all necessary dependencies.
2.  **Test Phase**: I added automated linting with Flake8 to ensure my code quality is high. I also included a "Smoke Test" that initializes the Flask app to catch startup errors before they reach production.
3.  **Deploy Phase**: I configured the pipeline to automatically deploy to **Vercel** whenever I push to the `main` or `feature/devops-enhancement` branches. This ensures the live site is always up-to-date with my latest work.

---

## 5. Git Workflow Used
I followed a professional, structured Git workflow to manage my development:
- **Main Branch**: This is my stable, production-ready code.
- **Develop Branch**: I used this for integrating different features.
- **Feature Branches**: I isolated my DevOps and UI work in a `feature/devops-enhancement` branch.
- **Pull Requests (PRs)**: I made it a rule to use PRs for all major changes, ensuring that the CI pipeline verifies my code before it merges.

---

## 6. Tools Used
- **Backend**: Flask (Python)
- **Database**: SQLite with SQL-Alchemy
- **Security**: Flask-Login and Werkzeug Password Hashing
- **Cloud/DevOps**: GitHub Actions, Vercel, Docker
- **APIs**: Gutendex Public API
- **Version Control**: GitPython

---

## 7. Screenshots
### My Pipeline Success
![Pipeline Success Placeholder](https://github.com/aasthadhavan/PLOT-TWIST/actions/workflows/ci.yml/badge.svg)

### Live Deployment Output
You can access my live simulation here: [PLOT-TWIST on Vercel](https://plot-twist.vercel.app)

---

## 8. Challenges I Faced
- **Password Hashing Transition**: One of my biggest hurdles was migrating from plain-text passwords to secure hashing. I had to carefully recreate the database schema to handle the new `password_hash` field without breaking the app.
- **API Performance**: Connecting to the Gutendex API was initially slowing down my site. I solved this by implementing a **global caching mechanism** in Python that stores API results for 10 minutes, making the dashboard load instantly.
- **Vercel Routing**: Configuring the project to work as a serverless function required a lot of trial and error with the `vercel.json` rewrites and the `api/index.py` handler.

---

## ⚙️ My Project Structure
```text
PLOT-TWIST/
 ├── api/                # My Vercel Serverless Entry
 ├── instance/           # Secure Database Storage
 ├── templates/          # My Redesigned Light-Mode UI
 ├── .github/workflows/  # My Automated DevOps Pipeline
 ├── app.py              # The Core Story Engine
 ├── models.py           # My Data Models
 ├── vercel.json         # My Deployment Logic
 └── README.md           # My Documentation
```
