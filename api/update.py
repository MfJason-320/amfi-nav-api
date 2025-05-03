# api/update.py
import os
import sys
from storage import init_db
from nav_fetcher import fetch_and_store_schemes, fetch_daily_nav

# Add project root to path so imports work
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def handler(request, response):
    init_db()
    fetch_and_store_schemes()
    fetch_daily_nav()
    return response.json({"status": "daily update completed"})
