import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            url         TEXT UNIQUE NOT NULL,
            source      TEXT NOT NULL,
            company     TEXT,
            published   TEXT,
            summary     TEXT,
            tags        TEXT,
            significance TEXT,
            fetched_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS trends (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            report      TEXT NOT NULL,
            generated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS topic_snapshots (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date   TEXT NOT NULL,
            topic       TEXT NOT NULL,
            count       INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS signals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            report      TEXT NOT NULL,
            generated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_articles_source    ON articles(source);
        CREATE INDEX IF NOT EXISTS idx_articles_company   ON articles(company);
        CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published);
        CREATE INDEX IF NOT EXISTS idx_snapshots_date     ON topic_snapshots(scan_date);
    """)
    conn.commit()
    conn.close()


def upsert_article(title, url, source, company, published, summary, tags, significance):
    conn = get_conn()
    conn.execute("""
        INSERT INTO articles (title, url, source, company, published, summary, tags, significance, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            summary=excluded.summary,
            tags=excluded.tags,
            significance=excluded.significance,
            fetched_at=excluded.fetched_at
    """, (title, url, source, company, published, summary, tags, significance, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def save_trend_report(report: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO trends (report, generated_at) VALUES (?, ?)",
        (report, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_articles(source=None, company=None, limit=200):
    conn = get_conn()
    query = "SELECT * FROM articles WHERE 1=1"
    params = []
    if source:
        query += " AND source = ?"
        params.append(source)
    if company:
        query += " AND company LIKE ?"
        params.append(f"%{company}%")
    query += " ORDER BY published DESC, fetched_at DESC LIMIT ?"
    params.append(limit)
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    return rows


def get_latest_trend():
    conn = get_conn()
    row = conn.execute("SELECT * FROM trends ORDER BY generated_at DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


def get_sources():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT source FROM articles ORDER BY source").fetchall()
    conn.close()
    return [r["source"] for r in rows]


def get_companies():
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT company FROM articles WHERE company IS NOT NULL ORDER BY company"
    ).fetchall()
    conn.close()
    return [r["company"] for r in rows]


def save_topic_snapshot(scan_date: str, topic_counts: dict):
    conn = get_conn()
    conn.executemany(
        "INSERT INTO topic_snapshots (scan_date, topic, count) VALUES (?, ?, ?)",
        [(scan_date, topic, count) for topic, count in topic_counts.items()]
    )
    conn.commit()
    conn.close()


def get_topic_history(days: int = 60) -> list[dict]:
    """Returns topic counts per scan_date for the last N days."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT scan_date, topic, count FROM topic_snapshots
        WHERE scan_date >= datetime('now', ?)
        ORDER BY scan_date ASC
    """, (f"-{days} days",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_signal_report(report: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO signals (report, generated_at) VALUES (?, ?)",
        (report, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_latest_signal():
    conn = get_conn()
    row = conn.execute("SELECT * FROM signals ORDER BY generated_at DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None
