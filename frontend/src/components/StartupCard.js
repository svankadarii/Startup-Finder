import React from 'react';

function formatFollowers(n) {
  if (n == null) return null;
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return `${n}`;
}

const BADGE_CONFIG = {
  hidden_gem: { label: '🎯 Hidden Gem', cls: 'badge-gem', followerCls: 'gem' },
  early: { label: '🌱 Early Stage', cls: 'badge-early', followerCls: 'early' },
  known: { label: '🌐 Known', cls: 'badge-known', followerCls: 'known' },
  unknown: { label: '? No Data', cls: 'badge-unknown', followerCls: 'unknown' },
};

export default function StartupCard({ startup, onClick }) {
  const range = startup.follower_range || 'unknown';
  const badge = BADGE_CONFIG[range] || BADGE_CONFIG.unknown;
  const followers = formatFollowers(startup.linkedin_followers);
  const cardCls = `startup-card ${range === 'hidden_gem' ? 'gem' : range === 'early' ? 'early' : ''}`;

  return (
    <div className={cardCls} onClick={onClick} role="button" tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}>

      <div className="card-top">
        <div className="card-name">{startup.name}</div>
        <span className={`card-badge ${badge.cls}`}>{badge.label}</span>
      </div>

      {startup.description && (
        <div className="card-desc">{startup.description}</div>
      )}

      <div className="card-meta">
        {startup.funding_stage && (
          <span className="meta-tag">{startup.funding_stage}</span>
        )}
        {startup.funding_amount && (
          <span className="meta-tag">${startup.funding_amount.replace(/^\$/, '')}</span>
        )}
        {startup.industry && (
          <span className="meta-tag">{startup.industry.split(',')[0].trim()}</span>
        )}
        {startup.yc_batch && (
          <span className="meta-tag">YC {startup.yc_batch}</span>
        )}
        {startup.team_size && (
          <span className="meta-tag">{startup.team_size} people</span>
        )}
      </div>

      <div className="card-bottom">
        <div className={`card-followers ${badge.followerCls}`}>
          {followers ? (
            <>
              <span>🔗</span>
              {followers} followers
            </>
          ) : (
            <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>No LinkedIn data</span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {startup.saved_by_user && <span className="saved-dot" title="Saved" />}
          <span className="card-source" title={startup.source}>{startup.source}</span>
        </div>
      </div>
    </div>
  );
}
