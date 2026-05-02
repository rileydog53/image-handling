# ─────────────────────────────────────────────
# main.py — The entry point for the backend server
#
# This file creates the FastAPI app, loads your API key
# from the .env file, sets up security rules (CORS),
# and registers all the URL routes the frontend can call.
# ─────────────────────────────────────────────

import os
from pathlib import Path

from dotenv import load_dotenv

# Load GEMINI_API_KEY from the .env file sitting one folder above this file.
# This keeps your secret key out of the code itself.
load_dotenv(Path(__file__).parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.create import router as create_router
from routes.heartbeat import router as heartbeat_router
from routes.parse import router as parse_router

# Create the FastAPI app — this is the actual web server object.
app = FastAPI(title="reminderhub")

# CORS = Cross-Origin Resource Sharing.
# Browsers block requests between different ports by default.
# This tells the server to allow requests from the Vite dev server
# running on port 5173 (where the React app lives).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # only allow our own frontend
    allow_methods=["*"],                       # allow GET, POST, etc.
    allow_headers=["*"],                       # allow any headers
)

# Register the three route files.
# Each "router" is a mini group of URL endpoints defined elsewhere.
app.include_router(parse_router)      # handles POST /parse
app.include_router(create_router)     # handles POST /create
app.include_router(heartbeat_router)  # handles POST /heartbeat
