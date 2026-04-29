import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.create import router as create_router
from routes.heartbeat import router as heartbeat_router
from routes.parse import router as parse_router

app = FastAPI(title="reminderhub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parse_router)
app.include_router(create_router)
app.include_router(heartbeat_router)
