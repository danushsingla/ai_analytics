from fastapi import FastAPI
from app.routes.ingest import router as ingest_router

app = FastAPI()

# Include the router from ingest.py
app.include_router(ingest_router)

# Get endpoint to check if the app is running
@app.get("/")
def root():
    return {"status": "running"}
