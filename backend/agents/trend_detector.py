from backend.agents.openai_client import generate_text

SYSTEM_PROMPT = """You are a senior technology analyst covering AI research and industry.
You will receive a list of recent article titles and their tags across five areas:
embodied AI & robotics, agentic AI, physics-based AI, quantum computing & AI, and general AI trends.

Write a concise trend report (5-7 bullet points) covering:
- Dominant research themes this week across all areas
- Notable company activity
- Emerging topics gaining momentum
- Cross-cutting themes connecting multiple areas
- Any surprising or contrarian signals

Be specific — name companies, topics, and numbers where possible.
Format as markdown bullet points."""


def generate_trend_report(articles: list[dict]) -> str:
    """articles: list of {title, source, company, tags, significance}"""
    if not articles:
        return "No data available for trend analysis."

    lines = []
    for a in articles[:80]:  # cap to avoid token limits
        company = f" [{a.get('company')}]" if a.get("company") else ""
        tags = a.get("tags", "")
        lines.append(f"- {a['title']}{company} | tags: {tags} | significance: {a.get('significance', '')}")

    content = "\n".join(lines)
    return generate_text(
        SYSTEM_PROMPT,
        f"Recent articles:\n{content}",
        report=True,
        max_output_tokens=800,
    )
