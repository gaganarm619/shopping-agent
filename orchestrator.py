import sys
import json

from search_agent import search_products
from price_agent import compare_prices
from review_agent import summarize_reviews
from recommendation_agent import get_recommendation


def run_pipeline(query, num_results=5):
    print(f"[1/4] Search Agent: searching for '{query}'...")
    candidates = search_products(query, num_results=num_results)
    if not candidates:
        raise RuntimeError("Search Agent returned no candidates. Check your SerpAPI key/quota.")
    print(f"      Found {len(candidates)} candidates.\n")

    print("[2/4] Price Agent: scoring candidates by value...")
    scored_candidates = compare_prices(candidates)
    best = next((c for c in scored_candidates if c["is_best_deal"]), None)
    print(f"      Best raw value score: {best['title']} (Rs.{best['price']})\n")

    print("[3/4] Review Summarizer Agent: pulling real customer reviews for top candidate...")
    review_summary = summarize_reviews(best["title"].split(",")[0])
    print(f"      Found {review_summary['review_count']} matching reviews.\n")

    print("[4/4] Recommendation Agent: asking Gemini to reason over price + reviews...")
    recommendation = get_recommendation(query, scored_candidates, review_summary)
    print("      Done.\n")

    return {
        "query": query,
        "candidates": scored_candidates,
        "review_summary": review_summary,
        "recommendation": recommendation,
    }


def print_summary(result):
    print("=" * 60)
    print(f"RESULTS FOR: {result['query']}")
    print("=" * 60)

    ranked = result["recommendation"]["ranked_products"]
    candidates_by_id = {c["product_id"]: c for c in result["candidates"]}

    for entry in ranked:
        product = candidates_by_id.get(entry["product_id"])
        if not product:
            continue
        print(f"\n#{entry['rank']}: {product['title']}")
        print(f"   Rs.{product['price']}  |  {product['rating']} stars  |  {product['source']}")
        print(f"   Why: {entry['reasoning']}")

    print("\n" + "-" * 60)
    print("Overall reasoning:")
    print(result["recommendation"]["overall_reasoning"])
    print("=" * 60)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "wireless earbuds under 1000 rupees"
    result = run_pipeline(query)
    print_summary(result)

    with open("last_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n(Full result also saved to last_result.json)")