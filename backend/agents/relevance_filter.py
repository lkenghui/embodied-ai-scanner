import anthropic
from config import ANTHROPIC_API_KEY, COMPANIES

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are an expert technology analyst covering AI research and industry developments.
Your job is to determine if a given article or paper is relevant to any of these areas:

1. Embodied AI & Robotics: humanoid robots, legged/wheeled robots, robot learning,
   manipulation, locomotion, sim-to-real transfer, vision-language-action (VLA) models,
   world models for robotics, dexterous hands, whole-body control.

2. Agentic AI: AI agents, multi-agent systems, autonomous AI, tool use, AI planning,
   LLM-based agents, agent frameworks, AI reasoning and decision-making.

3. Physics-based AI: physics simulation, physics-informed neural networks, neural physics,
   differentiable simulation, generative physics models, AI for scientific simulation.

4. Quantum Computing & AI: quantum machine learning, quantum neural networks, quantum algorithms
   for AI, quantum hardware advances, quantum-classical hybrid systems, quantum advantage.

5. General AI Trends: foundation models, large language models, major AI research breakthroughs,
   significant AI company news, AI policy and regulation, major AI product launches.

Respond with JSON only: {"relevant": true/false, "reason": "one sentence"}"""


def is_relevant(title: str, abstract: str) -> tuple[bool, str]:
    """Returns (is_relevant, reason)."""
    text = f"Title: {title}\n\nAbstract: {abstract[:1500]}"
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    import json, re
    try:
        text = message.content[0].text
        text = re.sub(r"^```[a-z]*\n?", "", text.strip(), flags=re.MULTILINE)
        text = text.rstrip("`").strip()
        data = json.loads(text)
        return data.get("relevant", False), data.get("reason", "")
    except Exception:
        return False, ""


def detect_company(title: str, abstract: str) -> "str | None":
    """Return the company name mentioned, if any from our watchlist."""
    text = (title + " " + abstract).lower()
    for company in COMPANIES:
        if company.lower() in text:
            return company
    return None
