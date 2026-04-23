import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import OverviewTab from './tabs/OverviewTab';
import ContactsTab from './tabs/ContactsTab';
import HiringTab from './tabs/HiringTab';
import ProjectsTab from './tabs/ProjectsTab';
import NotesTab from './tabs/NotesTab';

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'contacts', label: 'Contacts' },
  { id: 'hiring', label: 'Hiring' },
  { id: 'projects', label: 'Projects' },
  { id: 'notes', label: 'Notes' },
];

function formatFollowers(n) {
  if (n == null) return null;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return `${n}`;
}

const RANGE_CONFIG = {
  hidden_gem: { label: '🎯 Hidden Gem', cls: 'gem' },
  early: { label: '🌱 Early Stage', cls: 'early' },
  known: { label: '🌐 Known', cls: 'known' },
  unknown: { label: '? No LinkedIn Data', cls: 'unknown' },
};

export default function StartupDetail({ startup, onClose, onSave, onNotesChange }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [isSaved, setIsSaved] = useState(startup.saved_by_user || false);

  // Analysis state
  const [analysis, setAnalysis] = useState(null);
  const [checkingCache, setCheckingCache] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState(null);

  // On open: silently check if this startup was already analyzed
  useEffect(() => {
    api.getAnalysis(startup.id)
      .then((res) => {
        if (res.cached && res.analysis) {
          setAnalysis(res.analysis);
        }
      })
      .catch(() => {})
      .finally(() => setCheckingCache(false));
  }, [startup.id]);

  // Keyboard: Escape closes modal
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  // Lock body scroll
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  async function handleAnalyze() {
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const res = await api.analyzeStartup(startup.id, startup);
      if (!res.success) throw new Error(res.error || 'Analysis failed');
      setAnalysis(res.analysis);
    } catch (e) {
      setAnalyzeError(e.message);
    } finally {
      setAnalyzing(false);
    }
  }

  async function toggleSave() {
    try {
      await api.saveStartup(startup.id);
      const next = !isSaved;
      setIsSaved(next);
      if (onSave) onSave(startup.id, next);
    } catch (e) {
      console.error(e);
    }
  }

  function handleOverlayClick(e) {
    if (e.target === e.currentTarget) onClose();
  }

  const range = startup.follower_range || 'unknown';
  const rc = RANGE_CONFIG[range] || RANGE_CONFIG.unknown;
  const followers = formatFollowers(startup.linkedin_followers);

  // Tabs only relevant when analysis exists (except Notes which is always useful)
  const analysisTabIds = ['contacts', 'hiring', 'projects'];
  const tabsWithData = analysis
    ? TABS
    : TABS.filter((t) => !analysisTabIds.includes(t.id));

  const renderTabContent = useCallback(() => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab startup={startup} analysis={analysis} />;
      case 'contacts':
        return <ContactsTab analysis={analysis} />;
      case 'hiring':
        return <HiringTab analysis={analysis} />;
      case 'projects':
        return <ProjectsTab analysis={analysis} />;
      case 'notes':
        return <NotesTab startup={startup} onNotesChange={onNotesChange} />;
      default:
        return null;
    }
  }, [activeTab, startup, analysis, onNotesChange]);

  // If user was on an analysis-only tab and analysis just appeared, stay there
  useEffect(() => {
    if (!analysis && analysisTabIds.includes(activeTab)) {
      setActiveTab('overview');
    }
  }, [analysis]); // eslint-disable-line

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="detail-modal" role="dialog" aria-modal="true">

        {/* Header */}
        <div className="modal-header">
          <div className="modal-title-area">
            <div className="modal-company-name">{startup.name}</div>

            <div className="modal-badges">
              <span className={`modal-follower-badge ${rc.cls}`}>
                {rc.label}
                {followers && ` · ${followers} followers`}
              </span>
              {startup.yc_batch && (
                <span className="meta-tag">YC {startup.yc_batch}</span>
              )}
              {analysis && (
                <span style={{
                  fontSize: '0.7rem', background: 'var(--gem-bg)',
                  color: 'var(--gem)', border: '1px solid var(--gem-border)',
                  padding: '2px 8px', borderRadius: 20, fontWeight: 600
                }}>
                  ✦ Analyzed
                </span>
              )}
            </div>

            <div className="modal-info-row">
              {startup.funding_stage && <span>{startup.funding_stage}</span>}
              {startup.funding_amount && <span>${startup.funding_amount.replace(/^\$/, '')} raised</span>}
              {startup.team_size && <span>{startup.team_size} people</span>}
              {startup.founded_date && <span>Founded {startup.founded_date.slice(0, 7)}</span>}
              {startup.website && <a href={startup.website} target="_blank" rel="noreferrer">Website ↗</a>}
              {startup.linkedin_url && <a href={startup.linkedin_url} target="_blank" rel="noreferrer">LinkedIn ↗</a>}
              {startup.product_hunt_url && <a href={startup.product_hunt_url} target="_blank" rel="noreferrer">Product Hunt ↗</a>}
            </div>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        {/* Tabs */}
        <div className="modal-tabs">
          {tabsWithData.map((t) => (
            <button
              key={t.id}
              className={`tab-btn ${activeTab === t.id ? 'active' : ''}`}
              onClick={() => setActiveTab(t.id)}
            >
              {t.label}
              {t.id === 'notes' && startup.user_notes ? ' •' : ''}
            </button>
          ))}
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* Analyze CTA — shown until analysis is available */}
          {!checkingCache && !analysis && (
            <div style={{
              background: 'var(--surface-2)',
              border: '1px solid var(--gem-border)',
              borderRadius: 'var(--radius)',
              padding: '20px 24px',
              marginBottom: 20,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 16,
              flexWrap: 'wrap',
            }}>
              <div>
                <div style={{ fontWeight: 600, color: 'var(--text)', marginBottom: 4 }}>
                  Unlock full analysis
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  One Claude call → hiring score, contacts, pain points, project ideas. Cached permanently.
                </div>
                {analyzeError && (
                  <div className="error-state" style={{ marginTop: 10 }}>{analyzeError}</div>
                )}
              </div>
              <button
                className="btn btn-primary"
                onClick={handleAnalyze}
                disabled={analyzing}
                style={{ whiteSpace: 'nowrap', flexShrink: 0 }}
              >
                {analyzing ? (
                  <><span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Analyzing…</>
                ) : (
                  '✦ Analyze This Startup'
                )}
              </button>
            </div>
          )}

          {checkingCache ? (
            <div className="loading-state">
              <div className="spinner" />
              Checking cache…
            </div>
          ) : (
            renderTabContent()
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button
            className={`btn btn-save ${isSaved ? 'saved' : ''}`}
            onClick={toggleSave}
          >
            {isSaved ? '★ Saved' : '☆ Save to My List'}
          </button>
          <button className="btn btn-outline" onClick={onClose} style={{ marginLeft: 'auto' }}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
