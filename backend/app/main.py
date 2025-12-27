import os
from fastapi import FastAPI
from app.routes.ingest import router as ingest_router
from dotenv import load_dotenv
from fastapi import FastAPI
from .middleware.cache import lifespan
from fastapi.middleware.cors import CORSMiddleware

# Load .env.local by looking for the file one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))

app = FastAPI(lifespan=lifespan)

# Include the router from ingest.py
app.include_router(ingest_router)

# Set up CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[("*")],    # allow everything, we check with internal cache later for matching api keys
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

# Get endpoint to check if the app is running
@app.get("/")
def root():
    return {"status": "running"}
