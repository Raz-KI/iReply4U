import os
from functools import lru_cache
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    # url = os.getenv("SUPABASE_URL")
    url = "https://phqpwmoovpdldmnikzre.supabase.co"
    # key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBocXB3bW9vdnBkbGRtbmlrenJlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5NDkxOTAsImV4cCI6MjA3MzUyNTE5MH0.CqubDfHbQaAU2A8Avwqfro-NofqojX_qcTjIFlEeTBU"
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_ANON_KEY/SUPABASE_SERVICE_ROLE_KEY in environment")
    return create_client(url, key)


