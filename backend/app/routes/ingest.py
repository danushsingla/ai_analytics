import os
import secrets
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, EmailStr
from ..middleware.cache import ALLOWED_CACHE

# Load .env.local by looking for the file two directories above
load_dotenv(os.path.join(os.path.dirname(__file__), "../../", ".env.local"))
supabase_url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

# Create a Supabase client with the url and service key
supabase: Client = create_client(supabase_url, key)

# Create a FastAPI router to help grab endpoints (like /collect)
router = APIRouter()

# Helper to confirm api key is valid
def verify_public_api_key(public_api_key: str):
    # Ensure public_api_key is valid
    if not public_api_key or public_api_key in ["undefined", "null"]:
        raise HTTPException(status_code=400, detail="Invalid public_api_key")
    
    # Check the cache to see if the api key is enabled
    if public_api_key in ALLOWED_CACHE and ALLOWED_CACHE[public_api_key]["public_api_key_enabled"]:
            return True
    return False

# Whenever someone writes POST to /collect then this happens
@router.post("/collect")
# Parses the JSON body and turns it into a Python dictionary
async def collect_event(event: dict, public_api_key: str):
    # Verify the public api key
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
    
    # Add the public_api_key to the event data
    event["project_api_key"] = public_api_key
    
    # Insert the event data
    response = supabase.table("events").insert(event).execute()

    ''' After inserting the data, calculate latency between request and response time and populate the latency_events table '''

    # First, we will only send latency_event if the event type is 'api_response'
    if event.get("event_type") == "ai_response":
        # Now, let's get the request timestamp from supabase that has the corresponding request_id
        request_id = event.get("request_id")
        request_response = supabase.table("events").select("created_at").eq("request_id", request_id).eq("event_type", "ai_request").execute()
        if request_response.data and len(request_response.data) > 0:
            request_ts = request_response.data[0]["created_at"]
            response_ts = event.get("timestamp")
        
        latency_event = {
            "project_api_key": public_api_key,
            "endpoint": event.get("payload")["url"],
            "request_ts": request_ts,
            "response_ts": response_ts,
            "latency_ms": (response_ts - request_ts) * 1000  # Convert to milliseconds
        }

        # Insert the latency event into the latency_events table
        supabase.table("latency_events").insert(latency_event).execute()
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
async def config(public_api_key: str):
    # Ensure project_id is valid
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
    
    # Grab the response from Supabase
    response_all = supabase.table("project_api_urls").select("all_api_urls").eq("project_api_key", public_api_key).execute()
    response_valid = supabase.table("project_api_urls").select("valid_api_urls").eq("project_api_key", public_api_key).execute()

    # Return the list of valid and all URLs if they exist
    if response_all.data and response_all.data[0]["all_api_urls"] and "urls" in response_all.data[0]["all_api_urls"] \
    and response_valid.data and response_valid.data[0]["valid_api_urls"] and "urls" in response_valid.data[0]["valid_api_urls"]:
        return {"valid_urls": response_valid.data[0]["valid_api_urls"]["urls"], "all_urls": response_all.data[0]["all_api_urls"]["urls"]}
    else:
        return {"valid_urls": [], "all_urls": []}
    
