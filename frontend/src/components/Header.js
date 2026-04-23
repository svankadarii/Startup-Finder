import React from 'react';

function formatRelativeTime(isoString) {
  if (!isoString) return null;
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function Header({ stats, scrapeState, onScrapeNow, showSaved, onToggleSaved }) {
  const isScraping = scrapeState?.is_scraping;
  const lastRun = scrapeState?.last_run || stats?.last_scrape_time;
  const relTime = formatRelativeTime(lastRun);

  return (
    <header className="header">
      <div className="header-left">
        <div>
          <div className="header-title">
            Hidden <span>Gem</span> Startup Finder
          </div>
          {relTime && (
            <div className="header-meta">Last scrape: {relTime}</div>
          )}
        </div>
      </div>

      <div className="header-right">
        <button
          className={`btn btn-outline ${showSaved ? 'active' : ''}`}
          onClick={onToggleSaved}
        >
          ★ Saved {stats?.saved_count > 0 ? `(${stats.saved_count})` : ''}
        </button>

        <button
          className="btn btn-primary"
          onClick={onScrapeNow}
          disabled={isScraping}
        >
          {isScraping ? (
            <>
              <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
              Scraping…
            </>
          ) : (
            '⟳ Scrape Now'
          )}
        </button>
      </div>
    </header>
  );
}
