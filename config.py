import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "scanner.db")

COMPANIES = [
    # Embodied AI / Robotics - US
    "Figure AI", "Physical Intelligence", "Boston Dynamics", "Agility Robotics",
    "Tesla Optimus", "1X Technologies", "Apptronik", "Sharpa", "AI2",
    # Embodied AI / Robotics - China
    "Unitree", "Zhiyuan Robotics", "AgiBot", "UBTECH", "Fourier Intelligence",
    "Deep Robotics", "EngineAI",
    # Foundation Models / Agentic AI
    "Anthropic", "OpenAI", "Google DeepMind", "Microsoft", "xAI", "Mistral",
    "Cohere", "Hugging Face", "LangChain", "Perplexity",
    # World Models / Broader
    "World Labs", "Wayve", "Nvidia", "DeepMind", "Meta", "Runway", "Odyssey",
]

COMPANY_BLOG_FEEDS = {
    # Robotics
    "Boston Dynamics": "https://bostondynamics.com/blog/feed/",
    "Agility Robotics": "https://agilityrobotics.com/blog/feed/",
    "Figure AI": "https://www.figure.ai/news/rss.xml",
    "Wayve": "https://wayve.ai/thinking/feed/",
    # Foundation Models / Agentic AI
    "OpenAI": "https://openai.com/blog/rss.xml",
    "DeepMind": "https://deepmind.google/blog/rss.xml",
    "Meta AI": "https://ai.meta.com/blog/rss/",
    "Anthropic": "https://www.anthropic.com/news/rss.xml",
    "Nvidia": "https://blogs.nvidia.com/feed/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
}

ARXIV_QUERY = (
    "embodied AI OR humanoid robot OR robot learning OR world model robot "
    "OR locomotion manipulation OR sim-to-real OR vision language action "
    "OR agentic AI OR AI agent OR multi-agent OR autonomous agent OR tool use LLM "
    "OR physics simulation AI OR physics-informed neural network OR neural physics "
    "OR quantum computing machine learning OR quantum AI OR quantum neural network "
    "OR large language model reasoning OR foundation model"
)
ARXIV_MAX_RESULTS = 50

MIT_TECH_REVIEW_FEED = "https://www.technologyreview.com/feed/"
VENTUREBEAT_AI_FEED = "https://venturebeat.com/category/ai/feed/"
THE_VERGE_AI_FEED = "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"

SCAN_HOUR = 7   # run daily at 7am
SCAN_MINUTE = 0

# Keywords used to filter articles into topic areas for per-tab reports
TOPIC_AREA_KEYWORDS = {
    "embodied": [
        "humanoid", "locomotion", "manipulation", "dexterous", "whole-body",
        "sim-to-real", "world model", "vision-language-action", "legged",
        "autonomous navigation", "tactile", "imitation learning",
    ],
    "agentic": [
        "agentic", "multi-agent", "tool use", "ai planning", "ai reasoning",
        "autonomous agent", "agent framework",
    ],
    "physics": [
        "physics simulation", "physics-informed", "differentiable simulation",
        "neural physics", "generative physics",
    ],
    "quantum": [
        "quantum machine learning", "quantum computing", "quantum algorithm",
        "quantum hardware", "quantum neural",
    ],
}
