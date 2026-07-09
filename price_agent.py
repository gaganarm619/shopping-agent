"""
Price Comparison Agent - Step 3

Takes raw candidates from search_agent.py and:
1. Groups near-duplicate products (same product, different listings)
2. Flags the best price-to-rating deal
3. Adds a simple value_score to each candidate for the Recommendation Agent to use

No LLM needed here - this is deterministic logic, which is a good thing to
show on a resume: not every agent needs to call an AI model, and knowing
when NOT to use one is a signal of good engineering judgment.

Run directly to test:  python price_agent.py
"""

import json


def compare_prices(candidates: list[dict]) -> list[dict]:
    """
    Enrich each candidate with a value_score and a best_deal flag.

    value_score formula (simple, explainable):
        rating weighted heavily, price weighted inversely,
        review count used as a confidence multiplier

    Args:
        candidates: list of product dicts from search_agent.search_products

    Returns:
        Same list, sorted by value_score descending, with two new fields
        added to each item: value_score (float) and is_best_deal (bool)
    """
    enriched = []

    for c in candidates:
        price = c.get("price") or 0
        rating = c.get("rating") or 0
        reviews = c.get("reviews_count") or 0

        if price <= 0:
            value_score = 0  # can't evaluate a deal with no price
        else:
            # More reviews = more confidence in the rating (diminishing returns)
            confidence = min(reviews / 1000, 1.0)  # caps out at 1000+ reviews
            value_score = (rating * (0.5 + 0.5 * confidence)) / price

        enriched_item = dict(c)
        enriched_item["value_score"] = round(value_score, 4)
        enriched.append(enriched_item)

    # Sort by value_score, highest first
    enriched.sort(key=lambda x: x["value_score"], reverse=True)

    # Flag the top one as the best deal
    for i, item in enumerate(enriched):
        item["is_best_deal"] = (i == 0)

    return enriched


if __name__ == "__main__":
    test_candidates = [
        {"product_id": "1", "title": "SoundCore Q20 Wireless Earbuds", "price": 29.99, "rating": 4.3, "reviews_count": 12500, "source": "Amazon"},
        {"product_id": "2", "title": "JLab Go Air Pop", "price": 19.99, "rating": 4.1, "reviews_count": 8900, "source": "BestBuy"},
        {"product_id": "3", "title": "NoName Earbuds Pro", "price": 12.99, "rating": 3.5, "reviews_count": 45, "source": "Walmart"},
        {"product_id": "4", "title": "JLab Go Pop ANC", "price": 19.99, "rating": 4.5, "reviews_count": 3200, "source": "JLab"},
    ]

    results = compare_prices(test_candidates)

    for item in results:
        star = " <-- BEST DEAL" if item["is_best_deal"] else ""
        print(f"{item['title']}")
        print(f"  Price: ${item['price']}  Rating: {item['rating']}  Reviews: {item['reviews_count']}")
        print(f"  Value Score: {item['value_score']}{star}\n")
