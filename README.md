# PLOT-TWIST: The Git-Integrated Story Engine

## 1. Project Title
**PLOT-TWIST** — A DevOps-Enhanced Branching Narrative Experience.

---

## 2. Problem Statement
Many interactive fiction games lack a truly "meta" connection to the developer's world. **PLOT-TWIST** bridges this gap by using Git branches to represent story timelines. The project also addresses professional development standards by implementing a robust CI/CD pipeline, solving the problem of manual deployment and inconsistent environments in collaborative settings.

---

## 3. Architecture Diagram
![PLOT-TWIST Architecture](C:\Users\aasth\.gemini\antigravity\brain\127a9d8c-adff-4329-936f-a3d3f790dcf7\plot_twist_architecture_1775986869004.png)

---

## 4. CI/CD Pipeline Explanation
The project utilizes **GitHub Actions** for an automated 3-stage pipeline:
1.  **Build**: Initializes the Python environment and installs dependencies from `requirements.txt`.
2.  **Test**: Runs automated linting (Flake8) and a "Smoke Test" to verify the Flask app initializes without errors.
3.  **Deploy**: Upon a successful merge to `main` or `feature/devops-enhancement`, the pipeline automatically triggers a production deployment to **Vercel** using the `amondnet/vercel-action`.

---

## 5. Git Workflow Used
We implemented a **Structured Git Workflow**:
- **Main Branch**: Protected production branch.
- **Develop Branch**: Integration branch for team features.
- **Feature Branches**: Individual task branches (e.g., `feature/devops-enhancement`).
- **PR Strategy**: All features require a Pull Request and successful CI pass before merging into `develop` or `main`.

---

## 6. Tools Used
- **Backend**: Flask (Python)
- **Database**: SQLite / SQL-Alchemy
- **Auth**: Flask-Login + Werkzeug Hashing
- **DevOps**: GitHub Actions, Docker, Vercel
- **APIs**: Gutendex (Archive Library)
- **SCM**: GitPython

---

## 7. Screenshots
### Pipeline Success
*(Place screenshot of GitHub Actions green checkmarks here)*

### Deployment Output
*(Place screenshot of the working .vercel.app URL here)*

---

## 8. Challenges Faced
- **Database Schema Migration**: Transitioning from plain-text passwords to `password_hash` required a full database wipe and recreation to prevent `SQLAlchemy` errors.
- **Vercel/Flask Integration**: Configuring Vercel's serverless functions to correctly find the Flask `app` object in a nested directory structure (`api/index.py`).
- **Git State Engine**: Designing a Git engine that doesn't conflict with the CI/CD runners' own Git state.

---

## ⚙️ Project Structure
```text
PLOT-TWIST/
 ├── api/                # Vercel Serverless Entry
 │    └── index.py
 ├── instance/           # Local Database Storage
 ├── templates/          # Light-Mode UI (HTML)
 ├── .github/workflows/  # CI/CD Pipeline (GitHub Actions)
 ├── app.py              # Main Flask Engine
 ├── models.py           # SQL-Alchemy Models
 ├── config.py           # Central Configuration
 ├── vercel.json         # Vercel Deployment Config
 └── README.md           # Documentation
```
