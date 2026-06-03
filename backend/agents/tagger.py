from backend.agents.anthropic_client import generate_json

TOPICS = [
    # Embodied AI / Robotics
    "locomotion", "manipulation", "dexterous hands", "whole-body control",
    "sim-to-real", "world models", "vision-language-action", "reinforcement learning",
    "imitation learning", "humanoid", "legged robots", "autonomous navigation",
    "tactile sensing", "hardware",
    # Agentic AI
    "agentic AI", "multi-agent systems", "tool use", "AI planning", "AI reasoning",
    # Physics-based AI
    "physics simulation", "physics-informed ML", "differentiable simulation",
    # Quantum Computing & AI
    "quantum machine learning", "quantum computing", "quantum algorithms", "quantum hardware",
    # General AI
    "foundation models", "large language models", "AI safety", "AI policy",
    "investment/funding", "policy/regulation",
]

SYSTEM_PROMPT = f"""You are a technology analyst covering AI research and industry.
Given an article title and abstract, return JSON with:
- "topics": list of 1-3 relevant topics from this list: {TOPICS}
- "significance": one of "high", "medium", "low"
  (high = breakthrough, major funding, new product launch;
   medium = incremental research, company update;
   low = minor news, opinion piece)

Respond with structured JSON only."""

TAG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "topics": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string", "enum": TOPICS},
        },
        "significance": {"type": "string", "enum": ["high", "medium", "low"]},
    },
    "required": ["topics", "significance"],
}


def tag(title: str, abstract: str) -> tuple[list[str], str]:
    """Returns (topics, significance)."""
    text = f"Title: {title}\n\nAbstract: {abstract[:1500]}"
    try:
        data = generate_json(
            SYSTEM_PROMPT,
            text,
            TAG_SCHEMA,
            name="article_tags",
            max_output_tokens=250,
        )
        topics = data.get("topics", [])
        significance = data.get("significance", "medium")
        return topics, significance
    except Exception:
        return [], "medium"
