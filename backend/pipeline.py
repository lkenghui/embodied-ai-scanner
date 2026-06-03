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
from config import ANTHROPIC_API_KEY, TOPIC_AREA_KEYWORDS

_scan_lock = threading.Lock()
scan_state = {"running": False, "processed": 0, "total": 0, "saved": 0, "stage": ""}
MISSING_ANTHROPIC_KEY_STAGE = "Anthropic API key missing. Add ANTHROPIC_API_KEY to .env before running a scan."


def get_scan_state():
    return dict(scan_state)


def run_scan():
    if not _scan_lock.acquire(blocking=False):
        print("[pipeline] Scan already running, skipping.")
        return
    scan_state.update({"running": True, "processed": 0, "total": 0, "saved": 0, "stage": "starting"})
    try:
        _run_scan()
    except Exception as e:
        scan_state["stage"] = f"failed: {e}"
        print(f"[pipeline] Scan failed: {e}")
    finally:
        if not scan_state["stage"].startswith("failed:"):
            if scan_state["stage"] != MISSING_ANTHROPIC_KEY_STAGE:
                scan_state["stage"] = "complete"
        scan_state["running"] = False
        _scan_lock.release()


def _run_scan():
    print("[pipeline] Starting scan...")
    if not ANTHROPIC_API_KEY:
        scan_state.update({
            "stage": MISSING_ANTHROPIC_KEY_STAGE,
            "processed": 0,
            "total": 0,
            "saved": 0,
        })
        print("[pipeline] ANTHROPIC_API_KEY is not configured; scan skipped.")
        return

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

    def _ascii(s: str) -> str:
        return (s or "").encode("ascii", errors="ignore").decode("ascii")

    saved = 0
    topic_counts = {}
    for item in raw_items:
        title = _ascii(item.get("title", ""))
        abstract = _ascii(item.get("abstract", ""))

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

    # 7. Generate trend + signal reports — global ("all") and per topic area
    recent = get_articles(limit=80)
    history = []
    try:
        history = get_topic_history(days=60)
    except Exception as e:
        print(f"[pipeline] Could not fetch topic history: {e}")

    def articles_for_area(articles, area_keywords):
        def matches(a):
            text = ((a.get("tags") or "") + " " + (a.get("title") or "")).lower()
            return any(kw in text for kw in area_keywords)
        return [a for a in articles if matches(a)]

    def topics_for_area(topic_history, area_keywords):
        return [row for row in topic_history if any(kw in row["topic"].lower() for kw in area_keywords)]

    # Global report
    if recent:
        report = generate_trend_report(recent)
        save_trend_report(report, topic_area="all")
        print("[pipeline] Global trend report generated")
    try:
        signal_report = detect_weak_signals(history)
        save_signal_report(signal_report, topic_area="all")
        print("[pipeline] Global weak signal report generated")
    except Exception as e:
        print(f"[pipeline] Global signal detection failed: {e}")

    # Per-topic reports
    for area, keywords in TOPIC_AREA_KEYWORDS.items():
        area_articles = articles_for_area(recent, keywords)
        if area_articles:
            try:
                report = generate_trend_report(area_articles)
                save_trend_report(report, topic_area=area)
                print(f"[pipeline] Trend report generated for {area}")
            except Exception as e:
                print(f"[pipeline] Trend report failed for {area}: {e}")
        area_history = topics_for_area(history, keywords)
        if area_history:
            try:
                signal_report = detect_weak_signals(area_history)
                save_signal_report(signal_report, topic_area=area)
                print(f"[pipeline] Signal report generated for {area}")
            except Exception as e:
                print(f"[pipeline] Signal report failed for {area}: {e}")

    print("[pipeline] Scan complete")


if __name__ == "__main__":
    from backend.database import init_db
    init_db()
    run_scan()
