# E-commerce Multi-Agent Shopping Assistant

A multi-agent system that searches products, compares prices, summarizes reviews,
and produces an explained recommendation.

## Status: Step 2 - Recommendation Agent added (standalone, no orchestration yet)

## Stack: 100% free

- **Gemini API** (Google) - free tier, 1,500 requests/day, no credit card
- **SerpAPI** - free tier, 100 searches/month, no credit card
- **Kaggle** Amazon Reviews dataset - free download

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # Mac/Linux
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your keys:
   ```
   cp .env.example .env
   ```
   - Get a Gemini key (free) at aistudio.google.com/app/apikey
   - Get a SerpAPI key (free tier) at serpapi.com

4. Test the search agent on its own:
   ```
   python search_agent.py
   ```
   You should see 5 real products printed with price, rating, and source.

5. Test the recommendation agent on its own:
   ```
   python recommendation_agent.py
   ```
   You should see JSON output ranking 3 sample earbuds with reasoning.

## Build order (do not skip ahead)

- [x] Step 1: `search_agent.py` - standalone SerpAPI call, works with no framework
- [x] Step 2: `recommendation_agent.py` - standalone Gemini call, ranks products with reasoning
- [ ] Step 3: Price comparison logic (group same product across sources)
- [ ] Step 4: Review summarizer agent (Amazon Reviews dataset + Gemini)
- [ ] Step 5: Wire steps 1-4 into a LangGraph graph
- [ ] Step 6: Simple frontend

## Why this order

Each piece is testable in isolation before it touches the agent framework.
If something breaks later, you'll know it's the orchestration, not the underlying logic.
