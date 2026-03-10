# Ardoise Project Memory
_Auto-maintained. Last updated: 2026-03-05_

## Quick Reference
- **Repo root**: `C:\dhindsa\Ardoise`
- **E2E tests**: `C:\dhindsa\Ardoise\e2e\`
- **Env file**: `C:\dhindsa\Ardoise\.env.e2e` (gitignored)
- **Auth cache**: `C:\dhindsa\Ardoise\e2e\.auth\` (mc-user.json, ui-user.json, sw-user.json)
- **Run GUI**: `npx playwright test --config=e2e/playwright.config.ts --ui` from repo root

## Three Products
| App | Folder | URL (dev) | Auth |
|-----|--------|-----------|------|
| Mission Control | `mission-control/` | https://mission-control.ardoirse.com | Google SSO (NextAuth) |
| Studio-Web | `studio-web/` | https://engie.ardoirse.com | fnac domain bearer token |
| UI (student) | `ui/` | https://engie.ardoirse.com | fnac domain bearer token |

## Critical Auth Notes
- **MC**: MUST use real browser Google login. global-setup opens headed browser, waits for user to click Google (2 min timeout), saves full session (next-auth.session-token + accessToken cookies). Cached 23h.
- **UI/SW**: Use `PLAYWRIGHT_UI_TOKEN` / `PLAYWRIGHT_SW_TOKEN` from .env.e2e (fnac domain JWT). Token injected directly as cookie. No browser needed.
- **NEVER** change code inside `mission-control/`, `studio-web/`, or `ui/` — only write inside `e2e/`

## Key Selectors (MC)
- RichText editor: `.ql-editor[contenteditable="true"]` (uses Quill/@mantine/rte)
- Select dropdown: `.mantine-Select-input`
- Error messages: `[role="alert"], .mantine-InputWrapper-error`
- Course name on overview appears TWICE (heading + detail card) → always use `.first()`

## Completed Tests
- `e2e/specs/mission-control/courses/course-create-full.spec.ts` — 18/18 passing
  - Form validation (6 tests), full lifecycle create→overview→delete (5 tests), edge cases (4 tests), courses list read-only (3 tests)

## Detailed Docs (read these before writing tests)
- `memory/architecture.md` — Full codebase: asset types, board types, API endpoints, page routes
- `memory/test-plan.md` — Complete GUI + API test plan for all three products

## Phase Status
| Phase | Status |
|-------|--------|
| 1 — Foundation (config, global-setup, fixtures) | ✓ Done |
| 2 — Migrate UI tests | Partial |
| 3 — Mission Control specs | In progress |
| 4 — Studio-Web specs | Not started |
| 5 — Full validation | Not started |
