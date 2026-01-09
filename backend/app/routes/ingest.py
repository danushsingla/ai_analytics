import os
import secrets
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, EmailStr
from typing import List
from ..middleware.cache import ALLOWED_CACHE
from .analysis import calculate_latency
from ..middleware.cache import refresh_allowed_origins_cache_from_supabase

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
    if public_api_key in ALLOWED_CACHE:
            return True
    return False

# Helper to get data based on path and body
def parse_by_path(path: str, body: dict):
    for part in path.replace("]", "").split("."):
        if "[" in part:
            key, index = part.split("[")
            # For when this is a dictionary
            body = body.get(key) if isinstance(body, dict) else None
            # For when this is a list
            index = int(index)
            body = body[index] if isinstance(body, list) and index < len(body) else None
        else:
            # For when this is a regular . access
            body = body.get(part) if isinstance(body, dict) else None
        
        if body is None:
            return None
    return body


# Helper to get extracted text from body/url based on schema stored in supabase
def get_text(public_api_key: str, url: str, body: str, alias: str):
    # Get schema from Supabase
    response = supabase.table("project_api_urls").select("message_paths").eq("project_api_key", public_api_key).execute()

    # Get the message paths for this alias and endpint
    ai = response.data[0]["message_paths"].get(url)[1] if response.data and response.data[0]["message_paths"] and response.data[0]["message_paths"].get(url) else ""
    user = response.data[0]["message_paths"].get(url)[0] if response.data and response.data[0]["message_paths"] and response.data[0]["message_paths"].get(url) else ""

    # Depending on whether this is an ai_response or user_request, extract the text accordingly
    if alias == "ai_response" and ai:
        return parse_by_path(ai, body)
    elif alias == "user_request" and user:
        return parse_by_path(user, body)
    else:
        return None


# Whenever someone writes POST to /collect then this happens
@router.post("/collect")
# Parses the JSON body and turns it into a Python dictionary
async def collect_event(event: dict, public_api_key: str):
    # Verify the public api key
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
    
    # Add the public_api_key to the event data
    event["project_api_key"] = public_api_key

    # Since schema may be different, get the extracted text and store it in event
    event["payload"]["extracted_text"] = get_text(public_api_key, event.get("payload")["url"], event.get("payload")["body"], event.get("event_type"))
    
    # Insert the event data
    response = supabase.table("events").insert(event).execute()

    # Grab the request_id
    request_id = event.get("request_id")

    ''' After inserting the data, if this is an ai_response or user_request event, ensure the other is in supabase and calculate latency '''
    if event.get("event_type") == "ai_response":
        # Check supabase for ai_request with same request_id
        request_response = supabase.table("events").select("created_at").eq("request_id", request_id).eq("event_type", "ai_request").limit(1).execute()
        if request_response.data and len(request_response.data) > 0:
            # Grab the response timestamp from the supabase entry rather than the events
            response_response = supabase.table("events").select("created_at").eq("request_id", request_id).eq("event_type", "ai_response").limit(1).execute()
            calculate_latency(public_api_key, event.get("payload")["url"], request_response.data[0]["created_at"], response_response.data[0]["created_at"], request_id)
    elif event.get("event_type") == "ai_request":
        # Check supabase for ai_response with same request_id
        response_response = supabase.table("events").select("created_at").eq("request_id", request_id).eq("event_type", "ai_response").limit(1).execute()
        if response_response.data and len(response_response.data) > 0:
            # Grab the request timestamp from the supabase entry rather than the events
            request_response = supabase.table("events").select("created_at").eq("request_id", request_id).eq("event_type", "ai_request").limit(1).execute()
            calculate_latency(public_api_key, event.get("payload")["url"], request_response.data[0]["created_at"], response_response.data[0]["created_at"], request_id)     

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

# Helper for /register_domain to grab all domains
def get_domains_helper(user_id):
    # Ensure user_id is valid
    if not user_id or user_id in ["undefined", "null"]:
        return {"domains": [], "names": []}
    
    # Grab the response from Supabase for domains
    response = supabase.table("projects").select("domain", "project_name").eq("user_id", user_id).execute()

    # Ensure there is a response
    if not response.data:
        return {"domains": [], "names": []}

    # Grab each domain from each row
    domains, names = [row["domain"] for row in response.data if row.get("domain")], [row["project_name"] for row in response.data if row.get("project_name")]

    return {"domains": domains, "names": names}

class RegisterDomainRequest(BaseModel):
    user_id: str
    domain: str
    name: str

# When a user wishes to register a domain, add it to their allowlist in Supabase
@router.post("/register_domain")
async def register_domain(payload: RegisterDomainRequest):
    user_id = payload.user_id
    domain = payload.domain
    name = payload.name

    # Ensure user_id is valid
    if not user_id or user_id in ["undefined", "null"]:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    
    # Grab the existing domains from Supabase if it exists
    domains_names = get_domains_helper(user_id)

    # If the domain-name pair already exists, return exists
    if (domain, name) in zip(domains_names["domains"], domains_names["names"]):
        return {"status": "exists"}
    
    # Do a while true loop to avoid api key collisions
    while(True):
        # Generate an api key for the new domain
        api_key = "aia_pk_" + secrets.token_urlsafe(16)
        
        # Insert the new domain into the projects table, check if the api key meets a collision
        try:
            supabase.table("projects").insert({"user_id": user_id, "project_name": name,"domain": domain, "public_api_key": api_key, "public_api_key_enabled": True}).execute()
            break
        except Exception as e:
            continue

    # When a project is officially registered, I need to update the project_api_urls table to have an entry for this api key
    supabase.table("project_api_urls").insert({"project_api_key": api_key, "all_api_urls": {"urls": []}, "valid_api_urls": {"urls": []}}).execute()
    
    # After the project is registered, refresh the allowed origins cache
    refresh_allowed_origins_cache_from_supabase()

    return {"status": "registered"}

