import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ingest import router as ingest_router
from dotenv import load_dotenv

# Load .env.local by looking for the file one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))

app = FastAPI()

# Include the router from ingest.py
app.include_router(ingest_router)

# Set up CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("NEXT_PUBLIC_FRONTEND_URL"), "https://aianalyticstestapp.vercel.app"],    # temporarily adding localhost, will need to figure out a list of allowed origins later
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

# Get endpoint to check if the app is running
@app.get("/")
def root():
    return {"status": "running"}
