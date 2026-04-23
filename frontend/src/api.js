const BASE = '';  // proxied to localhost:5000 by CRA

async function req(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(BASE + path, opts);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  getStartups: () => req('GET', '/api/startups'),
  getStats: () => req('GET', '/api/stats'),
  scrapeNow: () => req('POST', '/api/scrape-now'),
  scrapeStatus: () => req('GET', '/api/scrape-status'),

  // Analysis — one call covers everything, results cached permanently
  getAnalysis: (startup_id) => req('GET', `/api/analysis/${startup_id}`),
  analyzeStartup: (startup_id, startup_data) =>
    req('POST', '/api/analyze-startup', { startup_id, startup_data }),

  saveStartup: (startup_id) => req('POST', '/api/save-startup', { startup_id }),
  updateNotes: (startup_id, notes) =>
    req('POST', '/api/update-notes', { startup_id, notes }),
  updateFollowers: (startup_id, followers) =>
    req('POST', '/api/update-followers', { startup_id, followers }),
};
