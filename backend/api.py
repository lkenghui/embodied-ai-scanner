import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
from backend.database import init_db, get_articles, get_latest_trend, get_sources, get_companies, get_latest_signal
from backend.pipeline import run_scan, get_scan_state
from config import SCAN_HOUR, SCAN_MINUTE

app = FastAPI(title="Embodied AI Scanner")

# Initialise DB on startup
init_db()

# Schedule daily scan
scheduler = BackgroundScheduler()
scheduler.add_job(run_scan, "cron", hour=SCAN_HOUR, minute=SCAN_MINUTE)
scheduler.start()


@app.get("/api/articles")
def articles(
    source: str = Query(None),
    company: str = Query(None),
    significance: str = Query(None),
    limit: int = Query(200),
):
    items = get_articles(source=source, company=company, limit=limit)
    if significance:
        items = [a for a in items if a.get("significance") == significance]
    return items


@app.get("/api/trends")
def trends(topic: str = Query("all")):
    return get_latest_trend(topic) or {"report": "No trend report yet. Run a scan first.", "generated_at": None}


@app.get("/api/filters")
def filters():
    return {"sources": get_sources(), "companies": get_companies()}


@app.get("/api/signals")
def signals(topic: str = Query("all")):
    return get_latest_signal(topic) or {"report": "No signal report yet. Run a scan first.", "generated_at": None}


@app.get("/api/scan/status")
def scan_status():
    return get_scan_state()


@app.post("/api/scan")
def trigger_scan():
    """Manually trigger a scan."""
    import threading
    threading.Thread(target=run_scan, daemon=True).start()
    return {"status": "scan started"}


# Serve frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))
