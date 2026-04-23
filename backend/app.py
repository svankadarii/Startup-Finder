import os
import threading
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from data_manager import DataManager
from claude_api import ClaudeAPI
from scrapers.yc_scraper import YCScraper
from scrapers.hn_scraper import HNScraper
from scrapers.product_hunt_scraper import ProductHuntScraper
from scrapers.linkedin_scraper import LinkedInScraper, reset_lookup_count
from scrapers.crunchbase_scraper import CrunchbaseScraper

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

data_manager = DataManager()
claude_api = ClaudeAPI()

# --- Scrape state (in-process, single-scrape-at-a-time) ----------------
_scrape_state = {
    "is_scraping": False,
    "progress": 0,
    "message": "Ready",
    "startups_found": 0,
    "new_added": 0,
    "last_run": None,
    "error": None,
}
_scrape_lock = threading.Lock()


def _run_scrapers():
    global _scrape_state

    def update(**kw):
        with _scrape_lock:
            _scrape_state.update(kw)

    update(is_scraping=True, progress=0, message="Initializing...", error=None, startups_found=0, new_added=0)
    reset_lookup_count()

    all_startups = []

    try:
        # 1. YC Directory (official public API) ---------------------------
        update(message="Scraping YC Directory...", progress=5)
        try:
            yc_results = YCScraper().scrape()
            all_startups.extend(yc_results)
            update(message=f"YC: {len(yc_results)} companies found.", progress=20)
        except Exception as e:
            print(f"[YC scraper error] {e}")
            update(message=f"YC error ({e}). Continuing...")

        # 2. Hacker News Show HN (free Algolia API) -----------------------
        update(message="Scraping Hacker News launches...", progress=25)
        try:
            hn_results = HNScraper().scrape()
            all_startups.extend(hn_results)
            update(message=f"HN: {len(hn_results)} launches found.", progress=40)
        except Exception as e:
            print(f"[HN scraper error] {e}")
            update(message=f"HN error ({e}). Continuing...")

        # 3. Product Hunt (requires PH_API_TOKEN in .env) -----------------
        try:
            ph_results = ProductHuntScraper().scrape()
            all_startups.extend(ph_results)
            update(message=f"Product Hunt: {len(ph_results)} launches found.", progress=55)
        except Exception as e:
            print(f"[PH scraper error] {e}")

        # 4. Crunchbase (requires CRUNCHBASE_API_KEY in .env) -------------
        try:
            cb_results = CrunchbaseScraper().scrape()
            all_startups.extend(cb_results)
            update(message=f"Crunchbase: {len(cb_results)} companies found.", progress=65)
        except Exception as e:
            print(f"[CB scraper error] {e}")

        update(startups_found=len(all_startups))

        # 5. LinkedIn follower lookup (capped at 30/run, 3-6s per req) ----
        li = LinkedInScraper()
        total = len(all_startups)
        for i, startup in enumerate(all_startups):
            if startup.get("linkedin_url") and startup.get("linkedin_followers") is None:
                followers = li.get_followers(startup["linkedin_url"])
                startup["linkedin_followers"] = followers
            startup["follower_range"] = data_manager.classify_followers(
                startup.get("linkedin_followers")
            )
            pct = 65 + int((i + 1) / max(total, 1) * 25)
            if i % 5 == 0:
                update(progress=min(pct, 90), message=f"LinkedIn lookup: {i+1}/{total}...")

        # 5. Persist ------------------------------------------------------
        update(message="Saving results...", progress=95)
        new_added = data_manager.merge_and_save(all_startups)

        update(
            is_scraping=False,
            progress=100,
            message=f"Done! {len(all_startups)} startups found, {new_added} new.",
            new_added=new_added,
            last_run=datetime.now().isoformat(),
        )

    except Exception as e:
        update(is_scraping=False, error=str(e), message=f"Scraping failed: {e}")


# --- API routes --------------------------------------------------------

@app.route("/api/startups", methods=["GET"])
def get_startups():
    startups = data_manager.get_all_startups()
    return jsonify({"success": True, "startups": startups, "count": len(startups)})


@app.route("/api/scrape-now", methods=["POST"])
def scrape_now():
    with _scrape_lock:
        if _scrape_state["is_scraping"]:
            return jsonify({"success": False, "message": "Already scraping", "status": _scrape_state})
    t = threading.Thread(target=_run_scrapers, daemon=True)
    t.start()
    return jsonify({"success": True, "message": "Scraping started", "status": _scrape_state})


@app.route("/api/scrape-status", methods=["GET"])
def scrape_status():
    with _scrape_lock:
        return jsonify(dict(_scrape_state))


@app.route("/api/analysis/<startup_id>", methods=["GET"])
def get_analysis(startup_id):
    """Return cached analysis for a startup, or {cached: false} if not yet analyzed."""
    cached = data_manager.get_analysis(startup_id)
    if cached:
        return jsonify({"cached": True, "analysis": cached})
    return jsonify({"cached": False, "analysis": None})


@app.route("/api/analyze-startup", methods=["POST"])
def analyze_startup():
    """
    Run a single Claude call covering research, hiring, contacts, and projects.
    Returns the cached result immediately if this startup was already analyzed.
    """
    body = request.get_json(force=True) or {}
    startup_id = body.get("startup_id", "")

    if not startup_id:
        return jsonify({"success": False, "error": "startup_id required"}), 400

    # Serve from cache — no API call
    cached = data_manager.get_analysis(startup_id)
    if cached:
        return jsonify({"success": True, "analysis": cached, "from_cache": True})

    # Call Claude once, cache forever
    startup_data = body.get("startup_data", {})
    result = claude_api.analyze_startup(startup_data)

    if "error" in result:
        return jsonify({"success": False, "error": result["error"]}), 500

    data_manager.save_analysis(startup_id, result)
    return jsonify({"success": True, "analysis": result, "from_cache": False})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify(data_manager.get_stats())


@app.route("/api/save-startup", methods=["POST"])
def save_startup():
    body = request.get_json(force=True) or {}
    startup_id = body.get("startup_id", "")
    if startup_id:
        data_manager.toggle_save(startup_id)
    return jsonify({"success": True})


@app.route("/api/update-notes", methods=["POST"])
def update_notes():
    body = request.get_json(force=True) or {}
    data_manager.update_notes(body.get("startup_id", ""), body.get("notes", ""))
    return jsonify({"success": True})


@app.route("/api/update-followers", methods=["POST"])
def update_followers():
    """Manual follower count override for a specific startup."""
    body = request.get_json(force=True) or {}
    startup_id = body.get("startup_id", "")
    followers = body.get("followers")
    if startup_id and followers is not None:
        from data_manager import _load, _save, STARTUPS_FILE
        data = _load(STARTUPS_FILE, {"startups": [], "last_scrape": None})
        for s in data["startups"]:
            if s.get("id") == startup_id:
                s["linkedin_followers"] = int(followers)
                s["follower_range"] = data_manager.classify_followers(int(followers))
                break
        _save(STARTUPS_FILE, data)
    return jsonify({"success": True})


if __name__ == "__main__":
    print("Starting Hidden Gem Startup Finder backend on http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
