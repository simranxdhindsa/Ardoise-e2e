import { useEffect, useState } from 'react';
import type { RunMeta } from './types';
import { RunList } from './components/RunList';
import { RunDetail } from './components/RunDetail';

export function App() {
  const [runs, setRuns] = useState<RunMeta[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/runs')
      .then(r => r.json())
      .then((data: RunMeta[]) => {
        setRuns(data);
        if (data.length > 0) setSelected(data[0].timestamp); // auto-select newest
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const selectedMeta = runs.find(r => r.timestamp === selected) ?? null;

  return (
    <div className="app">
      <header className="app-header">
        <span style={{ fontSize: '20px' }}>🎭</span>
        <h1>Ardoise Test Reports</h1>
        {loading && <span style={{ color: 'var(--text-muted)', fontSize: '12px', marginLeft: 8 }}>Loading…</span>}
      </header>
      <div className="app-body">
        <RunList
          runs={runs}
          selected={selected}
          filter={filter}
          onSelect={setSelected}
          onFilter={setFilter}
        />
        {selectedMeta ? (
          <RunDetail meta={selectedMeta} />
        ) : (
          <div className="detail">
            <div className="detail-empty">
              {loading ? 'Loading runs…' : runs.length === 0
                ? 'No test runs found. Run `npm run pw:test` to generate a report.'
                : 'Select a run from the sidebar'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
