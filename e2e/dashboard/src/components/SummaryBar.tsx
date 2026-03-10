import type { RunMeta } from '../types';

interface Props {
  meta: RunMeta;
  ts: string;
}

function fmt(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  const s = Math.round(ms / 100) / 10;
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  const sec = Math.round(s % 60);
  return `${m}m ${sec}s`;
}

export function SummaryBar({ meta, ts }: Props) {
  const reportUrl = `/reports/${ts}/html/index.html`;
  return (
    <div className="summary-bar">
      <span className="summary-chip chip-pass">✅ {meta.passed} passed</span>
      <span className="summary-chip chip-fail">❌ {meta.failed} failed</span>
      <span className="summary-chip chip-skip">⏭ {meta.skipped} skipped</span>
      <span className="summary-chip chip-dur">{fmt(meta.durationMs)}</span>
      {meta.products.map(p => (
        <span key={p} className="product-tag">{p}</span>
      ))}
      <a
        className="open-report-btn"
        href={reportUrl}
        target="_blank"
        rel="noreferrer"
      >
        Open Full Report ↗
      </a>
    </div>
  );
}
