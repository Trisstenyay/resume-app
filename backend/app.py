# Flask = the tiny web framework that runs our API server and routes (e.g., /health)
# jsonify = helper to return proper JSON responses (sets content-type etc.)
from flask import Flask, jsonify, request

# CORS = lets a browser app on a different origin/port (our React frontend) call this API in dev
from flask_cors import CORS

# SQLAlchemy = ORM (object–relational mapper) so we define Python classes (User, Job, Resume)
# instead of writing raw SQL for every query. It manages the connection pool to Postgres too.
from flask_sqlalchemy import SQLAlchemy

# JWTManager = handles issuing and validating JSON Web Tokens for login-protected endpoints
from flask_jwt_extended import JWTManager

# os = lets us read environment variables (DATABASE_URL, JWT_SECRET_KEY, etc.)
import os

# load_dotenv = reads key=value pairs from .env and puts them into the process environment
# IMPORTANT: call load_dotenv() BEFORE you read os.environ anywhere (e.g., in app config).
from dotenv import load_dotenv
load_dotenv()  # <-- loads backend/.env so the config below can see DATABASE_URL / JWT_SECRET_KEY

# These are singletons the app will use. We "bind" them to the Flask app in create_app().
db = SQLAlchemy()
jwt = JWTManager()



# ----- Job parsing & matching helpers (module-level) -----

KNOWN_SKILLS = {
    "javascript", "react", "html", "css", "python", "flask", "sql",
    "postgres", "postgresql", "git", "rest", "apis", "api",
    "docker", "aws", "vite", "redux", "typescript"
}

def extract_skills_from_text(text: str):
    words = {w.strip(".,():;").lower() for w in text.split()}
    found = sorted(s for s in KNOWN_SKILLS if s in words)
    return found


def create_app():
    """Application factory — creates and configures the Flask app instance."""
    app = Flask(__name__)
    CORS(app)  # allow frontend -> backend requests during development

    # ── Config ──────────────────────────────────────────────────────────────────
    # DB URL comes from env; default to SQLite so local dev works WITHOUT Postgres.
    # (You can change the default back to 'postgresql:///resume_app_dev' if you prefer.)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql:///resume_app_dev") # local DB name if .env missing
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret")

    db.init_app(app) # attach SQLAlchemy to this Flask app
    jwt.init_app(app) # attach JWT manager to this app





    # ── ROUTES ──────────────────────────────────────────────────────────────────
    
    @app.get("/")
    def index():
        """
        GET /
        Simple sanity check route. Useful to see if the server is up at all.
        Returns: {"message": "Resume API is running"} with HTTP 200.
        """
        return jsonify({"message": "Resume API is running"})
   
    
    @app.get("/api/resume")
    def get_resume():
        """
        GET /api/resume
        Returns the current resume data as JSON.
        For now this is static sample data; later we’ll load/save it from the DB.
        """
        resume = {
            "contact": {
                "fullName": "Tristan Tenyay",
                "role": "Full-Stack Developer",
                "email": "you@example.com",
                "phone": "(555) 123-4567",
                "location": "NYC, NY",
                "website": "https://www.tristantenyay.com",
                "github": "https://github.com/Trisstenyay",
                "linkedin": "https://www.linkedin.com/in/yourhandle/"
            },
            "summary": "Detail-oriented developer with JS/React & Python/Flask experience.",
            "skills": ["JavaScript", "React", "HTML", "CSS", "Python", "Flask", "SQL", "Git", "REST APIs"],
            "experience": [{
                "id": "exp-1",
                "title": "Front-End Developer",
                "company": "Example Co.",
                "location": "Remote",
                "start": "2024",
                "end": "Current",
                "bullets": [
                    "Built responsive UI components in React.",
                    "Integrated REST APIs and managed app state."
                ]
            }],
            "education": [{
                "id": "edu-1",
                "school": "Springboard (Bootcamp)",
                "credential": "Software Engineering",
                "dates": "2024–2025",
                "details": ["Full-stack web development."]
            }],
            "projects": [{
                "id": "proj-1",
                "name": "Full-Stack Resume App",
                "link": "https://www.tristantenyay.com",
                "tech": "Flask, SQLAlchemy, TMDB API, Bootstrap",
                "bullets": ["Deployed on Render with PostgreSQL."]
            }]
        }
        return jsonify(resume), 200
    
    
    @app.post("/api/job/parse")
    def parse_job():
        data = request.get_json(force=True)
        jd_text = data.get("text", "")
        skills = extract_skills_from_text(jd_text)
        return jsonify({"skills": skills})
    
    @app.post("/api/match")
    def match_resume_to_job():
        body = request.get_json(force=True)
        resume = body.get("resume", {})
        jd_skills = [s.lower() for s in body.get("jdSkills", [])]

        resume_skills = set([s.lower() for s in resume.get("skills", [])])

        bullets_texts = []
        for exp in resume.get("experience", []):
            for b in exp.get("bullets", []):
                bullets_texts.append(b.lower())

        matched = []
        for s in jd_skills:
            if s in resume_skills:
                matched.append(s)
                continue
            if any(s in bt for bt in bullets_texts):
                matched.append(s)

        missing = [s for s in jd_skills if s not in matched]
        score = int(round(100 * (len(matched) / max(1, len(jd_skills)))))

        scored_bullets = []
        for bt in bullets_texts:
            hits = [s for s in matched if s in bt]
            if hits:
                scored_bullets.append({"text": bt, "reason": f"mentions: {', '.join(hits)}"})

        scored_bullets.sort(key=lambda x: len(x["reason"].split(",")), reverse=True)
        top = scored_bullets[:5]

        return jsonify({
            "score": score,
            "coverage": {"matched": matched, "missing": missing},
            "topBullets": top
        })
    return app



app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # no models yet; just ensures DB connection works
    app.run(debug=True)


