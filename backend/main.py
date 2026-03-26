from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.moderation import router as moderation_router

import os

# ==============================
# CREATE APP
# ==============================

app = FastAPI(
    title="Aegis AI Backend",
    description="Multimodal video moderation API",
    version="1.0.0"
)

# ==============================
# CORS CONFIG (IMPORTANT)
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# INCLUDE ROUTES
# ==============================

app.include_router(
    moderation_router,
    prefix="/api"
)

# ==============================
# ROOT ENDPOINT (TEST)
# ==============================

@app.get("/")
def root():
    return {
        "message": "Aegis AI backend is running 🚀"
    }

# ==============================
# ENSURE DIRECTORIES EXIST
# ==============================

os.makedirs("uploads", exist_ok=True)
os.makedirs("temp", exist_ok=True)