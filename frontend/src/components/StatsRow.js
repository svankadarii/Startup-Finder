import React from 'react';

export default function StatsRow({ stats }) {
  if (!stats) return null;
  return (
    <div className="stats-row">
      <div className="stat-card">
        <span className="stat-icon">📊</span>
        <div className="stat-info">
          <span className="stat-value">{stats.total_startups ?? 0}</span>
          <span className="stat-label">Total</span>
        </div>
      </div>
      <div className="stat-card gem">
        <span className="stat-icon">🎯</span>
        <div className="stat-info">
          <span className="stat-value">{stats.hidden_gems_count ?? 0}</span>
          <span className="stat-label">No Public Funding</span>
        </div>
      </div>
      <div className="stat-card early">
        <span className="stat-icon">🌱</span>
        <div className="stat-info">
          <span className="stat-value">{stats.early_stage_count ?? 0}</span>
          <span className="stat-label">Seed / Angel</span>
        </div>
      </div>
      <div className="stat-card known">
        <span className="stat-icon">🌐</span>
        <div className="stat-info">
          <span className="stat-value">{stats.known_startups_count ?? 0}</span>
          <span className="stat-label">Series A+</span>
        </div>
      </div>
    </div>
  );
}
