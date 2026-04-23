"""
Hacker News 'Show HN' scraper — uses the free HN Algolia API.
No API key or auth required.
Finds recent startup launches posted to Hacker News.
"""

import time
import re
import requests
from datetime import datetime, timedelta

HN_API = "https://hn.algolia.com/api/v1/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; StartupFinder/1.0)",
    "Accept": "application/json",
}

# --- Scraping limits -------------------------------------------------------
MAX_PAGES = 4           # 4 pages × 50 posts = up to 200 Show HN posts
DELAY_BETWEEN_PAGES = 1.0   # seconds between requests
DAYS_BACK = 30          # only look at posts from the last 30 days
REQUEST_TIMEOUT = 15

# Keywords that indicate a genuine product/startup launch
LAUNCH_KEYWORDS = [
    "launch", "built", "made", "created", "new startup", "my startup",
    "open source", "saas", "api", "tool", "app", "platform", "service",
    "product", "company", "startup", "software", "ai", "ml",
]

# Keywords that suggest it's NOT a startup (skip these)
SKIP_KEYWORDS = [
    "ask hn", "who is hiring", "freelancer", "book", "course", "tutorial",
    "seeking", "hired", "job", "resume",
]


def _looks_like_startup(title: str) -> bool:
    t = title.lower()
    if any(skip in t for skip in SKIP_KEYWORDS):
        return False
    return any(kw in t for kw in LAUNCH_KEYWORDS)


def _extract_company_name(title: str) -> str:
    """
    'Show HN: Acme – We built X' → 'Acme'
    'Show HN: I built X for Y'   → cleaned title
    """
    # Strip 'Show HN:' prefix
    name = re.sub(r'^show hn:\s*', '', title, flags=re.I).strip()
    # Take the part before common separators
    for sep in [' – ', ' - ', ': ', ' | ', ' — ']:
        if sep in name:
            name = name.split(sep)[0].strip()
            break
    # If it starts with "I " or "We " it's a description, not a name
    if re.match(r'^(I |We |My )', name, re.I):
        return title.replace('Show HN: ', '').strip()
    return name[:80]


def _extract_description(title: str) -> str:
    """Try to pull the description part after the company name separator."""
    clean = re.sub(r'^show hn:\s*', '', title, flags=re.I).strip()
    for sep in [' – ', ' - ', ': ', ' | ', ' — ']:
        if sep in clean:
            return clean.split(sep, 1)[1].strip()
    return clean


class HNScraper:
    def scrape(self, days_back=DAYS_BACK, max_pages=MAX_PAGES):
        cutoff_ts = int((datetime.utcnow() - timedelta(days=days_back)).timestamp())
        results = []

        for page in range(max_pages):
            batch = self._fetch_page(page, cutoff_ts)
            if not batch:
                break
            results.extend(batch)
            print(f"[HN] Page {page}: {len(batch)} startup launches (total {len(results)})")
            if page < max_pages - 1:
                time.sleep(DELAY_BETWEEN_PAGES)

        print(f"[HN] Done — {len(results)} launches scraped")
        return results

    def _fetch_page(self, page, cutoff_ts):
        try:
            resp = requests.get(
                HN_API,
                params={
                    "tags": "show_hn",
                    "hitsPerPage": 50,
                    "page": page,
                    "numericFilters": f"created_at_i>{cutoff_ts}",
                },
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code == 429:
                print("[HN] Rate limited — waiting 5s")
                time.sleep(5)
                return []
            resp.raise_for_status()

            hits = resp.json().get("hits", [])
            results = []
            for h in hits:
                title = h.get("title", "")
                if not title or not _looks_like_startup(title):
                    continue
                parsed = self._parse(h)
                if parsed:
                    results.append(parsed)
            return results

        except Exception as e:
            print(f"[HN] Page {page} error: {e}")
            return []

    def _parse(self, hit):
        title = hit.get("title", "")
        url = hit.get("url") or ""
        company_name = _extract_company_name(title)
        description = _extract_description(title)

        if not company_name or not url:
            return None

        # Skip HN links (not real startup websites)
        if "news.ycombinator.com" in url or "ycombinator.com" in url:
            return None

        return {
            "name": company_name,
            "description": description[:300],
            "website": url,
            "founded_date": None,
            "funding_stage": "Unknown",
            "funding_amount": None,
            "team_size": None,
            "linkedin_url": "",
            "linkedin_followers": None,
            "follower_range": "unknown",
            "product_hunt_url": None,
            "yc_batch": None,
            "industry": "",
            "source": "Hacker News",
            "scraped_date": None,
            "saved_by_user": False,
            "user_notes": "",
        }
