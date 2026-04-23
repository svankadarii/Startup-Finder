import React from 'react';

export default function OverviewTab({ startup, analysis }) {
  return (
    <div className="tab-content">
      {/* Always-visible static info */}
      {startup.description && (
        <div className="section-card">
          <div className="section-card-title">Description</div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text)', lineHeight: 1.6 }}>
            {startup.description}
          </p>
        </div>
      )}

      <div className="info-grid">
        {startup.funding_stage && (
          <div className="info-block">
            <div className="info-block-label">Funding Stage</div>
            <div className="info-block-value">{startup.funding_stage}</div>
          </div>
        )}
        {startup.funding_amount && (
          <div className="info-block">
            <div className="info-block-label">Raised</div>
            <div className="info-block-value">${startup.funding_amount.replace(/^\$/, '')}</div>
          </div>
        )}
        {startup.team_size && (
          <div className="info-block">
            <div className="info-block-label">Team Size</div>
            <div className="info-block-value">{startup.team_size} people</div>
          </div>
        )}
        {startup.founded_date && (
          <div className="info-block">
            <div className="info-block-label">Founded</div>
            <div className="info-block-value">{startup.founded_date.slice(0, 7)}</div>
          </div>
        )}
        {startup.industry && (
          <div className="info-block">
            <div className="info-block-label">Industry</div>
            <div className="info-block-value">{startup.industry}</div>
          </div>
        )}
        {startup.yc_batch && (
          <div className="info-block">
            <div className="info-block-label">YC Batch</div>
            <div className="info-block-value">{startup.yc_batch}</div>
          </div>
        )}
      </div>

      {/* Claude analysis — only shown after "Analyze" is clicked */}
      {analysis?.research_summary && (
        <div className="section-card" style={{ borderColor: 'var(--gem-border)' }}>
          <div className="section-card-title" style={{ color: 'var(--gem)' }}>
            ✦ Claude Analysis
          </div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text)', lineHeight: 1.6 }}>
            {analysis.research_summary}
          </p>
        </div>
      )}
    </div>
  );
}