# Update all api urls for the project if a new one is seen
@router.post("/update_api_urls")
async def update_api_urls(public_api_key: str, new_url: str):
    # Ensure project_id is valid
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
    
    # Grab the existing api urls from Supabase
    response = supabase.table("project_api_urls").select("all_api_urls").eq("project_api_key", public_api_key).execute()

    all_urls = []
    if response.data and response.data[0]["all_api_urls"] and "urls" in response.data[0]["all_api_urls"]:
        all_urls = response.data[0]["all_api_urls"]["urls"]
    
    # If the new url is not in the list, add it
    if new_url not in all_urls:
        all_urls.append(new_url)
        # Update the row in Supabase
        supabase.table("project_api_urls").update({"all_api_urls": {"urls": all_urls}}).eq("project_api_key", public_api_key).execute()
    
    return {"all_urls": all_urls}
    
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
        return {"domains": [], "api_keys": []}
    
    # Grab the response from Supabase for domains
    response_domains = supabase.table("projects").select("domain").eq("user_id", user_id).execute()

    # Ensure there is a response
    if not response_domains.data:
        return {"domains": [], "api_keys": []}
    
    # Grab each domain from each row
    domains = [row["domain"] for row in response_domains.data if row.get("domain")]

    # Grab the response from Supabase for api keys
    response = supabase.table("projects").select("public_api_key").eq("user_id", user_id).execute()

    # Ensure there is a response
    if not response.data:
        return {"domains": domains, "api_keys": []}
    
    # Grab each api key from each row
    api_keys = [row["public_api_key"] for row in response.data if row.get("public_api_key")]

    return domains, api_keys

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
    domains, api_keys = get_domains_helper(user_id)

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

    # When a project is officially registered, I need to update the project_api_urls table to have an entry for this api key
    supabase.table("project_api_urls").insert({"project_api_key": api_key, "all_api_urls": {"urls": []}, "valid_api_urls": {"urls": []}}).execute()
    

class DomainsRequest(BaseModel):
    user_id: str

# When loading user dashboard, grab their domain allowlist from Supabase
@router.post("/get_domains")
async def get_domains(payload: DomainsRequest):
    user_id = payload.user_id
    domains, api_keys = get_domains_helper(user_id)
    return {"domains": domains, "api_keys": api_keys}

# When loading user dashboard, grab all of their api urls from Supabase
@router.get("/get_api_urls")
async def get_api_urls(public_api_key: str):
    # Ensure project_id is valid
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
        
    # Grab the response from Supabase
    response = supabase.table("project_api_urls").select("all_api_urls", "valid_api_urls").eq("project_api_key", public_api_key).execute()

    # Return the list of valid and all URLs if they exist
    if response.data and response.data[0]["all_api_urls"] and "urls" in response.data[0]["all_api_urls"] and "urls" in response.data[0]["valid_api_urls"]:
        return {"valid_urls": response.data[0]["valid_api_urls"]["urls"], "all_urls": response.data[0]["all_api_urls"]["urls"]}

class UpdateValidURLsRequest(BaseModel):
    public_api_key: str
    url: str

# When a checkbox is ticked, add the url to the valid list
@router.post("/add_valid_api_url")
async def add_valid_url(payload: UpdateValidURLsRequest):
    public_api_key = payload.public_api_key
    url = payload.url

    # Ensure project_id is valid
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
    
    # Grab the existing valid api urls from Supabase
    response = supabase.table("project_api_urls").select("valid_api_urls").eq("project_api_key", public_api_key).execute()

    valid_urls = []
    if response.data and response.data[0]["valid_api_urls"] and "urls" in response.data[0]["valid_api_urls"]:
        valid_urls = response.data[0]["valid_api_urls"]["urls"]
    
    # If the url is not in the list, add it
    if url not in valid_urls:
        valid_urls.append(url)
        # Update the row in Supabase
        supabase.table("project_api_urls").update({"valid_api_urls": {"urls": valid_urls}}).eq("project_api_key", public_api_key).execute()

# When a checkbox is unticked, remove the url from the valid list
@router.post("/remove_valid_api_url")
async def remove_valid_url(payload: UpdateValidURLsRequest):
    public_api_key = payload.public_api_key
    url = payload.url

    # Ensure project_id is valid
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
    
    # Grab the existing valid api urls from Supabase
    response = supabase.table("project_api_urls").select("valid_api_urls").eq("project_api_key", public_api_key).execute()

    valid_urls = []
    if response.data and response.data[0]["valid_api_urls"] and "urls" in response.data[0]["valid_api_urls"]:
        valid_urls = response.data[0]["valid_api_urls"]["urls"]
    
    # If the url is in the list, remove it
    if url in valid_urls:
        valid_urls.remove(url)
        # Update the row in Supabase
        supabase.table("project_api_urls").update({"valid_api_urls": {"urls": valid_urls}}).eq("project_api_key", public_api_key).execute()