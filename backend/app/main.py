import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ingest import router as ingest_router
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .middleware.middleware import AIAnalyticsMiddleware

# Let's have a loop that refreshes every 60 seconds
async def refresh_loop():
    middleware = AIAnalyticsMiddleware()
    while True:
        try:
            await middleware.refresh_allowed_origins_cache_from_supabase()
        except Exception as e:
            print(f"Error refreshing projects: {e}")
        await asyncio.sleep(60)

# To update the allowed origins periodically
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the refresh loop in the background
    task = asyncio.create_task(refresh_loop())
    try:
        yield
    finally:
        task.cancel()

# Load .env.local by looking for the file one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))

app = FastAPI(lifespan=lifespan)

# Include the router from ingest.py
app.include_router(ingest_router)

# Set up CORS middleware to allow requests from any origin
app.add_middleware(
    AIAnalyticsMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("NEXT_PUBLIC_FRONTEND_URL")],    # temporarily adding localhost, will need to figure out a list of allowed origins later
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

# Get endpoint to check if the app is running
@app.get("/")
def root():
    return {"status": "running"}
