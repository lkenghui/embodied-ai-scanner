import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

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
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Recent articles:\n{content}"}],
    )
    return message.content[0].text.strip()
