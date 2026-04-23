import React from 'react';

const FOLLOWER_OPTIONS = [
  { value: 'all', label: 'All Followers' },
  { value: 'hidden_gem', label: '🎯 Hidden Gems (250–5k)' },
  { value: 'early', label: '🌱 Early Stage (<250)' },
  { value: 'known', label: '🌐 Known (5k+)' },
  { value: 'unknown', label: '? No LinkedIn Data' },
];

const STAGE_OPTIONS = [
  { value: 'all', label: 'All Stages' },
  { value: 'Pre-Seed', label: 'Pre-Seed' },
  { value: 'Seed', label: 'Seed' },
  { value: 'Series A', label: 'Series A' },
  { value: 'Series B', label: 'Series B' },
  { value: 'Series C', label: 'Series C+' },
];

const SORT_OPTIONS = [
  { value: 'followers_asc', label: 'Followers: Low → High' },
  { value: 'followers_desc', label: 'Followers: High → Low' },
  { value: 'funding_date', label: 'Funding Date: Newest' },
  { value: 'team_asc', label: 'Team Size: Small first' },
  { value: 'name_az', label: 'Name A → Z' },
];

export default function FilterBar({ filters, onChange, resultCount }) {
  function set(key, value) {
    onChange({ ...filters, [key]: value });
  }

  return (
    <div className="filter-bar">
      <div className="search-wrap">
        <span className="search-icon">🔍</span>
        <input
          className="search-input"
          type="text"
          placeholder="Search name, industry, description…"
          value={filters.search}
          onChange={(e) => set('search', e.target.value)}
        />
      </div>

      <div className="filter-group">
        <span className="filter-label">Followers</span>
        <select
          className="filter-select"
          value={filters.followerRange}
          onChange={(e) => set('followerRange', e.target.value)}
        >
          {FOLLOWER_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <span className="filter-label">Stage</span>
        <select
          className="filter-select"
          value={filters.stage}
          onChange={(e) => set('stage', e.target.value)}
        >
          {STAGE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <span className="filter-label">Sort</span>
        <select
          className="filter-select"
          value={filters.sort}
          onChange={(e) => set('sort', e.target.value)}
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      <span className="filter-results">{resultCount} startup{resultCount !== 1 ? 's' : ''}</span>
    </div>
  );
}
