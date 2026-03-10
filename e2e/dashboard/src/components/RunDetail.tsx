import { useEffect, useState } from 'react';
import type { RunMeta, SpecGroup } from '../types';
import { parseResults } from '../utils/parseResults';
import { SummaryBar } from './SummaryBar';
import { TestRow } from './TestRow';

interface Props {
  meta: RunMeta;
}

export function RunDetail({ meta }: Props) {
  const [groups, setGroups] = useState<SpecGroup[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/runs/${meta.timestamp}/results`)
      .then(r => r.json())
      .then(data => {
        setGroups(parseResults(data));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [meta.timestamp]);

  if (loading) {
    return (
      <div className="detail">
        <div className="loading">Loading results…</div>
      </div>
    );
  }

  return (
    <div className="detail">
      <div className="detail-header">
        <div className="detail-title">{meta.label}</div>
        <SummaryBar meta={meta} ts={meta.timestamp} />
      </div>

      {groups.length === 0 && (
        <div className="no-runs">No test data found for this run.</div>
      )}

      {groups.map(group => {
        const passCount = group.tests.filter(t => t.status === 'passed' || t.status === 'expected').length;
        const failCount = group.tests.filter(t => t.status === 'failed' || t.status === 'unexpected' || t.status === 'timedOut').length;
        const label = group.file.replace(/\\/g, '/').split('/').slice(-3).join('/');

        return (
          <details key={group.file} className="spec-group" open={failCount > 0}>
            <summary>
              <span className="spec-file-name" title={group.file}>{label}</span>
              <span className="spec-counts">
                {failCount > 0 && <span style={{ color: 'var(--fail)' }}>❌ {failCount} </span>}
                <span style={{ color: 'var(--pass)' }}>✅ {passCount}</span>
                <span style={{ color: 'var(--text-muted)' }}> / {group.tests.length}</span>
              </span>
            </summary>
            {group.tests.map((test, i) => (
              <TestRow key={i} test={test} />
            ))}
          </details>
        );
      })}
    </div>
  );
}
