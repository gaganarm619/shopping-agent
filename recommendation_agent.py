import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_recommendation(query, candidates, review_summary=None):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Add it to your .env file.")

    client = genai.Client(api_key=GEMINI_API_KEY)

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

    review_context = ""
    if review_summary and review_summary.get("review_count", 0) > 0:
        review_context = "\n\nAdditionally, here is a summary of " + str(review_summary['review_count']) + " real customer reviews for the top value candidate (\"" + str(review_summary['product_query']) + "\"):\nPros: " + ', '.join(review_summary['pros']) + "\nCons: " + ', '.join(review_summary['cons']) + "\nSummary: " + review_summary['summary'] + "\n\nFactor this real customer sentiment into your ranking and reasoning where relevant."

    prompt = "You are a shopping recommendation agent. A user searched for: \"" + query + "\"\n\nHere are the candidate products found:\n" + json.dumps(trimmed, indent=2) + review_context + "\n\nRank these products from best to worst match for the user's query, considering price, rating, number of reviews, and any real customer review sentiment provided above.\n\nRespond ONLY with valid JSON in this exact format, no other text:\n{\n  \"ranked_products\": [\n    {\"product_id\": \"...\", \"rank\": 1, \"reasoning\": \"one sentence why this rank\"}\n  ],\n  \"overall_reasoning\": \"2-3 sentences summarizing the tradeoffs across all options\"\n}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw_text = response.text.strip()
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    return json.loads(raw_text)


if __name__ == "__main__":
    test_candidates = [
        {"product_id": "1", "title": "SoundCore Q20 Wireless Earbuds", "price": 29.99, "rating": 4.3, "reviews_count": 12500, "source": "Amazon"},
        {"product_id": "2", "title": "JLab Go Air Pop", "price": 19.99, "rating": 4.1, "reviews_count": 8900, "source": "BestBuy"},
        {"product_id": "3", "title": "NoName Earbuds Pro", "price": 12.99, "rating": 3.5, "reviews_count": 45, "source": "Walmart"},
    ]

    result = get_recommendation("wireless earbuds under 1000 rupees", test_candidates)
    print(json.dumps(result, indent=2))