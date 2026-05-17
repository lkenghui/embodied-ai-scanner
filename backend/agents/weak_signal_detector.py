"""
Detects weak signals: topics that are low in absolute volume but accelerating fast.
Compares recent scan window (last 14 days) vs previous window (15-45 days ago).
"""
from collections import defaultdict
from backend.agents.openai_client import generate_text

SYSTEM_PROMPT = """You are a strategic technology analyst covering AI research and industry.

You will receive topic frequency data comparing two time windows:
- RECENT (last 14 days): how often each topic appeared
- PREVIOUS (15-45 days ago): how often each topic appeared

Topics span five areas: embodied AI & robotics, agentic AI, physics-based AI, quantum computing & AI, and general AI trends.

Your job is to identify WEAK SIGNALS — topics that are:
1. Accelerating (frequency increasing, even if still low in absolute terms)
2. Potentially significant for the future of AI

For each weak signal, explain:
- What the signal is and which area it belongs to
- Why the acceleration matters
- What big trend it might be an early indicator of
- What to watch for next

Be specific and forward-looking. Avoid obvious dominant topics — focus on what's emerging under the radar.
Format as markdown bullet points. Aim for 3-5 signals."""


def detect_weak_signals(topic_history: list[dict]) -> str:
    """
    topic_history: list of {scan_date, topic, count} from DB
    Returns a markdown report string.
    """
    if not topic_history:
        return "Not enough historical data yet. Run more scans over time to detect weak signals."

    from datetime import datetime, timedelta

    now = datetime.utcnow()
    cutoff_recent = now - timedelta(days=14)
    cutoff_previous = now - timedelta(days=45)

    recent_counts = defaultdict(int)
    previous_counts = defaultdict(int)

    for row in topic_history:
        try:
            scan_dt = datetime.fromisoformat(row["scan_date"])
        except Exception:
            continue
        topic = row["topic"]
        count = row["count"]
        if scan_dt >= cutoff_recent:
            recent_counts[topic] += count
        elif scan_dt >= cutoff_previous:
            previous_counts[topic] += count

    if not recent_counts:
        return "No recent scan data available. Run a scan first."

    # Build comparison table
    all_topics = set(recent_counts) | set(previous_counts)
    lines = ["Topic | Recent (14d) | Previous (15-45d) | Change"]
    lines.append("------|-------------|-------------------|-------")
    for topic in sorted(all_topics):
        r = recent_counts.get(topic, 0)
        p = previous_counts.get(topic, 0)
        if p == 0:
            change = "+NEW" if r > 0 else "—"
        else:
            pct = round(((r - p) / p) * 100)
            change = f"{'+' if pct >= 0 else ''}{pct}%"
        lines.append(f"{topic} | {r} | {p} | {change}")

    content = "\n".join(lines)

    return generate_text(
        SYSTEM_PROMPT,
        f"Topic frequency comparison:\n\n{content}",
        report=True,
        max_output_tokens=1000,
    )
