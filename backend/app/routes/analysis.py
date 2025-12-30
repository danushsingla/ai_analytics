import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load .env.local by looking for the file two directories above
load_dotenv(os.path.join(os.path.dirname(__file__), "../../", ".env.local"))
supabase_url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

# Create a Supabase client with the url and service key
supabase: Client = create_client(supabase_url, key)


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