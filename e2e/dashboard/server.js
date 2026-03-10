/**
 * server.js  (CommonJS)
 * Serves the built React dashboard + exposes report data as REST API.
 *
 * Run: node e2e/dashboard/server.js
 * Open: http://localhost:4000
 */

const express  = require('express');
const fs       = require('fs');
const path     = require('path');

const app  = express();
const PORT = 4000;

// ── Paths ──────────────────────────────────────────────────────────────────
const E2E_DIR  = path.resolve(__dirname, '..');           // e2e/
const RUNS_DIR = path.join(E2E_DIR, 'reports', 'runs');
const DIST_DIR = path.join(__dirname, 'dist');            // built React app

// ── API: list all runs (newest first) ─────────────────────────────────────
app.get('/api/runs', (req, res) => {
  if (!fs.existsSync(RUNS_DIR)) {
    return res.json([]);
  }

  const entries = fs.readdirSync(RUNS_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => {
      const metaPath = path.join(RUNS_DIR, d.name, 'meta.json');
      try {
        return JSON.parse(fs.readFileSync(metaPath, 'utf8'));
      } catch {
        return { timestamp: d.name, label: d.name, passed: 0, failed: 0, skipped: 0, total: 0, durationMs: 0, products: [] };
      }
    })
    .sort((a, b) => b.timestamp.localeCompare(a.timestamp)); // newest first

  res.json(entries);
});

// ── API: results.json for a specific run ──────────────────────────────────
app.get('/api/runs/:ts/results', (req, res) => {
  const file = path.join(RUNS_DIR, req.params.ts, 'results.json');
  if (!fs.existsSync(file)) {
    return res.status(404).json({ error: 'Not found' });
  }
  res.json(JSON.parse(fs.readFileSync(file, 'utf8')));
});

// ── API: serve screenshot by absolute path ────────────────────────────────
app.get('/api/screenshot', (req, res) => {
  const filePath = req.query.path;
  if (!filePath || typeof filePath !== 'string') {
    return res.status(400).send('Missing path');
  }
  // Security: only allow files that exist and look like PNGs/JPEGs
  const ext = path.extname(filePath).toLowerCase();
  if (!['.png', '.jpg', '.jpeg', '.webp'].includes(ext)) {
    return res.status(400).send('Only image files allowed');
  }
  if (!fs.existsSync(filePath)) {
    return res.status(404).send('File not found');
  }
  res.sendFile(path.resolve(filePath));
});

// ── Static: Playwright HTML reports ──────────────────────────────────────
// GET /reports/:ts/html/index.html etc.
app.use('/reports', express.static(RUNS_DIR));

// ── Static: React app ─────────────────────────────────────────────────────
if (fs.existsSync(DIST_DIR)) {
  app.use(express.static(DIST_DIR));
  // SPA fallback
  app.get('*', (req, res) => {
    res.sendFile(path.join(DIST_DIR, 'index.html'));
  });
} else {
  app.get('/', (req, res) => {
    res.send(`
      <html><body style="font-family:monospace;padding:2rem;background:#1a1a2e;color:#e0e0e0;">
        <h2>🎭 Ardoise Test Dashboard</h2>
        <p style="color:#ff6b6b">React app not built yet.</p>
        <p>Run: <code style="background:#2d2d44;padding:4px 8px;border-radius:4px;">cd e2e/dashboard &amp;&amp; npm install &amp;&amp; npm run build</code></p>
        <p>Then restart this server.</p>
      </body></html>
    `);
  });
}

app.listen(PORT, () => {
  console.log(`\n🎭 Ardoise Test Dashboard`);
  console.log(`   http://localhost:${PORT}\n`);
  console.log(`   API: /api/runs`);
  console.log(`   Reports: /reports/{timestamp}/html/index.html`);
  if (!fs.existsSync(DIST_DIR)) {
    console.log(`\n⚠️  React app not built. Run:`);
    console.log(`   cd e2e/dashboard && npm install && npm run build\n`);
  }
});
