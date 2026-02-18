"""
Web app: input a GitHub repo URL (or owner/repo), clone it, run Python 3.12
keyword/builtin/dunder analytics, return JSON for the frontend to display.
Results are cached by normalized repo URL so repeat requests are instant.
"""

import hashlib
import json
import os
import subprocess
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request

from keyword_analytics import _normalize_repo_url, run_workflow_repo

app = Flask(__name__)

# Limit request size
app.config["MAX_CONTENT_LENGTH"] = 1024

CACHE_DIR = Path(__file__).resolve().parent / ".analytics_cache"
INDEX_HTML = open(os.path.join(os.path.dirname(__file__), "templates", "index.html")).read()


def _cache_key(repo: str) -> str:
    """Stable cache key from repo input (owner/repo or URL)."""
    url = _normalize_repo_url(repo)
    return hashlib.sha256(url.encode()).hexdigest()[:24]


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True, silent=True) or {}
    repo = (data.get("repo") or "").strip()
    if not repo:
        return jsonify({"error": "Missing 'repo'. Send e.g. { \"repo\": \"django/django\" }"}), 400
    key = _cache_key(repo)
    cache_path = CACHE_DIR / f"{key}.json"
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                return jsonify(json.load(f))
        except (json.JSONDecodeError, OSError):
            cache_path.unlink(missing_ok=True)
    try:
        result = run_workflow_repo(repo, timeout_seconds=90, max_files=30_000)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(result, f, indent=2)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Clone timed out. Try a smaller repo."}), 408
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
