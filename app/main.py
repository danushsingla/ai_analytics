from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ingest import router as ingest_router

app = FastAPI()

# Include the router from ingest.py
app.include_router(ingest_router)

# Set up CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
)

# Get endpoint to check if the app is running
@app.get("/")
def root():
    return {"status": "running"}
