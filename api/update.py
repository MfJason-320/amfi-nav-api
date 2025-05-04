# api/update.py

from fastapi import FastAPI
from app.storage import init_db
from app.nav_fetcher import fetch_and_store_schemes, fetch_daily_nav

app = FastAPI()

# Match both / and empty string
@app.get("/", include_in_schema=False)
@app.get("", include_in_schema=False)
def update_data():
    """
    Triggers a full update: scheme list + today's NAV.
    """
    try:
        init_db()
        fetch_and_store_schemes()
        fetch_daily_nav()
        return {"status": "success", "message": "NAV data updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
