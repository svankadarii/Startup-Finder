"""
Product Hunt scraper — recent launches (past 7 days).

Uses Product Hunt's public GraphQL API.
A free developer token can be obtained at https://www.producthunt.com/v2/oauth/applications
Set PH_API_TOKEN in backend/.env, or the scraper will skip PH.
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

PH_TOKEN = os.environ.get("PH_API_TOKEN", "")
PH_GRAPHQL = "https://api.producthunt.com/v2/api/graphql"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Content-Type": "application/json",
    "Accept": "application/json",
}


class ProductHuntScraper:
    def scrape(self, days_back=7, limit=50):
        if not PH_TOKEN:
            print("[PH] PH_API_TOKEN not set — skipping Product Hunt scraper.")
            return []
        return self._query_graphql(days_back, limit)

    def _query_graphql(self, days_back, limit):
        posted_after = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
        query = """
        query($after: String, $postedAfter: DateTime) {
          posts(first: 50, postedAfter: $postedAfter, order: VOTES, after: $after) {
            edges {
              node {
                id
                name
                tagline
                description
                website
                url
                createdAt
                votesCount
                makers { name username }
                topics { edges { node { name } } }
                thumbnail { url }
              }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
        """
        headers = {**HEADERS, "Authorization": f"Bearer {PH_TOKEN}"}
        variables = {"postedAfter": posted_after}

        results = []
        cursor = None

        try:
            while len(results) < limit:
                if cursor:
                    variables["after"] = cursor
                resp = requests.post(
                    PH_GRAPHQL,
                    json={"query": query, "variables": variables},
                    headers=headers,
                    timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()

                if "errors" in data:
                    print(f"[PH GraphQL] Errors: {data['errors']}")
                    break

                posts = data.get("data", {}).get("posts", {})
                edges = posts.get("edges", [])
                for edge in edges:
                    node = edge.get("node", {})
                    parsed = self._parse_post(node)
                    if parsed:
                        results.append(parsed)

                page_info = posts.get("pageInfo", {})
                if not page_info.get("hasNextPage"):
                    break
                cursor = page_info.get("endCursor")

        except Exception as e:
            print(f"[PH] {e}")

        print(f"[PH] Found {len(results)} recent launches")
        return results

    def _parse_post(self, node):
        name = node.get("name", "").strip()
        if not name:
            return None

        website = node.get("website") or node.get("url") or ""
        topics = [
            e["node"]["name"]
            for e in (node.get("topics") or {}).get("edges", [])
        ]
        desc = node.get("tagline") or node.get("description") or ""

        return {
            "name": name,
            "description": desc[:300],
            "website": website,
            "founded_date": None,
            "funding_stage": "Unknown",
            "funding_amount": None,
            "team_size": None,
            "linkedin_url": "",
            "linkedin_followers": None,
            "follower_range": "unknown",
            "product_hunt_url": f"https://www.producthunt.com/posts/{node.get('id', '')}",
            "yc_batch": None,
            "industry": ", ".join(topics[:3]),
            "source": "Product Hunt",
            "scraped_date": None,
            "saved_by_user": False,
            "user_notes": "",
        }
