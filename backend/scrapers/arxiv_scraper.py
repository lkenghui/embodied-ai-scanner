import time
import arxiv
from config import ARXIV_QUERY, ARXIV_MAX_RESULTS


def fetch_arxiv_papers():
    """Fetch latest embodied AI papers from arXiv."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=ARXIV_QUERY,
        max_results=ARXIV_MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    results = []
    for attempt in range(3):
        try:
            for paper in client.results(search):
                results.append({
                    "title": paper.title,
                    "url": paper.entry_id,
                    "source": "arXiv",
                    "company": None,
                    "published": paper.published.isoformat() if paper.published else None,
                    "abstract": paper.summary,
                })
            break
        except arxiv.HTTPError as e:
            if e.status == 429 and attempt < 2:
                wait = 30 * (attempt + 1)
                print(f"[arxiv] Rate limited, retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"[arxiv] Failed after retries: {e}")
                break
        except Exception as e:
            print(f"[arxiv] Error fetching papers: {e}")
            break
    return results
