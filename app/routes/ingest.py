import os
from fastapi import FastAPI, APIRouter
from fastapi.responses import Response
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Load .env.local by looking for the file one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))
supabase_url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

# Create a Supabase client with the url and service key
supabase: Client = create_client(supabase_url, key)

# Create a FastAPI router to help grab endpoints (like /collect)
router = APIRouter()

# Whenever someone writes POST to /collect then this happens
@router.post("/collect")
# Parses the JSON body and turns it into a Python dictionary
async def collect_event(event: dict):
    # Create a table in supabase called "events" and insert the event data
    response = supabase.table("events").insert(event).execute()
    return {"status": "ok", "data": response.data}

# Set the path of the tracker.js file which holds my HTML code
TRACKER_PATH = Path(__file__).parent / "tracker.js"

# Sends the GTM tag so it can easily be managed locally
@router.get("/gtmtracker.js")
async def gtmtracker():
    with open(TRACKER_PATH, "r", encoding="utf-8") as f:
        tracker_js = f.read()
    return Response(
        content=tracker_js,
        media_type="application/javascript",
        headers={
            "Cache-Control": "no-store, max-age=0"
        }
    )

# Access Supabase to return a list of api urls the client chose
@router.get("/config")
async def get_config(project_id: str):
    response = supabase.table("project_allowlist").select("api_urls").eq("project_id", project_id).execute()
    if response.data and "urls" in response.data["api_urls"]:
        return {"valid_urls": response.data["api_urls"]["urls"]}
    else:
        return {"valid_urls": []}
