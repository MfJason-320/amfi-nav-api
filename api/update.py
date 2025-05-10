# api/update.py

import traceback
from app.storage import init_db
from app.nav_fetcher import fetch_and_store_schemes, fetch_daily_nav

def handler(request, response):
    """
    Vercel will invoke this on GET /api/update.
    It initializes the DB, refreshes scheme metadata, and fetches today's NAV.
    """
    try:
        init_db()
        fetch_and_store_schemes()
        fetch_daily_nav()
        return response.json({"status": "success", "message": "NAV data updated."})
    except Exception as e:
        # Print the full traceback to Vercel logs so you can debug
        traceback.print_exc()
        return response.json({"status": "error", "message": str(e)})
