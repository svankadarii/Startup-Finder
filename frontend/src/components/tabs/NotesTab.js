import React, { useState, useEffect } from 'react';
import { api } from '../../api';

export default function NotesTab({ startup, onNotesChange }) {
  const [notes, setNotes] = useState(startup.user_notes || '');
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setNotes(startup.user_notes || '');
  }, [startup.id]);

  async function save() {
    setSaving(true);
    try {
      await api.updateNotes(startup.id, notes);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
      if (onNotesChange) onNotesChange(startup.id, notes);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="tab-content">
      <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
        Your private notes about {startup.name}. Saved locally to startups.json.
      </p>
      <textarea
        className="notes-textarea"
        placeholder={`Notes about ${startup.name}…\n\nE.g.:\n- Reached out to John on April 20\n- Building a dashboard demo this week\n- Follow up after their Series A closes`}
        value={notes}
        onChange={(e) => { setNotes(e.target.value); setSaved(false); }}
      />
      <div className="notes-save-row">
        {saved && <span className="notes-saved-msg">✓ Saved</span>}
        <button
          className="btn btn-primary"
          onClick={save}
          disabled={saving}
        >
          {saving ? 'Saving…' : 'Save Notes'}
        </button>
      </div>
    </div>
  );
}
