"""
Search Agent - Step 1

Standalone function that queries SerpAPI's Google Shopping engine
and returns clean product data. No agent framework yet - just get
this working reliably first.

Run directly to test:  python search_agent.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_URL = "https://serpapi.com/search"


def search_products(query: str, num_results: int = 5) -> list[dict]:
    """
    Search Google Shopping via SerpAPI and return a clean list of candidate products.

    Args:
        query: natural language shopping query, e.g. "wireless earbuds under $50"
        num_results: how many candidates to return

    Returns:
        List of dicts: [{title, price, rating, source, link, product_id}, ...]
    """
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY not found. Add it to your .env file.")

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": SERPAPI_KEY,
    }

    response = requests.get(SERPAPI_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    raw_results = data.get("shopping_results", [])[:num_results]

    candidates = []
    for item in raw_results:
        candidates.append({
            "product_id": item.get("product_id") or item.get("position"),
            "title": item.get("title"),
            "price": item.get("extracted_price"),
            "rating": item.get("rating"),
            "reviews_count": item.get("reviews"),
            "source": item.get("source"),
            "link": item.get("link") or item.get("product_link"),
            "thumbnail": item.get("thumbnail"),
        })

    return candidates


if __name__ == "__main__":
    test_query = "wireless earbuds under $50"
    print(f"Searching for: {test_query}\n")

    results = search_products(test_query)

    if not results:
        print("No results found. Check your API key and query.")
    else:
        for i, product in enumerate(results, 1):
            print(f"{i}. {product['title']}")
            print(f"   Price: ${product['price']}  |  Rating: {product['rating']}  |  Source: {product['source']}")
            print(f"   Link: {product['link']}\n")
