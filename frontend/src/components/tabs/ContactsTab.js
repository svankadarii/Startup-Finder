import React, { useState } from 'react';

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  function copy() {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }
  return (
    <button className={`copy-btn ${copied ? 'copied' : ''}`} onClick={copy}>
      {copied ? '✓ Copied' : 'Copy'}
    </button>
  );
}

export default function ContactsTab({ analysis }) {
  if (!analysis) return null;

  return (
    <div className="tab-content">
      {/* Titles to target */}
      {analysis.contact_titles?.length > 0 && (
        <div className="section-card">
          <div className="section-card-title">Job Titles to Target</div>
          <ul className="bullet-list">
            {analysis.contact_titles.map((t, i) => <li key={i}>{t}</li>)}
          </ul>
        </div>
      )}

      {/* Search tips */}
      {analysis.contact_search_tips && (
        <div className="section-card">
          <div className="section-card-title">How to Find Them</div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text)', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
            {analysis.contact_search_tips}
          </p>
        </div>
      )}

      {/* Cold message template */}
      {analysis.cold_message_template && (
        <div className="section-card">
          <div className="section-card-title">Cold Message Template</div>
          <div className="message-template">{analysis.cold_message_template}</div>
          <div className="copy-btn-wrap">
            <CopyButton text={analysis.cold_message_template} />
          </div>
        </div>
      )}
    </div>
  );
}
