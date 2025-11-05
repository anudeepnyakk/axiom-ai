"""
Axiom AI - Streamlit App Entry Point for HuggingFace Spaces

HuggingFace Spaces expects streamlit_app.py when using Streamlit template.
This file imports our frontend-only app_hf.py which calls the backend API.
"""

import sys
from pathlib import Path

# Add frontend directory to path so imports work
frontend_dir = Path(__file__).parent / "frontend"
sys.path.insert(0, str(frontend_dir))
sys.path.insert(0, str(Path(__file__).parent))

# Import frontend-only app (which calls backend API)
from app_hf import *

