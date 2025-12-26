import os
import secrets
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
    response = supabase.table("projects").select("api_urls").eq("project_id", project_id).execute()

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

    # Check if user already exists
    response = supabase.table("users").select("*").eq("user_id", id).execute()
    if response.data:
        return {"status": "exists", "user_id": response.data[0]["id"]}
    
    # If user does not exist, create a new entry with the email and the user ID
    supabase.table("users").insert({"email": email, "user_id": id}).execute()

# Helper for /register_domain and /get_domains to grab all domains
def get_domains_helper(user_id):
    # Ensure user_id is valid
    if not user_id or user_id in ["undefined", "null"]:
        return {"domains": []}
    
    # Grab the response from Supabase
    response = supabase.table("projects").select("domain").eq("user_id", user_id).execute()
    print(response)

    # Ensure there is a response
    if not response.data:
        return {"domains": []}
    
    # Grab each domain from each row
    domains = [row["domain"] for row in response.data if row.get("domain")]

    return domains

class RegisterDomainRequest(BaseModel):
    user_id: str
    domain: str

# When a user wishes to register a domain, add it to their allowlist in Supabase
@router.post("/register_domain")
async def register_domain(payload: RegisterDomainRequest):
    user_id = payload.user_id
    domain = payload.domain
    # Ensure user_id is valid
    if not user_id or user_id in ["undefined", "null"]:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    
    # Grab the existing domains from Supabase if it exists
    domains = get_domains_helper(user_id)

    # If the domain is already in the list, do nothing
    if domain in domains:
        return {"status": "exists"}
    
    # Do a while true loop to avoid api key collisions
    while(True):
        # Generate an api key for the new domain
        api_key = "aia_pk_" + secrets.token_urlsafe(16)
        
        # Insert the new domain into the projects table, check if the api key meets a collision
        try:
            supabase.table("projects").insert({"user_id": user_id, "domain": domain, "public_api_key": api_key, "public_api_key_enabled": True}).execute()
            break
        except Exception as e:
            continue
    

class DomainsRequest(BaseModel):
    user_id: str

# When loading user dashboard, grab their domain allowlist from Supabase
@router.post("/get_domains")
async def get_domains(payload: DomainsRequest):
    print("CALLING GET DOMAINS")
    user_id = payload.user_id
    domains = get_domains_helper(user_id)
    return {"domains": domains}