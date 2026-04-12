import os
import sys

# Add the project root to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

# Vercel needs the 'app' variable to be the handler
handler = app
