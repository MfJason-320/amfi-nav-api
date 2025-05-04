# api/update.py

from fastapi import FastAPI
from app.storage import init_db
from app.nav_fetcher import fetch_and_store_schemes, fetch_daily_nav

app = FastAPI()

# Register exactly the empty path – this will map to /api/update on Vercel
@app.get("")
def update_data():
    try:
        init_db()
        fetch_and_store_schemes()
        fetch_daily_nav()
        return {"status": "success", "message": "NAV data updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
