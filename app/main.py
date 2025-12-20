from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ingest import router as ingest_router

app = FastAPI()

# Include the router from ingest.py
app.include_router(ingest_router)

# Set up CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],    # temporarily adding localhost, will need to figure out a list of allowed origins later
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

# Get endpoint to check if the app is running
@app.get("/")
def root():
    return {"status": "running"}
