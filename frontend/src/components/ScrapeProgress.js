import React from 'react';

export default function ScrapeProgress({ scrapeState }) {
  if (!scrapeState?.is_scraping && scrapeState?.progress !== 100) return null;
  const { progress, message, startups_found, new_added, error } = scrapeState;

  return (
    <div className="scrape-banner">
      {scrapeState.is_scraping && <div className="spinner" />}
      <div className="scrape-text">
        <div className="scrape-message">
          {error ? `❌ ${error}` : message}
          {startups_found > 0 && !scrapeState.is_scraping && (
            <span style={{ marginLeft: 10, color: 'var(--gem)', fontWeight: 600 }}>
              {new_added} new added
            </span>
          )}
        </div>
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>
      {!scrapeState.is_scraping && (
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', flexShrink: 0 }}>
          {progress}%
        </span>
      )}
    </div>
  );
}
