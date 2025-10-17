"""
backend/server.py wrapper

This file makes the repository root importable and re-exports the top-level
ASGI `app` defined in `server.py`. It allows running `gunicorn server:app`
from the `backend/` directory (Render Root Directory = backend/).
"""

import os
import sys

# Add repository root (parent of this file) to sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from server import app  # re-export the ASGI app from top-level server.py

__all__ = ["app"]
