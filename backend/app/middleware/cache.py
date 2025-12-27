import asyncio
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from supabase import create_client, Client
from dotenv import load_dotenv

# Load .env.local by looking for the file one directory above
load_dotenv(os.path.join(os.path.dirname(__file__), "../", ".env.local"))
supabase_url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

# Create a Supabase client with the url and service key
supabase: Client = create_client(supabase_url, key)

# Empty Cache
ALLOWED_CACHE = {}

# Refresh the allowed origins cache
def refresh_allowed_origins_cache_from_supabase():
    try:
        # We will store the origins in a cache as follows: (pk_api: str) -> Dict[domain: str, api_enabled: bool]
        response = supabase.table("projects").select("domain, public_api_key, public_api_key_enabled").execute()
    except Exception as e:
        print(f"Error fetching allowed origins from Supabase: {e}")
        return

    if response.data:
        NEW_CACHE = {}

        for row in response.data:
            domains = row.get("domain")
            api_enableds = row.get("public_api_key_enabled")
            api_keys = row.get("public_api_key")

            # Create the dict
            if api_keys and domains and api_enableds is not None:
                NEW_CACHE[api_keys] = {"domain": domains, "api_enabled": api_enableds}
            else:
                print(f"Invalid row data when refreshing allowed origins from Supabase: {row}")
            
        # Update cache - doing it this way to avoid empty cache if mid-refresh
        ALLOWED_CACHE.clear()
        ALLOWED_CACHE.update(NEW_CACHE)

        print(ALLOWED_CACHE)
    else:
        print("No data found when refreshing allowed origins from Supabase.")

# Let's have a loop that refreshes every 60 seconds
async def refresh_loop():
    while True:
        try:
            refresh_allowed_origins_cache_from_supabase()
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