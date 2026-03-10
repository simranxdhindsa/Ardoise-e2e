export interface RunMeta {
  timestamp: string;   // "Mar-05-2026_02-30-PM"
  label: string;       // "Mar 05, 2026 — 2:30 PM"
  passed: number;
  failed: number;
  skipped: number;
  total: number;
  durationMs: number;
  products: string[];
}

export interface Attachment {
  name: string;        // "screenshot" | "trace" | "video"
  path: string;        // absolute Windows path
  contentType: string;
}

export interface TestResultItem {
  status: 'passed' | 'failed' | 'skipped' | 'timedOut' | 'interrupted';
  duration: number;    // ms
  error?: { message?: string; stack?: string };
  attachments: Attachment[];
}

export interface TestEntry {
  title: string;
  projectName: string;
  status: string;      // from test.status or first result
  duration: number;    // ms (sum of results)
  error?: string;
  screenshotPath?: string;
  tracePath?: string;
}

export interface SpecGroup {
  file: string;        // spec file path (relative to project root)
  tests: TestEntry[];
}
