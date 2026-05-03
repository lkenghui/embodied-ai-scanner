import feedparser
import httpx
from datetime import datetime
from config import MIT_TECH_REVIEW_FEED, COMPANY_BLOG_FEEDS, VENTUREBEAT_AI_FEED, THE_VERGE_AI_FEED


def _parse_feed(url: str, source: str, company: str = None) -> list[dict]:
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries[:20]:
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6]).isoformat()
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6]).isoformat()

        summary = getattr(entry, "summary", "") or ""
        # Strip basic HTML tags from summary
        import re
        summary = re.sub(r"<[^>]+>", "", summary).strip()

        results.append({
            "title": entry.get("title", "").strip(),
            "url": entry.get("link", ""),
            "source": source,
            "company": company,
            "published": published,
            "abstract": summary[:1000],
        })
    return results


def fetch_mit_tech_review() -> list[dict]:
    return _parse_feed(MIT_TECH_REVIEW_FEED, source="MIT Technology Review")


def fetch_venturebeat() -> list[dict]:
    return _parse_feed(VENTUREBEAT_AI_FEED, source="VentureBeat")


def fetch_the_verge() -> list[dict]:
    return _parse_feed(THE_VERGE_AI_FEED, source="The Verge")


def fetch_company_blogs() -> list[dict]:
    results = []
    for company, feed_url in COMPANY_BLOG_FEEDS.items():
        try:
            items = _parse_feed(feed_url, source="Company Blog", company=company)
            results.extend(items)
        except Exception as e:
            print(f"[feed_scraper] Failed to fetch {company}: {e}")
    return results
