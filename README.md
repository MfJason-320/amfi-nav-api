# AMFI NAV API

This service fetches mutual fund NAV data from AMFI, stores it in SQLite, and exposes FastAPI endpoints.

## Setup

```bash
git clone https://github.com/yourusername/amfi-nav-api.git
cd amfi-nav-api
pip install -r requirements.txt
python storage.py       # Initializes the SQLite database
uvicorn main:app --reload
