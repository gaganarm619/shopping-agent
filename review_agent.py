"""
Review Summarizer Agent - Step 5

Takes a product name, finds matching reviews in the Amazon Reviews dataset,
and asks Gemini to synthesize them into pros/cons - instead of dumping raw
review text at the user.

This agent handles messier, real-world data (free text) compared to the
clean JSON from search_agent.py - a good thing to highlight on a resume,
since it shows you can work with unstructured input, not just tidy APIs.

Run directly to test:  python review_agent.py
"""

import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CSV_PATH = "archive/1429_1.csv"

# Load once at import time - the CSV is ~34k rows, small enough to keep in memory
_df = None


def _load_data() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(CSV_PATH, low_memory=False)
    return _df


def find_reviews(product_name_query: str, max_reviews: int = 15) -> list[dict]:
    """
    Find reviews for products whose name loosely matches the query.

    Args:
        product_name_query: partial product name, e.g. "Fire HD 8 Tablet"
        max_reviews: cap on how many reviews to pull (keeps the Gemini prompt small)

    Returns:
        List of dicts: [{rating, title, text}, ...]
    """
    df = _load_data()

    matches = df[df["name"].str.contains(product_name_query, case=False, na=False)]

    if matches.empty:
        return []

    matches = matches.head(max_reviews)

    reviews = []
    for _, row in matches.iterrows():
        text = row.get("reviews.text")
        if pd.isna(text) or not str(text).strip():
            continue
        reviews.append({
            "rating": row.get("reviews.rating"),
            "title": row.get("reviews.title"),
            "text": str(text)[:500],  # trim very long reviews to keep prompt size sane
        })

    return reviews


def summarize_reviews(product_name_query: str) -> dict:
    """
    Find reviews for a product and ask Gemini to synthesize pros/cons.

    Returns:
        dict with keys: product_query, review_count, pros (list), cons (list), summary (str)
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Add it to your .env file.")

    reviews = find_reviews(product_name_query)

    if not reviews:
        return {
            "product_query": product_name_query,
            "review_count": 0,
            "pros": [],
            "cons": [],
            "summary": "No reviews found for this product in the dataset.",
        }

    client = genai.Client(api_key=GEMINI_API_KEY)

    reviews_text = "\n\n".join(
        f"Rating: {r['rating']}/5\nTitle: {r['title']}\nReview: {r['text']}"
        for r in reviews
    )

    prompt = f"""You are a review summarization agent. Below are {len(reviews)} real customer
reviews for a product matching: "{product_name_query}"

{reviews_text}

Synthesize these into a concise summary. Respond ONLY with valid JSON, no other text,
in this exact format:
{{
  "pros": ["short phrase", "short phrase", "short phrase"],
  "cons": ["short phrase", "short phrase"],
  "summary": "2-3 sentence overall summary of customer sentiment"
}}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
    parsed = json.loads(raw_text)

    return {
        "product_query": product_name_query,
        "review_count": len(reviews),
        "pros": parsed.get("pros", []),
        "cons": parsed.get("cons", []),
        "summary": parsed.get("summary", ""),
    }


if __name__ == "__main__":
    test_query = "Fire HD 8 Tablet"
    print(f"Summarizing reviews for: {test_query}\n")

    result = summarize_reviews(test_query)
    print(json.dumps(result, indent=2))
