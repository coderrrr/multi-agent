import json
import urllib.request
import urllib.error
from strands import tool
from utils.logger import get_logger

logger = get_logger(__name__)

@tool
def web_search(
    search_query: str, target_website: str = "", topic: str = None, days: int = None
) -> str:
    """Searches the web for information.
    Args:
        search_query (str): The query to search the web with.
        target_website (str): The specific website to search including its domain name. If not provided, the most relevant website will be used.
        topic (str): The topic being searched. 'news' or 'general'. Helps narrow the search when news is the focus.
        days (str): The number of days of history to search. Helps when looking for recent events or news..
    Returns:
        List with search results.
    """
    
    logger.info(f"executing Tavily AI search with {search_query=}")

    base_url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "api_key": "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",
        "query": search_query,
        "search_depth": "advanced",
        "include_images": False,
        "include_answer": False,
        "include_raw_content": False,
        "max_results": 4,
        "topic": "general" if topic is None else topic,
        "days": 30 if days is None else days,
        "include_domains": [target_website] if target_website else [],
        "exclude_domains": [],
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base_url, data=data, headers=headers
    )  # nosec: B310 fixed url we want to open

    try:
        response = urllib.request.urlopen(
            request
        )  # nosec: B310 fixed url we want to open
        response_data: str = response.read().decode("utf-8")
        logger.info(f"response from Tavily AI search {response_data=}")
        return response_data
    except urllib.error.HTTPError as e:
        logger.error(
            f"failed to retrieve search results from Tavily AI Search, error: {e.code}"
        )

    return ""