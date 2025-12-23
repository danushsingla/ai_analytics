import os
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import Response
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, EmailStr

# Load .env.local by looking for the file twp directories above
load_dotenv(os.path.join(os.path.dirname(__file__), "../../", ".env.local"))
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
    # Ensure project_id is valid
    if not project_id or project_id in ["undefined", "null"]:
        return {"valid_urls": []}
    
    # Grab the response from Supabase
    response = supabase.table("project_allowlist").select("api_urls").eq("project_id", project_id).execute()

    # Return the list of valid URLs if they exist
    if response.data and "urls" in response.data[0]["api_urls"]:
        return {"valid_urls": response.data[0]["api_urls"]["urls"]}
    else:
        return {"valid_urls": []}
    
class RegisterUserRequest(BaseModel):
    email: EmailStr
    id: str

# When user signs into frontend, add them to the users table in Supabase and generate a unique id if they don't exist
@router.post("/register_user")
async def register_user(body: RegisterUserRequest):
    email = body.email
    id = body.id
    print(id)

    # Check if user already exists
    response = supabase.table("users").select("*").eq("user_id", id).execute()
    if response.data:
        return {"status": "exists", "user_id": response.data[0]["id"]}
    
    # If user does not exist, create a new entry with the email and the user ID
    supabase.table("users").insert({"email": email, "user_id": id}).execute()