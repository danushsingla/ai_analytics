import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# Load .env.local by looking for the file two directories above
load_dotenv(os.path.join(os.path.dirname(__file__), "../../", ".env.local"))
supabase_url = os.getenv("SUPABASE_URL")
print(supabase_url)
key = os.getenv("SUPABASE_SERVICE_KEY")

# Create a Supabase client with the url and service key
supabase: Client = create_client(supabase_url, key)

# Calculates latency differences between request and response timestamps and stores them in the latency_events table
def calculate_latency(public_api_key, endpoint, request_ts, response_ts, request_id):
        # Convert timestamps to milliseconds and calculate latency
        request_ms = datetime.fromisoformat(request_ts.replace("Z", "+00:00"))
        response_ms = datetime.fromisoformat(response_ts.replace("Z", "+00:00"))
        latency_ms = (response_ms - request_ms).total_seconds() * 1000  # Convert to milliseconds

        latency_event = {
            "project_api_key": public_api_key,
            "request_id": request_id,
            "endpoint": endpoint,
            "request_ts": request_ts,
            "response_ts": response_ts,
            "latency_ms": latency_ms
        }

        # Insert the latency event into the latency_events table (using upsert to avoid duplicates)
        supabase.table("latency_events").upsert(latency_event).execute()

# Update the latency_rollup table with average latency per endpoint for a given project_api_key over some period of seconds
def update_latency_rollup():
    # Call supabase for projects to get all project_api_keys
    response = supabase.table("projects").select("public_api_key").execute()
    if not response.data:
        print("No projects found for latency rollup update.")
        return
    projects = response.data[0]["public_api_key"]

    # We will update for each project that exists
    for project_api_key in projects:
        # We run the "Latency_Events_Rollup" SQL script in Supabase by sending in the project api key, and the start and end timestamps of the period
        now = datetime.now(timezone.utc)

        # Set end_ts to the start of the previous minute for a one minute safety lag
        end_ts = now.replace(second=0, microsecond=0) - timedelta(minutes=1)

        # Call supabase to get when the last rollup was done for the current project
        last_rollup_response = supabase.table("projects").select("last_latency_rollup").eq("project_api_key", project_api_key).order("end_ts", desc=True).limit(1).execute()

        # If there was a previous rollup, set start_ts to that timestamp otherwise set it to one hour ago
        if last_rollup_response.data and len(last_rollup_response.data) > 0:
            last_rollup_ts = last_rollup_response.data[0]["last_latency_rollup"]
            start_ts = last_rollup_ts
        else:
            start_ts = end_ts - timedelta(minutes=60)

        # Call the RPC function in Supabase to do the rollup
        supabase.rpc("run_latency_rollup", {
            "p_project_api_key": project_api_key,
            "p_start_ts": start_ts.isoformat(),
            "p_end_ts": end_ts.isoformat(),
        }).execute()