import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "scanner.db")

COMPANIES = [
    # US
    "Figure AI", "Physical Intelligence", "Boston Dynamics", "Agility Robotics",
    "Tesla Optimus", "1X Technologies", "Apptronik", "Sharpa", "AI2",
    # China
    "Unitree", "Zhiyuan Robotics", "AgiBot", "UBTECH", "Fourier Intelligence",
    "Deep Robotics", "EngineAI",
    # World Models / Broader
    "World Labs", "Wayve", "Nvidia", "DeepMind", "Meta", "OpenAI", "Runway", "Odyssey",
]

COMPANY_BLOG_FEEDS = {
    "Boston Dynamics": "https://bostondynamics.com/blog/feed/",
    "OpenAI": "https://openai.com/blog/rss.xml",
    "DeepMind": "https://deepmind.google/blog/rss.xml",
    "Meta AI": "https://ai.meta.com/blog/rss/",
    "Nvidia": "https://blogs.nvidia.com/feed/",
    "Wayve": "https://wayve.ai/thinking/feed/",
    "Agility Robotics": "https://agilityrobotics.com/blog/feed/",
    "Figure AI": "https://www.figure.ai/news/rss.xml",
}

ARXIV_QUERY = (
    "embodied AI OR humanoid robot OR robot learning OR world model robot "
    "OR locomotion manipulation OR sim-to-real OR vision language action"
)
ARXIV_MAX_RESULTS = 30

MIT_TECH_REVIEW_FEED = "https://www.technologyreview.com/feed/"

SCAN_HOUR = 7   # run daily at 7am
SCAN_MINUTE = 0