class DomainsRequest(BaseModel):
    user_id: str

# When loading user dashboard, grab their domain allowlist from Supabase
@router.post("/get_projects_info")
async def get_domains(payload: DomainsRequest):
    user_id = payload.user_id

    # Gets the project name, domain, and api key for all projects for this user
    response = supabase.table("projects").select("domain", "public_api_key", "project_name").eq("user_id", user_id).execute()

    # Ensure there is a response
    if not response.data:
        return {"domains": [], "api_keys": []}
    domains = [row["domain"] for row in response.data if row.get("domain")]
    api_keys = [row["public_api_key"] for row in response.data if row.get("public_api_key")]
    names = [row["project_name"] for row in response.data if row.get("project_name")]
    
    return {"domains": domains, "api_keys": api_keys, "names": names}

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

@router.get("/getLatencyRollupData")
async def get_latency_rollup_data(public_api_key: str, endpoint: str):
    # Ensure project_id is valid
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
    
    # Grab latency rollup data from Supabase but only for the last 24 hours
    response = supabase.rpc("get_latency_rollups", {
        "p_project_api_key": public_api_key,
        "p_endpoint": endpoint
    }).execute()

    if response.data:
        return {"latency_rollups": response.data}
    else:
        return {"latency_rollups": []}
    
# Based on the domain and name of the project, grab the api key from a specific user for CopyCard display
@router.post("/get_project_copy_card")
async def get_project_copy_card(payload: RegisterDomainRequest):
    user_id = payload.user_id
    domain = payload.domain
    name = payload.name

    # Ensure user_id is valid
    if not user_id or user_id in ["undefined", "null"]:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    
    # Grab the response from Supabase for domains
    response = supabase.table("projects").select("public_api_key").eq("user_id", user_id).eq("domain", domain).eq("project_name", name).limit(1).execute()

    # Ensure there is a response
    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    
    api_key = response.data[0]["public_api_key"]
    return {"public_api_key": api_key}

# Delete projects as grouped in an array
class DeleteProjectRequest(BaseModel):
    project_api_keys: List[str]

@router.post("/delete_projects")
async def delete_project(payload: DeleteProjectRequest):
    project_api_keys = payload.project_api_keys

    # If no keys provided, provide warning but no error (basically do nothing)
    if not project_api_keys or len(project_api_keys) == 0:
        return {"status": "no_keys_provided"}
    
    for project_api_key in project_api_keys:
        # Ensure project_api_key is valid
        if not verify_public_api_key(project_api_key):
            raise HTTPException(status_code=403, detail="Invalid or disabled project_api_key")

        # Delete the project from the projects table
        supabase.table("projects").delete().eq("public_api_key", project_api_key).execute()

        # Delete the project from the project_api_urls table
        supabase.table("project_api_urls").delete().eq("project_api_key", project_api_key).execute()

        # Delete the project from the events, latency_events, and Latency_rollups tables
        supabase.table("events").delete().eq("project_api_key", project_api_key).execute()
        supabase.table("latency_events").delete().eq("project_api_key", project_api_key).execute()
        supabase.table("latency_rollups").delete().eq("project_api_key", project_api_key).execute()

    return {"status": "deleted"}

# Get the schema for a specific public_api_key and url
@router.post("/get_schema")
async def get_schema(public_api_key: str, url: str):
    # Ensure project_id is valid
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
    
    # Grab the response from Supabase
    response = supabase.table("project_api_urls").select("message_paths").eq("project_api_key", public_api_key).execute()

    # Initialize empty paths
    user_request = ""
    ai_response = ""

    # Return the schema if it exists (first will be user and second will be ai always)
    if response.data and response.data[0]["message_paths"]:
        if response.data[0]["message_paths"].get(url):
            user_request = response.data[0]["message_paths"].get(url)[0]
            ai_response = response.data[0]["message_paths"].get(url)[1]
        
        return {"user_request": user_request, "ai_response": ai_response}
    else:
        return {"user_request": "", "ai_response": ""}

# Set the message paths for a particular endpoint of a project
@router.post("/set_schema")
async def set_schema(public_api_key: str, url: str, user_request_path: str, ai_response_path: str):
    # Ensure project_id is valid
    if not verify_public_api_key(public_api_key):
        raise HTTPException(status_code=403, detail="Invalid or disabled public_api_key")
    
    # Grab the existing message paths from Supabase
    response = supabase.table("project_api_urls").select("message_paths").eq("project_api_key", public_api_key).execute()

    message_paths = {}
    if response.data and response.data[0]["message_paths"]:
        message_paths = response.data[0]["message_paths"]
    
    # Update the message paths for this url
    message_paths[url] = [user_request_path, ai_response_path]

    # Update the row in Supabase
    supabase.table("project_api_urls").update({"message_paths": message_paths}).eq("project_api_key", public_api_key).execute()

    return {"status": "updated"}