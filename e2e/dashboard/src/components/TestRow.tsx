import { useState } from 'react';
import type { TestEntry } from '../types';

interface Props {
  test: TestEntry;
}

const ICON: Record<string, string> = {
  passed:      '✅',
  expected:    '✅',
  failed:      '❌',
  unexpected:  '❌',
  timedOut:    '⏱️',
  skipped:     '⏭️',
  interrupted: '⚡',
};

function fmtDur(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export function TestRow({ test }: Props) {
  const [expanded, setExpanded] = useState(false);
  const icon = ICON[test.status] ?? '❓';
  const hasFail = test.status === 'failed' || test.status === 'unexpected' || test.status === 'timedOut';
  const hasDetail = hasFail && (test.error || test.screenshotPath);

  const ssUrl = test.screenshotPath
    ? `/api/screenshot?path=${encodeURIComponent(test.screenshotPath)}`
    : null;

  return (
    <div className="test-row">
      <div
        className="test-row-header"
        onClick={() => hasDetail && setExpanded(e => !e)}
        style={{ cursor: hasDetail ? 'pointer' : 'default' }}
      >
        <span className="test-status-icon">{icon}</span>
        <span className="test-title" title={test.title}>{test.title}</span>
        {test.projectName && <span className="test-project">{test.projectName}</span>}
        <span className="test-dur">{fmtDur(test.duration)}</span>
      </div>

      {expanded && hasDetail && (
        <div className="test-detail">
          {test.error && (
            <div className="test-error">{test.error}</div>
          )}
          {ssUrl && (
            <div className="test-screenshot">
              <a href={ssUrl} target="_blank" rel="noreferrer">
                <img src={ssUrl} alt="failure screenshot" />
              </a>
            </div>
          )}
          <div className="test-links">
            {ssUrl && (
              <a className="test-link" href={ssUrl} target="_blank" rel="noreferrer">📷 Screenshot</a>
            )}
            {test.tracePath && (
              <span className="test-link" title={test.tracePath}>🔍 Trace (open via npx playwright show-trace)</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
