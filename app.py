"""
Simple Web Frontend - Step 6

A minimal Flask app with one search box. Submitting a query runs the full
4-agent pipeline (orchestrator.py) and displays the ranked results.

The HTML/CSS/JS lives in templates/index.html - kept separate from this
file to keep both pieces small and simple.

Run:  python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template

from orchestrator import run_pipeline

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json()
    query = (data or {}).get("query", "").strip()

    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    try:
        result = run_pipeline(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
