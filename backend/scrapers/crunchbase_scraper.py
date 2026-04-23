"""
Crunchbase recent funding announcements scraper.

Strategy:
  1. If CRUNCHBASE_API_KEY is set, use the free Basic API.
  2. Otherwise, scrape Crunchbase's public search results page
     (limited data, but no auth required).
"""

import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

CB_API_KEY = os.environ.get("CRUNCHBASE_API_KEY", "")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

STAGE_MAP = {
    "seed": "Seed",
    "pre-seed": "Pre-Seed",
    "series_a": "Series A",
    "series_b": "Series B",
    "series_c": "Series C",
    "series_d": "Series D+",
    "angel": "Angel",
    "grant": "Grant",
    "venture": "Venture",
}


class CrunchbaseScraper:
    def scrape(self, limit=50):
        if CB_API_KEY:
            results = self._api_scrape(limit)
        else:
            results = self._web_scrape(limit)
        print(f"[Crunchbase] Found {len(results)} companies")
        return results

    # ------------------------------------------------------------------
    # Crunchbase Basic API (requires free account + API key)
    # ------------------------------------------------------------------
    def _api_scrape(self, limit):
        url = "https://api.crunchbase.com/api/v4/searches/organizations"
        cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        payload = {
            "field_ids": [
                "identifier", "short_description", "website_url",
                "linkedin", "funding_stage", "funding_total",
                "last_funding_type", "num_employees_enum",
                "founded_on", "categories",
            ],
            "predicate_filters": [
                {
                    "field_id": "last_funding_at",
                    "operator_id": "gte",
                    "values": [cutoff],
                }
            ],
            "sort": [{"field_id": "last_funding_at", "sort_direction": "desc"}],
            "limit": limit,
        }
        try:
            resp = requests.post(
                url,
                json=payload,
                params={"user_key": CB_API_KEY},
                headers={**HEADERS, "Content-Type": "application/json"},
                timeout=20,
            )
            resp.raise_for_status()
            entities = resp.json().get("entities", [])
            return [self._parse_api_entity(e) for e in entities if e]
        except Exception as e:
            print(f"[Crunchbase API] {e}")
            return []

    def _parse_api_entity(self, entity):
        props = entity.get("properties", {})
        name = (props.get("identifier") or {}).get("value", "")
        linkedin_url = ""
        if props.get("linkedin"):
            linkedin_url = props["linkedin"].get("value", "")

        stage_raw = props.get("last_funding_type") or props.get("funding_stage") or ""
        stage = STAGE_MAP.get(stage_raw.lower().replace(" ", "_"), stage_raw)

        funding_total = props.get("funding_total")
        funding_str = None
        if funding_total:
            value = funding_total.get("value_usd")
            if value:
                funding_str = self._format_funding(value)

        team_size = self._parse_headcount(props.get("num_employees_enum", ""))

        categories = props.get("categories") or []
        industry = ", ".join(c.get("value", "") for c in categories[:3])

        return {
            "name": name,
            "description": props.get("short_description", "")[:300],
            "website": props.get("website_url", ""),
            "founded_date": props.get("founded_on"),
            "funding_stage": stage,
            "funding_amount": funding_str,
            "team_size": team_size,
            "linkedin_url": linkedin_url,
            "linkedin_followers": None,
            "follower_range": "unknown",
            "product_hunt_url": None,
            "yc_batch": None,
            "industry": industry,
            "source": "Crunchbase",
            "scraped_date": None,
            "saved_by_user": False,
            "user_notes": "",
        }

    # ------------------------------------------------------------------
    # Web scrape fallback
    # ------------------------------------------------------------------
    def _web_scrape(self, limit):
        results = []
        try:
            url = "https://www.crunchbase.com/discover/funding_rounds/e97e236cca8ef7cd50050fd6d1bb0e82"
            resp = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Crunchbase is JS-rendered so we get limited data
            cards = soup.select("[data-testid='funding-round-card']")
            for card in cards[:limit]:
                name_el = card.select_one("a[data-testid='company-name']")
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                href = name_el.get("href", "")
                website = f"https://www.crunchbase.com{href}" if href.startswith("/") else href

                desc_el = card.select_one("[data-testid='description']")
                desc = desc_el.get_text(strip=True) if desc_el else ""

                results.append({
                    "name": name,
                    "description": desc,
                    "website": website,
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
                    "source": "Crunchbase",
                    "scraped_date": None,
                    "saved_by_user": False,
                    "user_notes": "",
                })
                time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            print(f"[Crunchbase web] {e}")
        return results

    @staticmethod
    def _format_funding(usd):
        if usd >= 1_000_000_000:
            return f"${usd / 1_000_000_000:.1f}B"
        if usd >= 1_000_000:
            return f"${usd / 1_000_000:.1f}M"
        if usd >= 1_000:
            return f"${usd / 1_000:.0f}K"
        return f"${usd}"

    @staticmethod
    def _parse_headcount(enum_str):
        mapping = {
            "c_00001_00010": 5,
            "c_00011_00050": 25,
            "c_00051_00100": 75,
            "c_00101_00250": 150,
            "c_00251_00500": 350,
            "c_00501_01000": 750,
            "c_01001_05000": 2500,
            "c_05001_10000": 7500,
        }
        return mapping.get(enum_str)
