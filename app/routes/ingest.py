import os
from fastapi import FastAPI, APIRouter
from supabase import create_client, Client
from dotenv import load_dotenv

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
