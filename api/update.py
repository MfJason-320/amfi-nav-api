# api/update.py

from fastapi import FastAPI
from app.nav_fetcher import fetch_daily_nav, fetch_and_store_schemes
from app.storage     import init_db

app = FastAPI()

@app.get("/")
def update_data():
    """
    Triggers a full update: scheme list + today's NAV.
    """
    try:
        # Ensure tables exist
        init_db()
        # Refresh scheme metadata (in case new schemes added)
        fetch_and_store_schemes()
        # Fetch and store today's NAV
        fetch_daily_nav()
        return {"status": "success", "message": "NAV data updated successfully"}
    except Exception as e:
        # Return error for debugging
        return {"status": "error", "message": str(e)}
