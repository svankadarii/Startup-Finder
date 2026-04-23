import json
import os
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
STARTUPS_FILE = os.path.join(DATA_DIR, "startups.json")
ANALYZED_FILE = os.path.join(DATA_DIR, "analyzed_startups.json")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load(path, default):
    _ensure_dir()
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _save(path, data):
    _ensure_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class DataManager:
    def classify_followers(self, followers):
        if followers is None:
            return "unknown"
        try:
            n = int(followers)
        except (TypeError, ValueError):
            return "unknown"
        if n == 0:
            return "unknown"
        if n < 250:
            return "early"
        if n <= 5000:
            return "hidden_gem"
        return "known"

    def get_all_startups(self):
        data = _load(STARTUPS_FILE, {"startups": [], "last_scrape": None})
        return data.get("startups", [])

    def merge_and_save(self, new_startups):
        data = _load(STARTUPS_FILE, {"startups": [], "last_scrape": None})
        existing = data.get("startups", [])

        index = {}
        for s in existing:
            key = self._dedup_key(s)
            index[key] = s

        added = 0
        today = datetime.now().strftime("%Y-%m-%d")
        for s in new_startups:
            key = self._dedup_key(s)
            if key in index:
                for k, v in s.items():
                    if v is not None and v != "" and k not in ("id", "saved_by_user", "user_notes"):
                        index[key][k] = v
            else:
                s.setdefault("id", str(uuid.uuid4())[:8])
                s.setdefault("saved_by_user", False)
                s.setdefault("user_notes", "")
                s["scraped_date"] = today
                index[key] = s
                added += 1

        data["startups"] = list(index.values())
        data["last_scrape"] = datetime.now().isoformat()
        _save(STARTUPS_FILE, data)
        return added

    def _dedup_key(self, s):
        name = (s.get("name") or "").lower().strip()
        website = (s.get("website") or "").lower().strip().rstrip("/")
        website = website.replace("https://", "").replace("http://", "").replace("www.", "")
        return f"{name}|{website}"

    def get_stats(self):
        data = _load(STARTUPS_FILE, {"startups": [], "last_scrape": None})
        startups = data.get("startups", [])
        return {
            "total_startups": len(startups),
            "hidden_gems_count": sum(1 for s in startups if s.get("follower_range") == "hidden_gem"),
            "early_stage_count": sum(1 for s in startups if s.get("follower_range") == "early"),
            "known_startups_count": sum(1 for s in startups if s.get("follower_range") == "known"),
            "last_scrape_time": data.get("last_scrape"),
        }

    def toggle_save(self, startup_id):
        data = _load(STARTUPS_FILE, {"startups": [], "last_scrape": None})
        for s in data["startups"]:
            if s.get("id") == startup_id:
                s["saved_by_user"] = not s.get("saved_by_user", False)
                break
        _save(STARTUPS_FILE, data)

    def update_notes(self, startup_id, notes):
        data = _load(STARTUPS_FILE, {"startups": [], "last_scrape": None})
        for s in data["startups"]:
            if s.get("id") == startup_id:
                s["user_notes"] = notes
                break
        _save(STARTUPS_FILE, data)

    # --- Analysis cache ---------------------------------------------------

    def get_analysis(self, startup_id):
        data = _load(ANALYZED_FILE, {"analyzed": {}})
        entry = data["analyzed"].get(startup_id)
        return entry.get("claude_response") if entry else None

    def save_analysis(self, startup_id, claude_response):
        data = _load(ANALYZED_FILE, {"analyzed": {}})
        data["analyzed"][startup_id] = {
            "analyzed_date": datetime.now().isoformat(),
            "claude_response": claude_response,
        }
        _save(ANALYZED_FILE, data)
