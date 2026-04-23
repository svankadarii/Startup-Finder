"""
LinkedIn follower count scraper.

Reality check: LinkedIn aggressively blocks automated access. This module
tries a lightweight approach first, then falls back gracefully.

For reliable follower data:
  - Use a LinkedIn partner API (paid)
  - Use a proxy rotation service (BrightData, Oxylabs)
  - Manually update counts via the /api/update-followers endpoint
"""

import re
import time
import random
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# Cache to avoid re-scraping the same URL
# --- Scraping limits -------------------------------------------------------
MIN_DELAY = 3.0   # minimum seconds between LinkedIn requests
MAX_DELAY = 6.0   # maximum seconds between LinkedIn requests
MAX_PER_SCRAPE = 30  # cap how many LinkedIn profiles we look up per scrape run
REQUEST_TIMEOUT = 12

_cache = {}
_lookup_count = 0  # reset each scrape run


def reset_lookup_count():
    global _lookup_count
    _lookup_count = 0


def _parse_follower_count(text):
    """Parse strings like '2,345 followers', '12K followers', '1.2M followers'."""
    if not text:
        return None
    text = text.lower().replace(",", "").replace(" ", "")
    match = re.search(r"([\d.]+)([km]?)\s*follower", text)
    if not match:
        return None
    num = float(match.group(1))
    suffix = match.group(2)
    if suffix == "k":
        num *= 1000
    elif suffix == "m":
        num *= 1_000_000
    return int(num)


class LinkedInScraper:
    def get_followers(self, linkedin_url):
        global _lookup_count
        if not linkedin_url:
            return None
        linkedin_url = linkedin_url.rstrip("/")

        # Return cached result immediately — no request needed
        if linkedin_url in _cache:
            return _cache[linkedin_url]

        # Hard cap: stop looking up LinkedIn after MAX_PER_SCRAPE per run
        if _lookup_count >= MAX_PER_SCRAPE:
            return None

        # Polite delay between every request
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        _lookup_count += 1

        count = self._try_scrape(linkedin_url)
        _cache[linkedin_url] = count
        return count

    def _try_scrape(self, url):
        try:
            resp = SESSION.get(url, timeout=15, allow_redirects=True)
            if resp.status_code == 999:
                # LinkedIn's bot-detection response code
                print(f"[LinkedIn] Bot detected for {url}")
                return None
            if resp.status_code != 200:
                print(f"[LinkedIn] HTTP {resp.status_code} for {url}")
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            # Attempt 1: meta description often has "X followers"
            meta = soup.find("meta", {"name": "description"})
            if meta:
                count = _parse_follower_count(meta.get("content", ""))
                if count is not None:
                    return count

            # Attempt 2: look for follower text in page body
            for tag in soup.find_all(["span", "p", "div"], string=re.compile(r"follower", re.I)):
                count = _parse_follower_count(tag.get_text())
                if count is not None:
                    return count

            # Attempt 3: look in JSON-LD structured data
            for script in soup.find_all("script", type="application/ld+json"):
                text = script.string or ""
                count = _parse_follower_count(text)
                if count is not None:
                    return count

        except requests.RequestException as e:
            print(f"[LinkedIn] Request error for {url}: {e}")

        return None
