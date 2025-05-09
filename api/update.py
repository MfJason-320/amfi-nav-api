from app.storage import init_db
from app.nav_fetcher import fetch_and_store_schemes, fetch_daily_nav

def handler(request, response):
    try:
        init_db()
        fetch_and_store_schemes()
        fetch_daily_nav()
        return response.json({"status": "success", "message": "NAV updated."})
    except Exception as e:
        return response.json({"status": "error", "message": str(e)})
