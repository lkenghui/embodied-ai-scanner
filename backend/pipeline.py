"""
Orchestrates the full scan: scrape → filter → summarise → tag → store → trend report.
"""
import sys
import os
import time
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.scrapers import fetch_arxiv_papers, fetch_mit_tech_review, fetch_company_blogs, fetch_venturebeat, fetch_the_verge
from backend.agents import is_relevant, detect_company, summarise, tag, generate_trend_report, detect_weak_signals
from backend.database import upsert_article, save_trend_report, get_articles, save_topic_snapshot, get_topic_history, save_signal_report

_scan_lock = threading.Lock()
scan_state = {"running": False, "processed": 0, "total": 0, "saved": 0, "stage": ""}


def get_scan_state():
    return dict(scan_state)


def run_scan():
    if not _scan_lock.acquire(blocking=False):
        print("[pipeline] Scan already running, skipping.")
        return
    scan_state.update({"running": True, "processed": 0, "total": 0, "saved": 0, "stage": "starting"})
    try:
        _run_scan()
    finally:
        scan_state.update({"running": False, "stage": "complete"})
        _scan_lock.release()


def _run_scan():
    print("[pipeline] Starting scan...")

    raw_items = []
    for fetch_fn in (fetch_arxiv_papers, fetch_mit_tech_review, fetch_company_blogs, fetch_venturebeat, fetch_the_verge):
        try:
            items = fetch_fn()
            raw_items.extend(items)
            print(f"[pipeline] {fetch_fn.__name__}: {len(items)} items")
        except Exception as e:
            print(f"[pipeline] {fetch_fn.__name__} failed: {e}")
    print(f"[pipeline] Fetched {len(raw_items)} raw items total")
    scan_state.update({"stage": "filtering", "total": len(raw_items), "processed": 0})

    saved = 0
    topic_counts = {}
    for item in raw_items:
        title = item.get("title", "")
        abstract = item.get("abstract", "")

        if not title or not item.get("url"):
            scan_state["processed"] += 1
            continue

        # 1. Relevance filter
        relevant, _ = is_relevant(title, abstract)
        scan_state["processed"] += 1
        if not relevant:
            continue

        # 2. Detect company if not already set
        company = item.get("company") or detect_company(title, abstract)

        # 3. Summarise
        summary = summarise(title, abstract)

        # 4. Tag
        topics, significance = tag(title, abstract)

        # 5. Store
        upsert_article(
            title=title,
            url=item["url"],
            source=item["source"],
            company=company,
            published=item.get("published"),
            summary=summary,
            tags=", ".join(topics),
            significance=significance,
        )
        for t in topics:
            topic_counts[t] = topic_counts.get(t, 0) + 1
        saved += 1
        scan_state["saved"] = saved
        print(f"[pipeline] Saved: {title[:60]}")
        time.sleep(4)  # 3 API calls per item; 50 req/min limit needs ~4s gap
    print(f"[pipeline] Saved {saved} relevant articles")

    # 6. Save topic snapshot for weak signal tracking
    if topic_counts:
        from datetime import datetime
        save_topic_snapshot(datetime.utcnow().isoformat(), topic_counts)
        print(f"[pipeline] Topic snapshot saved: {topic_counts}")

    # 7. Generate trend report from recent articles
    recent = get_articles(limit=80)
    if recent:
        report = generate_trend_report(recent)
        save_trend_report(report)
        print("[pipeline] Trend report generated")

    # 8. Generate weak signal report from topic history
    try:
        history = get_topic_history(days=60)
        signal_report = detect_weak_signals(history)
        save_signal_report(signal_report)
        print("[pipeline] Weak signal report generated")
    except Exception as e:
        print(f"[pipeline] Weak signal detection failed: {e}")

    print("[pipeline] Scan complete")


if __name__ == "__main__":
    from backend.database import init_db
    init_db()
    run_scan()
