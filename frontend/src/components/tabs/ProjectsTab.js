import React from 'react';

export default function ProjectsTab({ analysis }) {
  if (!analysis) return null;

  const painPoints = analysis.pain_points || [];
  const projects = analysis.project_ideas || [];

  return (
    <div className="tab-content">
      {painPoints.length > 0 && (
        <div>
          <div className="section-card-title" style={{ paddingBottom: 8 }}>Pain Points</div>
          <div className="pain-points">
            {painPoints.map((pp, i) => (
              <div key={i} className="pain-point">
                <div className="pain-point-problem">
                  <span style={{ color: 'var(--accent)', marginRight: 6 }}>{i + 1}.</span>
                  {typeof pp === 'string' ? pp : pp.problem || JSON.stringify(pp)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {projects.length > 0 && (
        <div>
          <div className="section-card-title" style={{ paddingBottom: 8, marginTop: 8 }}>Project Ideas</div>
          <div className="project-cards">
            {projects.map((p, i) => (
              <div key={i} className="project-card">
                <div className="project-header">
                  <div className="project-title">{p.name}</div>
                  {p.build_time && (
                    <span className="project-tag">{p.build_time}</span>
                  )}
                </div>

                {p.description && (
                  <div className="project-desc">{p.description}</div>
                )}

                {p.solves_pain_point && (
                  <div className="project-why">
                    💡 Solves: {p.solves_pain_point}
                  </div>
                )}

                {p.tech_stack?.length > 0 && (
                  <div className="tech-chips" style={{ marginTop: 8 }}>
                    {p.tech_stack.map((t, j) => (
                      <span key={j} className="tech-chip">{t}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
