import type { RunMeta } from '../types';

interface Props {
  runs: RunMeta[];
  selected: string | null;
  filter: string;
  onSelect: (ts: string) => void;
  onFilter: (f: string) => void;
}

export function RunList({ runs, selected, filter, onSelect, onFilter }: Props) {
  // Collect all unique products across all runs
  const allProducts = [...new Set(runs.flatMap(r => r.products))].sort();

  const filtered = filter === 'all'
    ? runs
    : runs.filter(r => r.products.includes(filter));

  return (
    <div className="sidebar">
      <div className="sidebar-header">All Runs ({filtered.length})</div>
      <div className="sidebar-filter">
        <select value={filter} onChange={e => onFilter(e.target.value)}>
          <option value="all">All Products</option>
          {allProducts.map(p => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>

      <div className="run-list">
        {filtered.length === 0 && (
          <div className="no-runs">
            <span>No runs found</span>
          </div>
        )}
        {filtered.map(run => {
          const dotClass = run.total === 0 ? 'empty' : run.failed > 0 ? 'fail' : 'pass';
          const isSelected = run.timestamp === selected;
          // Format short date label: "Mar 05 — 2:30 PM"
          const [datePart, timePart] = run.label.split(' — ');
          const shortDate = datePart.replace(/,\s*\d{4}/, ''); // "Mar 05"
          return (
            <div
              key={run.timestamp}
              className={`run-item ${isSelected ? 'selected' : ''}`}
              onClick={() => onSelect(run.timestamp)}
            >
              <span className={`run-dot ${dotClass}`} />
              <span className="run-item-label" title={run.label}>
                {shortDate}
                <br />
                <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>{timePart}</span>
              </span>
              <span className="run-item-counts">
                {run.failed > 0
                  ? <span style={{ color: 'var(--fail)' }}>❌{run.failed}</span>
                  : <span style={{ color: 'var(--pass)' }}>✅{run.passed}</span>}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
