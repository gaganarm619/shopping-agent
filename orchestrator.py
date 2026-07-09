"""
Pipeline Orchestrator - Step 4

Connects the 3 agents into one flow:
  Search Agent -> Price Agent -> Recommendation Agent

This is a simple sequential orchestrator (no framework yet). It exists so
you can see and understand the full data flow with your own eyes before
wrapping it in LangGraph. Once you're comfortable with this, Step 5 will
convert this exact flow into a proper agent graph with parallel execution
and better state management.

Run directly to test:  python orchestrator.py "your search query"
"""

import sys
import json

from search_agent import search_products
from price_agent import compare_prices
from recommendation_agent import get_recommendation


def run_pipeline(query: str, num_results: int = 5) -> dict:
    """
    Run the full multi-agent pipeline for a shopping query.

    Args:
        query: natural language shopping query
        num_results: how many candidates to fetch from search

    Returns:
        dict with the full pipeline output: candidates, value-scored
        candidates, and the final AI recommendation
    """
    print(f"[1/3] Search Agent: searching for '{query}'...")
    candidates = search_products(query, num_results=num_results)
    if not candidates:
        raise RuntimeError("Search Agent returned no candidates. Check your SerpAPI key/quota.")
    print(f"      Found {len(candidates)} candidates.\n")

    print("[2/3] Price Agent: scoring candidates by value...")
    scored_candidates = compare_prices(candidates)
    best = next((c for c in scored_candidates if c["is_best_deal"]), None)
    print(f"      Best raw value score: {best['title']} (${best['price']})\n")

    print("[3/3] Recommendation Agent: asking Gemini to reason over the options...")
    recommendation = get_recommendation(query, scored_candidates)
    print("      Done.\n")

    return {
        "query": query,
        "candidates": scored_candidates,
        "recommendation": recommendation,
    }


def print_summary(result: dict) -> None:
    """Pretty-print the final pipeline result to the console."""
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
        print(f"   ${product['price']}  |  {product['rating']}★  |  {product['source']}")
        print(f"   Why: {entry['reasoning']}")

    print("\n" + "-" * 60)
    print("Overall reasoning:")
    print(result["recommendation"]["overall_reasoning"])
    print("=" * 60)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "wireless earbuds under $50"
    result = run_pipeline(query)
    print_summary(result)

    # Also dump raw JSON in case you want to feed it to a frontend later
    with open("last_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n(Full result also saved to last_result.json)")
