import React, { useState, useEffect, useCallback, useMemo } from 'react';
import './App.css';
import { api } from './api';
import Header from './components/Header';
import StatsRow from './components/StatsRow';
import FilterBar from './components/FilterBar';
import ScrapeProgress from './components/ScrapeProgress';
import StartupCard from './components/StartupCard';
import StartupDetail from './components/StartupDetail';

const DEFAULT_FILTERS = {
  search: '',
  followerRange: 'all',
  stage: 'all',
  sort: 'followers_asc',
};

function applyFilters(startups, filters, showSaved) {
  let list = [...startups];

  if (showSaved) {
    list = list.filter((s) => s.saved_by_user);
  }

  if (filters.search) {
    const q = filters.search.toLowerCase();
    list = list.filter(
      (s) =>
        (s.name || '').toLowerCase().includes(q) ||
        (s.description || '').toLowerCase().includes(q) ||
        (s.industry || '').toLowerCase().includes(q)
    );
  }

  if (filters.followerRange !== 'all') {
    list = list.filter((s) => s.follower_range === filters.followerRange);
  }

  if (filters.stage !== 'all') {
    list = list.filter(
      (s) => (s.funding_stage || '').toLowerCase() === filters.stage.toLowerCase()
    );
  }

  list.sort((a, b) => {
    switch (filters.sort) {
      case 'followers_asc': {
        const fa = a.linkedin_followers ?? Infinity;
        const fb = b.linkedin_followers ?? Infinity;
        return fa - fb;
      }
      case 'followers_desc': {
        const fa = a.linkedin_followers ?? -1;
        const fb = b.linkedin_followers ?? -1;
        return fb - fa;
      }
      case 'funding_date': {
        const da = a.scraped_date || '0';
        const db = b.scraped_date || '0';
        return db.localeCompare(da);
      }
      case 'team_asc': {
        const ta = a.team_size ?? Infinity;
        const tb = b.team_size ?? Infinity;
        return ta - tb;
      }
      case 'name_az':
        return (a.name || '').localeCompare(b.name || '');
      default:
        return 0;
    }
  });

  return list;
}

// Group filtered list into sections (hidden gems first, then early, then rest)
function groupByRange(list) {
  const gems = list.filter((s) => s.follower_range === 'hidden_gem');
  const early = list.filter((s) => s.follower_range === 'early');
  const others = list.filter(
    (s) => s.follower_range !== 'hidden_gem' && s.follower_range !== 'early'
  );
  return { gems, early, others };
}

export default function App() {
  const [startups, setStartups] = useState([]);
  const [stats, setStats] = useState(null);
  const [scrapeState, setScrapeState] = useState({ is_scraping: false, progress: 0, message: '' });
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [selectedStartup, setSelectedStartup] = useState(null);
  const [showSaved, setShowSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initial data load
  useEffect(() => {
    Promise.all([api.getStartups(), api.getStats()])
      .then(([startupsRes, statsRes]) => {
        setStartups(startupsRes.startups || []);
        setStats(statsRes);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Poll scrape status while scraping
  useEffect(() => {
    if (!scrapeState.is_scraping) return;
    const interval = setInterval(async () => {
      try {
        const status = await api.scrapeStatus();
        setScrapeState(status);
        if (!status.is_scraping) {
          // Reload data when done
          const [startupsRes, statsRes] = await Promise.all([
            api.getStartups(),
            api.getStats(),
          ]);
          setStartups(startupsRes.startups || []);
          setStats(statsRes);
        }
      } catch (e) {
        console.error(e);
      }
    }, 1500);
    return () => clearInterval(interval);
  }, [scrapeState.is_scraping]);

  const handleScrapeNow = useCallback(async () => {
    try {
      const res = await api.scrapeNow();
      setScrapeState(res.status || { is_scraping: true });
    } catch (e) {
      console.error(e);
    }
  }, []);

  const handleSave = useCallback((id, saved) => {
    setStartups((prev) =>
      prev.map((s) => (s.id === id ? { ...s, saved_by_user: saved } : s))
    );
    setStats((prev) =>
      prev
        ? {
            ...prev,
            saved_count: (prev.saved_count || 0) + (saved ? 1 : -1),
          }
        : prev
    );
  }, []);

  const handleNotesChange = useCallback((id, notes) => {
    setStartups((prev) =>
      prev.map((s) => (s.id === id ? { ...s, user_notes: notes } : s))
    );
    // Update selected startup in-place so Notes tab reflects change
    setSelectedStartup((prev) => (prev?.id === id ? { ...prev, user_notes: notes } : prev));
  }, []);

  const filtered = useMemo(
    () => applyFilters(startups, filters, showSaved),
    [startups, filters, showSaved]
  );

  const grouped = useMemo(() => groupByRange(filtered), [filtered]);

  const showingAll = filters.followerRange === 'all' && !showSaved;

  return (
    <div className="app-layout">
      <Header
        stats={stats}
        scrapeState={scrapeState}
        onScrapeNow={handleScrapeNow}
        showSaved={showSaved}
        onToggleSaved={() => setShowSaved((v) => !v)}
      />

      <StatsRow stats={stats} />

      <FilterBar
        filters={filters}
        onChange={setFilters}
        resultCount={filtered.length}
      />

      <ScrapeProgress scrapeState={scrapeState} />

      {loading ? (
        <div className="loading-state" style={{ padding: '80px 0' }}>
          <div className="spinner" style={{ width: 32, height: 32 }} />
          Loading startups…
        </div>
      ) : (
        <div className="cards-section">
          {filtered.length === 0 ? (
            <div className="cards-grid">
              <div className="empty-state">
                <div className="empty-state-icon">
                  {startups.length === 0 ? '🚀' : '🔍'}
                </div>
                <h3>
                  {startups.length === 0
                    ? 'No startups yet'
                    : 'No results match your filters'}
                </h3>
                <p>
                  {startups.length === 0
                    ? 'Click "Scrape Now" to discover hidden gem startups'
                    : 'Try adjusting your search or filters'}
                </p>
              </div>
            </div>
          ) : showingAll ? (
            <>
              {grouped.gems.length > 0 && (
                <>
                  <div className="section-label">🎯 Hidden Gems — {grouped.gems.length} companies</div>
                  <div className="cards-grid">
                    {grouped.gems.map((s) => (
                      <StartupCard key={s.id} startup={s} onClick={() => setSelectedStartup(s)} />
                    ))}
                  </div>
                </>
              )}
              {grouped.early.length > 0 && (
                <>
                  <div className="section-label" style={{ marginTop: 24 }}>
                    🌱 Early Stage — {grouped.early.length} companies
                  </div>
                  <div className="cards-grid">
                    {grouped.early.map((s) => (
                      <StartupCard key={s.id} startup={s} onClick={() => setSelectedStartup(s)} />
                    ))}
                  </div>
                </>
              )}
              {grouped.others.length > 0 && (
                <>
                  <div className="section-label" style={{ marginTop: 24 }}>
                    Other — {grouped.others.length} companies
                  </div>
                  <div className="cards-grid">
                    {grouped.others.map((s) => (
                      <StartupCard key={s.id} startup={s} onClick={() => setSelectedStartup(s)} />
                    ))}
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="cards-grid">
              {filtered.map((s) => (
                <StartupCard key={s.id} startup={s} onClick={() => setSelectedStartup(s)} />
              ))}
            </div>
          )}
        </div>
      )}

      {selectedStartup && (
        <StartupDetail
          startup={selectedStartup}
          onClose={() => setSelectedStartup(null)}
          onSave={handleSave}
          onNotesChange={handleNotesChange}
        />
      )}
    </div>
  );
}
