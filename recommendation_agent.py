"""
Recommendation Agent - Step 2

Standalone function that takes product candidates (from search_agent.py)
and asks Gemini (free tier) to reason over them and produce a ranked
recommendation with explanations.

Uses Google's Gemini API - completely free (1,500 requests/day on
Gemini Flash, no credit card required). Get a key at aistudio.google.com

Run directly to test:  python recommendation_agent.py
"""

import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_recommendation(query: str, candidates: list[dict]) -> dict:
    """
    Ask Gemini to rank product candidates and explain its reasoning.

    Args:
        query: the original shopping query, e.g. "wireless earbuds under $50"
        candidates: list of product dicts (from search_agent.search_products)

    Returns:
        dict with keys: ranked_products (list), overall_reasoning (str)
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Add it to your .env file.")

    client = genai.Client(api_key=GEMINI_API_KEY)

    # Keep the prompt tight - only send fields the model actually needs
    trimmed = [
        {
            "product_id": c.get("product_id"),
            "title": c.get("title"),
            "price": c.get("price"),
            "rating": c.get("rating"),
            "reviews_count": c.get("reviews_count"),
            "source": c.get("source"),
        }
        for c in candidates
    ]

    prompt = f"""You are a shopping recommendation agent. A user searched for: "{query}"

Here are the candidate products found:
{json.dumps(trimmed, indent=2)}

Rank these products from best to worst match for the user's query, considering
price, rating, and number of reviews (more reviews = more trustworthy rating).

Respond ONLY with valid JSON in this exact format, no other text:
{{
  "ranked_products": [
    {{"product_id": "...", "rank": 1, "reasoning": "one sentence why this rank"}}
  ],
  "overall_reasoning": "2-3 sentences summarizing the tradeoffs across all options"
}}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw_text = response.text.strip()
    # Strip markdown code fences if Gemini adds them despite instructions
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    return json.loads(raw_text)


if __name__ == "__main__":
    # Fake candidates for a standalone test - swap in real search_agent.py output later
    test_candidates = [
        {"product_id": "1", "title": "SoundCore Q20 Wireless Earbuds", "price": 29.99, "rating": 4.3, "reviews_count": 12500, "source": "Amazon"},
        {"product_id": "2", "title": "JLab Go Air Pop", "price": 19.99, "rating": 4.1, "reviews_count": 8900, "source": "BestBuy"},
        {"product_id": "3", "title": "NoName Earbuds Pro", "price": 12.99, "rating": 3.5, "reviews_count": 45, "source": "Walmart"},
    ]

    result = get_recommendation("wireless earbuds under $50", test_candidates)
    print(json.dumps(result, indent=2))
