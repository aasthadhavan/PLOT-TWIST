# PLOT-TWIST: The Git-Integrated Story Engine

## 1. Project Title
**PLOT-TWIST** — DevOps-Enhanced Branching Narrative Experience.

---

## 2. Problem Statement
We realized that many interactive games feel disconnected from the underlying technology. For this project, we wanted to create a "meta" narrative where your choices directly manipulate a Git repository—effectively making the story a part of the development history. Our team also used this project to solve the challenge of automated deployments in a team setting by implementing a full CI/CD pipeline, ensuring that every update I make is automatically built, tested, and deployed.

---

## 3. Architecture Diagram
<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/ec81230b-7356-418e-be14-980fa65fdb7f" />


---

## 4. CI/CD Pipeline Explanation
I implemented a robust 3-stage pipeline using **GitHub Actions**:
1.  **Build Phase**: We set up a Python 3.10 environment to install all necessary dependencies.
2.  **Test Phase**: We added automated linting with Flake8 to ensure my code quality is high &  also included a "Smoke Test" that initializes the Flask app to catch startup errors before they reach production.
3.  **Deploy Phase**: We configured the pipeline to automatically deploy to **Vercel** whenever we push to the `main` or `feature/devops-enhancement` branches. This ensures the live site is always up-to-date with my latest work.

---

## 5. Git Workflow Used
The team followed a professional, structured Git workflow to manage development:
- **Main Branch**: This is our stable, production-ready code.
- **Develop Branch**: Used this for integrating different features.
- **Feature Branches**: Isolated our DevOps work in a `feature/devops-enhancement` branch.
- **Pull Requests (PRs)**: Made it a rule to use PRs for all major changes, ensuring that the CI pipeline verifies my code before it merges.

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
### Pipeline Success
![Pipeline Success Placeholder](https://github.com/aasthadhavan/PLOT-TWIST/actions/workflows/ci.yml/badge.svg)

### Live Deployment Output
You can access the live simulation

---

## 8. Challenges We Faced
- **Password Hashing Transition**: One of the biggest hurdles was migrating from plain-text passwords to secure hashing, had to carefully recreate the database schema to handle the new `password_hash` field without breaking the app.
- **API Performance**: Connecting to the Gutendex API was initially slowing down the site, solved this by implementing a **global caching mechanism** in Python that stores API results for 10 minutes, making the dashboard load instantly.
- **Vercel Routing**: Configuring the project to work as a serverless function required a lot of trial and error with the `vercel.json` rewrites and the `api/index.py` handler.

---

## ⚙️ Project Structure
```text
PLOT-TWIST/
 ├── api/                # Vercel Serverless Entry
 ├── instance/           # Secure Database Storage
 ├── templates/          # Redesigned Light-Mode UI
 ├── .github/workflows/  # Automated DevOps Pipeline
 ├── app.py              # The Core Story Engine
 ├── models.py           # Data Models
 ├── vercel.json         # Deployment Logic
 └── README.md           # Documentation
```
