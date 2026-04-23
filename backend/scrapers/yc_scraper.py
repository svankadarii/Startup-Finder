"""
YC Directory scraper — uses the official public API at api.ycombinator.com.
No API key required. Respects rate limits with polite delays.
"""

import time
import requests

API_BASE = "https://api.ycombinator.com/v0.1/companies"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; StartupFinder/1.0)",
    "Accept": "application/json",
}

# --- Scraping limits -------------------------------------------------------
MAX_PAGES = 5          # 5 pages × ~20 companies = ~100 companies per run
DELAY_BETWEEN_PAGES = 1.5  # seconds between page requests
REQUEST_TIMEOUT = 15   # seconds


class YCScraper:
    def scrape(self, max_pages=MAX_PAGES):
        results = []
        for page in range(1, max_pages + 1):
            batch = self._fetch_page(page)
            if not batch:
                break
            results.extend(batch)
            print(f"[YC] Page {page}: {len(batch)} companies (total {len(results)})")
            if page < max_pages:
                time.sleep(DELAY_BETWEEN_PAGES)

        print(f"[YC] Done — {len(results)} companies scraped")
        return results

    def _fetch_page(self, page):
        try:
            resp = requests.get(
                API_BASE,
                params={"page": page},
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code == 429:
                print(f"[YC] Rate limited on page {page} — waiting 10s")
                time.sleep(10)
                resp = requests.get(API_BASE, params={"page": page},
                                    headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            companies = resp.json().get("companies", [])
            return [self._parse(c) for c in companies if c.get("name")]
        except Exception as e:
            print(f"[YC] Page {page} error: {e}")
            return []

    def _parse(self, c):
        desc = c.get("oneLiner") or ""
        if not desc and c.get("longDescription"):
            desc = c["longDescription"][:250]

        industries = c.get("industries") or []
        tags = c.get("tags") or []
        industry = ", ".join(industries[:2]) or ", ".join(tags[:2])

        return {
            "name": c.get("name", ""),
            "description": desc,
            "website": c.get("website") or "",
            "founded_date": None,
            "funding_stage": "Seed",
            "funding_amount": None,
            "team_size": c.get("teamSize"),
            "linkedin_url": "",
            "linkedin_followers": None,
            "follower_range": "unknown",
            "product_hunt_url": None,
            "yc_batch": c.get("batch") or "",
            "industry": industry,
            "source": "YC Directory",
            "scraped_date": None,
            "saved_by_user": False,
            "user_notes": "",
        }
