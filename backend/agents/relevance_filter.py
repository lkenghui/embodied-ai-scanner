from config import COMPANIES
from backend.agents.anthropic_client import generate_json

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

Respond with structured JSON only."""

RELEVANCE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "relevant": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["relevant", "reason"],
}


def is_relevant(title: str, abstract: str) -> tuple[bool, str]:
    """Returns (is_relevant, reason)."""
    text = f"Title: {title}\n\nAbstract: {abstract[:1500]}"
    try:
        data = generate_json(
            SYSTEM_PROMPT,
            text,
            RELEVANCE_SCHEMA,
            name="relevance_result",
            max_output_tokens=150,
        )
        return data.get("relevant", False), data.get("reason", "")
    except Exception as e:
        import traceback
        print(f"[relevance_filter] Error: {e}")
        traceback.print_exc()
        return False, ""


def detect_company(title: str, abstract: str) -> "str | None":
    """Return the company name mentioned, if any from our watchlist."""
    text = (title + " " + abstract).lower()
    for company in COMPANIES:
        if company.lower() in text:
            return company
    return None
