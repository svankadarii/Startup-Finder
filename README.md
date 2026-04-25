# Hidden Gem Startup Finder

Discover funded startups with low LinkedIn followers — the sweet spot for cold outreach before they blow up.

Scrapes YC Directory and Hacker News for recent launches, enriches them with LinkedIn follower data, and uses Claude AI to generate research summaries, hiring signals, contact strategies, and project ideas for each company.

## What it does

- Scrapes **YC Directory** (official public API) and **Hacker News Show HN** posts for recent startups
- Optionally enriches with **Product Hunt** and **Crunchbase** data (requires API keys)
- Classifies companies by LinkedIn follower range:
  - **Hidden Gem** — 250–5,000 followers (prime cold outreach targets)
  - **Early** — under 250 followers
  - **Known** — over 5,000 followers
- One-click **Claude AI analysis** per startup covering:
  - Research summary
  - Hiring score + reasoning
  - Contact titles to target + cold message template
  - Pain points + project ideas for freelance/contract work
- Filter by source, follower range, and funding stage
- Save favorites and add private notes

## Stack

- **Backend:** Python / Flask, BeautifulSoup, Anthropic Claude API
- **Frontend:** React 18, dark-themed SPA

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
python app.py
```

Runs on `http://localhost:5000`.

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

Runs on `http://localhost:3000`.

### 3. Scrape

Open the app and click **Scrape Now**. YC and HN data loads in ~30 seconds. LinkedIn follower lookups run in the background (capped at 30 per run to avoid blocks).

## Optional API keys

Add these to `backend/.env` to enable additional data sources:

| Key | Source | Where to get it |
|-----|--------|-----------------|
| `PH_API_TOKEN` | Product Hunt | [producthunt.com/v2/oauth/applications](https://www.producthunt.com/v2/oauth/applications) |
| `CRUNCHBASE_API_KEY` | Crunchbase | [data.crunchbase.com](https://data.crunchbase.com/docs/using-the-api) |

## Project structure

```
backend/
  app.py                  Flask API + scrape orchestration
  claude_api.py           Claude analysis (single cached call per startup)
  data_manager.py         JSON persistence + dedup logic
  scrapers/
    yc_scraper.py         YC public API
    hn_scraper.py         Hacker News Algolia API
    product_hunt_scraper.py
    crunchbase_scraper.py
    linkedin_scraper.py   Best-effort follower count lookup
  .env.example            Copy to .env and fill in keys

frontend/
  src/
    App.js                Main app shell + filter state
    api.js                Fetch helpers
    components/           Cards, detail modal, filter bar, tabs

data/                     Created at runtime (gitignored)
  startups.json           Scraped startup records
  analyzed_startups.json  Claude analysis cache
```

## Notes

- LinkedIn scraping is best-effort. LinkedIn aggressively blocks bots, so follower counts are often unavailable. You can manually set a follower count via the startup detail modal.
- Claude analysis results are cached permanently — each startup is only analyzed once, keeping API costs low.
- The app is for personal use / research. Respect each platform's terms of service.
