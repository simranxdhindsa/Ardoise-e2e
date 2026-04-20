# Ardoise E2E — Command Reference

All commands run from the **repo root**: `C:\dhindsa\Ardoise`

---

## Run Tests

```bash
# All 3 products (MC + UI + SW)
npm run pw:test

# One product at a time
npm run pw:test:mc           # Mission Control
npm run pw:test:ui           # UI (Student platform)
npm run pw:test:sw           # Studio-Web

# With browser visible (good for demos / debugging)
npm run pw:test:headed

# Step-through debugger
npm run pw:test:debug

# Playwright interactive GUI (pick tests, watch live)
npm run pw:ui
```

### Run a single spec file
```bash
npx playwright test --config=e2e/playwright.config.ts e2e/specs/mission-control/courses/course-create-full.spec.ts
npx playwright test --config=e2e/playwright.config.ts e2e/specs/ui/auth/login.spec.ts
npx playwright test --config=e2e/playwright.config.ts e2e/specs/studio-web/weaver/weaver.spec.ts
```

### Run by product + file
```bash
npx playwright test --config=e2e/playwright.config.ts --project=ui           e2e/specs/ui/courses/courses-list.spec.ts
npx playwright test --config=e2e/playwright.config.ts --project=mission-control e2e/specs/mission-control/courses/course-create-full.spec.ts
npx playwright test --config=e2e/playwright.config.ts --project=studio-web   e2e/specs/studio-web/projects/project-create.spec.ts
```

### Filter by test name (grep)
```bash
npx playwright test --config=e2e/playwright.config.ts --grep "course title is visible"
npx playwright test --config=e2e/playwright.config.ts --grep "login"
```

---

## Record New Tests (Codegen — pre-authenticated)

Browser opens **already logged in** — no manual login needed.

```bash
npm run pw:codegen:mc        # Mission Control
npm run pw:codegen:ui        # UI (Student platform)
npm run pw:codegen:sw        # Studio-Web
```

**Workflow:**
1. Run one of the above commands
2. Click through your flow in the browser
3. Playwright Inspector records every action as TypeScript
4. Close the Inspector → code auto-saved to `e2e/specs/recorded/recorded.spec.ts`
5. Tell Claude: *"add assertion for X, use CoursesPage POM, check accessibility"*
6. Claude refines it → move to the right folder → run it

---

## Reports & Dashboard

```bash
# Open Playwright built-in HTML report
npm run pw:report

# Open custom dashboard (http://localhost:4000) — Go backend
# Shows: run history, pass/fail/skip counts, per-test errors, screenshots, API logs
npm run pw:dashboard

# First-time dashboard setup (builds React app + starts Go server)
npm run pw:dashboard:build
```

### Dashboard dev mode (hot-reload React, Go API backend)

```bash
# Terminal 1 — Go API backend (port 4000):
cd e2e/dashboard/backend
go run .

# Terminal 2 — React dev server (port 5173, hot-reload):
cd e2e/dashboard/frontend
npm start          # or: npm run dev

# Open: http://localhost:5173
```

### Folder structure
```
e2e/dashboard/
  backend/          ← Go server (stdlib only, 0 deps)
    server.go
    go.mod
  frontend/         ← React + Vite
    src/
    package.json
    vite.config.ts
```

### Build backend binary (optional — faster startup than go run)
```bash
cd e2e/dashboard/backend
go build -o server .      # → server.exe on Windows
./server                  # or: server.exe
```
Requires Go 1.22+ (`go version` to check)

**Dashboard features:**
- Run history with timestamps
- Pass ✅ / Fail ❌ / Skip ⏭ counts per run
- Per-test error details + failure screenshots
- Console errors & API errors captured automatically
- Links to full Playwright trace files

---

## Visual Regression Snapshots

```bash
# Regenerate ALL visual baselines after intentional UI changes
npm run pw:update-snapshots

# Reset snapshots for one spec only:
# Delete: e2e/snapshots/[product]/[spec].spec.ts-snapshots/
# Then re-run the spec — new baseline is auto-created
```

---

## Error Capture (automatic — no action needed)

Every test automatically captures:

| Error Type | What it catches |
|-----------|----------------|
| Console errors | JS errors in browser DevTools |
| Uncaught exceptions | Crashes, unhandled promise rejections |
| Failed network requests | Timeouts, blocked resources, DNS failures |
| API 4xx / 5xx responses | Backend errors even when UI hides them |
| Request bodies | What was sent to the backend |
| Response snippets | What the API returned (first 300 chars) |

Errors appear in the **custom dashboard** under each test row and in `results.json` as `network-log.json` attachments.

---

## Rewrite / Refresh a Test

```bash
# Option 1: Record fresh from browser
npm run pw:codegen:ui         # or :mc / :sw
# → recorded to e2e/specs/recorded/recorded.spec.ts
# → tell Claude what to fix → Claude rewrites it cleanly

# Option 2: Tell Claude what changed
# "The course creation form now has a category dropdown — update the test"
# → Claude reads the existing spec + your description → rewrites it
```

---

## Auth Cache Management

Auth sessions are cached for 23 hours in `e2e/.auth/`.

```bash
# Force re-authentication (delete cache, next run will re-login)
rm e2e/.auth/mc-user.json    # Mission Control (requires Google login)
rm e2e/.auth/ui-user.json    # UI
rm e2e/.auth/sw-user.json    # Studio-Web

# Or delete all:
rm e2e/.auth/*.json
```

---

## Full Reference: All npm Scripts

| Script | What it does |
|--------|-------------|
| `npm run pw:install` | Install Playwright browsers (first time setup) |
| `npm run pw:test` | Run all tests, save report |
| `npm run pw:test:mc` | Run Mission Control tests |
| `npm run pw:test:ui` | Run UI tests |
| `npm run pw:test:sw` | Run Studio-Web tests |
| `npm run pw:test:headed` | Run all tests with browser visible |
| `npm run pw:test:debug` | Run in step-through debug mode |
| `npm run pw:ui` | Playwright interactive GUI |
| `npm run pw:report` | Open Playwright HTML report |
| `npm run pw:update-snapshots` | Regenerate visual baselines |
| `npm run pw:dashboard` | Start custom dashboard (port 4000) |
| `npm run pw:dashboard:build` | Build + start dashboard (first time) |
| `npm run pw:codegen:mc` | Record MC test (pre-authed) |
| `npm run pw:codegen:ui` | Record UI test (pre-authed) |
| `npm run pw:codegen:sw` | Record SW test (pre-authed) |
