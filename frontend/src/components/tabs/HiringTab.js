import React from 'react';

function ScoreCircle({ score }) {
  const cls = score >= 70 ? 'high' : score >= 40 ? 'med' : 'low';
  return (
    <div className={`score-circle ${cls}`}>
      <span className="score-number">{score}</span>
      <span className="score-pct">%</span>
    </div>
  );
}

export default function HiringTab({ analysis }) {
  if (!analysis) return null;

  const score = typeof analysis.hiring_score === 'number' ? analysis.hiring_score : null;

  return (
    <div className="tab-content">
      {score !== null && (
        <div className="score-display">
          <ScoreCircle score={score} />
          <div>
            <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text)', marginBottom: 8 }}>
              Hiring Likelihood
            </div>
            {analysis.hiring_reasoning && (
              <p className="score-reasoning">{analysis.hiring_reasoning}</p>
            )}
          </div>
        </div>
      )}

      {analysis.best_time_to_reach && (
        <div className="section-card">
          <div className="section-card-title">Best Time to Reach Out</div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text)', lineHeight: 1.5 }}>
            {analysis.best_time_to_reach}
          </p>
        </div>
      )}
    </div>
  );
}
