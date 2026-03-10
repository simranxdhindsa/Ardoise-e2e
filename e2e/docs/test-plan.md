# Ardoise — Complete Test Plan (GUI + API)
_Last updated: 2026-03-05_

---

## HOW TO RUN TESTS

```bash
# Open Playwright GUI (recommended — see tests run live)
cd C:\dhindsa\Ardoise
npx playwright test --config=e2e/playwright.config.ts --ui

# Run all tests headless
npx playwright test --config=e2e/playwright.config.ts

# Run one product only
npx playwright test --config=e2e/playwright.config.ts --project=mission-control
npx playwright test --config=e2e/playwright.config.ts --project=ui
npx playwright test --config=e2e/playwright.config.ts --project=studio-web

# Run one file
npx playwright test --config=e2e/playwright.config.ts e2e/specs/mission-control/courses/course-create-full.spec.ts

# View HTML report
npx playwright show-report e2e/reports/html
```

---

## WRITING NEW TESTS — WORKFLOW

1. **Describe the test in plain English** to Claude
   Example: "I want to test that when I add a language to a course, it appears in the languages list"
2. Claude writes the spec file in the correct folder
3. Open Playwright GUI → find the file → click Play
4. Watch it run live in the browser panel

---

## PHASE STATUS

| Phase | Files | Status |
|-------|-------|--------|
| Foundation | playwright.config.ts, global-setup.ts | ✓ Done |
| MC Course Create | course-create-full.spec.ts (18 tests) | ✓ Done |
| MC Bundles | bundle-create.spec.ts | Not started |
| MC Languages | languages.spec.ts | Not started |
| MC Authorizations | authorizations.spec.ts | Not started |
| MC Publish Flow | publish-flow.spec.ts | Not started |
| MC Navigation | navigation.spec.ts | Not started |
| Studio Project Create | project-create.spec.ts | Not started |
| Studio Asset Create | asset-create.spec.ts | Not started |
| Studio Weaver | weaver.spec.ts | Not started |
| UI Course Preview | course-preview.spec.ts | Not started |
| UI Asset Viewer modes | asset-viewer.spec.ts | Not started |
| UI Audio/Avatar mode | modes.spec.ts | Not started |
| API Contract Tests | api-*.spec.ts | Not started |

---

## MISSION CONTROL — TEST SPECS

### DONE: `e2e/specs/mission-control/courses/course-create-full.spec.ts`
18 tests. Form validation, full lifecycle (create→overview→delete), edge cases, list read-only.

---

### TODO: `e2e/specs/mission-control/courses/publish-flow.spec.ts`

**Flow being tested:** Course create → add language → publish → verify status → unpublish

```
GUI Tests:
  1. Publish button is DISABLED when course has no main language set
     - Navigate to /course/{uuid}/overview of a draft course with no language
     - Assert publish button is greyed out / has tooltip "Add language first"

  2. Publish button is DISABLED when course has no sections
     - Create course, set language, but add no sections
     - Assert publish button disabled

  3. Successful publish flow
     - Create course → set language → (sections already exist from fixture)
     - Click Publish
     - Assert: status badge changes from "draft" to "published"
     - Assert: confirmation notification appears
     - Assert: Publish button now shows "Unpublish"

  4. Unpublish a published course
     - Navigate to published course overview
     - Click Unpublish
     - Assert: status changes back to "draft"

  5. Published course appears in UI student platform
     - After publish, fetch /o/general/dashboard/courses from UI context
     - Assert course ID present in response

API Tests (using page.request / Playwright API context):
  A. POST /a/course — missing required fields
     Body: {} → expect 400 + error message about missing name

  B. POST /a/course — name exceeds 100 chars
     Body: { name: 'a'.repeat(101), ... } → expect 422 or 400

  C. PATCH /a/course/{id}/publish — course without main language
     → expect 400 + error: "main language required" or similar

  D. PATCH /a/course/{id}/publish — course without sections
     → expect 400 + error: "sections required"

  E. PATCH /a/course/{id}/publish — valid course
     → expect 200 + body.status === "published"

  F. PATCH /a/course/{id}/publish — already published (idempotency)
     → expect 200 (no error on double-publish)

  G. PATCH /a/course/{id}/publish — non-existent course ID
     → expect 404
```

---

### TODO: `e2e/specs/mission-control/courses/languages.spec.ts`

**Flow being tested:** Add language, set main language, auto-translate, verify

```
GUI Tests:
  1. Languages page loads with existing languages list
  2. "Add Language" button opens language picker modal
  3. Select a language → it appears in the languages table
  4. Set a language as "Main Language" → badge updates
  5. Auto-translate button triggers translation (assert API call made)
  6. Cannot publish without main language (verify UI block)
  7. Language selector on course detail shows added languages

API Tests:
  A. PATCH /a/course/{id}/language — valid language id
     Body: [{ id: "fr" }] → expect 200

  B. PATCH /a/course/{id}/language — invalid language id
     Body: [{ id: "xx-invalid" }] → expect 400 or 422

  C. PATCH /a/course/{id}/main-language — language not yet added to course
     → expect 400 (must add language before setting as main)

  D. PATCH /a/course/{id}/main-language — valid
     → expect 200 + verify main_language field updated

  E. POST /a/course/{id}/translate — course with no content
     → expect either 200 (no-op) or 400

  F. POST /a/course/{id}/translate — course with content in main language
     → expect 202 (async job) or 200 + verify translated fields exist
```

---

### TODO: `e2e/specs/mission-control/courses/authorizations.spec.ts`

**Flow being tested:** Add org authorization, verify access, revoke

```
GUI Tests:
  1. Authorizations page loads showing current list
  2. "Add Authorization" navigates to add form
  3. Select organization from dropdown → submit
  4. New org appears in authorizations list
  5. Revoke button removes org from list (with confirm modal)
  6. Toggle "Authorize for All" checkbox on course overview
     → assert authorize_for_all field updates

API Tests:
  A. POST /a/course/{id}/authorizations — valid org id
     → expect 201 + authorization object returned

  B. POST /a/course/{id}/authorizations — duplicate org (already authorized)
     → expect 409 or 400 (conflict)

  C. POST /a/course/{id}/authorizations — non-existent org id
     → expect 404 or 400

  D. DELETE /a/course/{id}/authorizations/{authId} — valid
     → expect 204 or 200

  E. DELETE /a/course/{id}/authorizations/{authId} — non-existent authId
     → expect 404

  F. GET /a/course/{id}/authorizations — verify list after add/remove
     → assert count changes correctly
```

---

### TODO: `e2e/specs/mission-control/bundles/bundle-create.spec.ts`

**Flow being tested:** Create bundle → add course → verify → delete

```
GUI Tests:
  1. Bundle list page loads at /bundles
  2. "Create Bundle" button navigates to /bundle/new
  3. Bundle creation form renders (name, description, level fields)
  4. Submit with empty name → shows validation error
  5. Successful bundle creation → redirects to /bundle/{uuid}/overview
  6. Bundle overview shows correct details
  7. Add Course button on /bundle/{uuid}/courses → opens course picker
  8. Select a published course → it appears in bundle courses list
  9. Cannot add draft/unpublished course to bundle
  10. Delete bundle → confirm modal → redirect to /bundles

API Tests:
  A. POST /a/bundles — valid body
     Body: { name: "Test Bundle", description: "..." }
     → expect 201 + id in response

  B. POST /a/bundles — missing name
     Body: {} → expect 400

  C. POST /a/bundles/{id}/courses — add published course
     → expect 201

  D. POST /a/bundles/{id}/courses — add draft course
     → expect 400 (course must be published)

  E. POST /a/bundles/{id}/courses — add already-added course
     → expect 409 (conflict / duplicate)

  F. DELETE /a/bundles/{id}/courses/{courseId} — valid
     → expect 204

  G. DELETE /a/bundles/{id} — valid
     → expect 204 or 200
```

---

### TODO: `e2e/specs/mission-control/courses/reindex.spec.ts`

```
GUI Tests:
  1. Re-index button visible on course overview
  2. Clicking Re-index shows loading state / spinner
  3. Success notification appears after reindex completes

API Tests:
  A. POST /a/course/{id}/reindex — valid course
     → expect 200 or 202 (async job)

  B. POST /a/course/{id}/reindex — non-existent course
     → expect 404

  C. POST /a/course/{id}/reindex — twice in quick succession
     → expect 200 both times (no lock error)
```

---

### TODO: `e2e/specs/mission-control/navigation/navigation.spec.ts`

```
GUI Tests:
  1. Sidebar renders with: Courses, Bundles, Organisations, Configurations
  2. Click Courses → navigates to /courses
  3. Click Bundles → navigates to /bundles
  4. Click Organisations → navigates to /organisations
  5. Click Configurations → navigates to /configurations
  6. Active nav item is highlighted
  7. Course detail breadcrumb shows: Courses > {course name}
  8. Logo click returns to dashboard/home
```

---

## STUDIO-WEB — TEST SPECS

### TODO: `e2e/specs/studio-web/projects/project-create.spec.ts`

**Flow being tested:** Create project (guided mode) through all steps

```
GUI Tests:

  STEP 1 — /project/new form:
  1. Form renders: Name, Type, Level, Description fields
  2. Submit empty → validation errors on Name and Type
  3. Fill Name, select Type, select Level, fill Description
  4. Submit → redirects to /project/{uuid}/teaser

  STEP 2 — Teaser (/project/{uuid}/teaser):
  5. Teaser page loads with upload dropzone
  6. Upload a small image → preview appears
  7. Can skip teaser → proceed to next step button
  8. Continue button navigates to /project/{uuid}/information

  STEP 3 — Information (/project/{uuid}/information):
  9. Title, Description, Objectives fields visible
  10. Fill all fields → save → success notification
  11. Navigate forward to next step

  STEP 4 — Manual editor (/project/{uuid}/manual):
  12. Empty section list shows "Add Section" button
  13. Add Section → section card appears with name input
  14. Fill section name → save
  15. Inside section: "Add Asset" button visible
  16. Add Asset of type "theory" → asset card appears
  17. Asset form shows: Name, Type selector
  18. Save asset → asset visible in section

API Tests:
  A. POST /a/course/projects — valid body
     Body: { name: "Test Project", level: "beginner", type: "..." }
     → expect 201 + { id: uuid }

  B. POST /a/course/projects — missing name
     Body: { level: "beginner" } → expect 400

  C. PATCH /a/course/projects/{id} — valid update
     → expect 200

  D. POST /a/course/projects/{id}/section — valid
     → expect 201 + section id

  E. POST /a/course/projects/{id}/section/{sId}/asset — type: "theory"
     → expect 201 + asset id

  F. POST /a/course/projects/{id}/section/{sId}/asset — invalid type key
     → expect 400

  G. DELETE /a/course/projects/{id} — valid cleanup
     → expect 204 or 200
```

---

### TODO: `e2e/specs/studio-web/projects/asset-create.spec.ts`

**Flow being tested:** All asset types, resource upload, verify

```
GUI Tests (per asset type):
  1. Create "theory" asset → upload video resource → verify preview appears
  2. Create "theory" asset → upload PDF resource → verify PDF preview
  3. Create "theory" asset → upload audio resource → verify audio player
  4. Create "theory" asset → add link resource → verify link preview
  5. Create "quiz" asset → verify no resource upload section shown
  6. Create "reflection" asset → verify instructions field present (no resources)
  7. Create "simulation" asset → verify external system note visible
  8. Resource upload shows progress bar
  9. Resource upload POST /check called after upload → "ready" state

API Tests:
  A. POST resource — valid video upload (multipart/form-data)
     → expect 201 + resource id

  B. POST resource — unsupported file type for theory asset
     → expect 400 (MIME type validation)

  C. POST resource/check — resource id that doesn't exist
     → expect 404

  D. POST resource/check — resource not yet processed
     → expect 200 with status: "processing"

  E. DELETE resource — valid
     → expect 204

  F. POST resource — for quiz asset (resources not allowed)
     → expect 400 or 405
```

---

### TODO: `e2e/specs/studio-web/weaver/weaver.spec.ts`

**Flow being tested:** Weaver AI editor — UI checks (read-only, no AI calls)

```
GUI Tests:
  1. Weaver page loads at /create/project/{uuid}/weaver/
  2. Accordion panels visible: Details, Instructions, Resources, Settings
  3. Chat input field is present and accepts text
  4. Project name visible in header
  5. Language selector shows current language
  6. Asset-level Weaver: /project/{uuid}/section/{sId}/asset/{aId}/weaver
     → same accordion panels visible
  7. Weaver history loads (previous conversations shown)
  8. Weaver input shows placeholder text

API Tests:
  A. GET weaver history — valid project + conversation id
     → expect 200 + array of messages

  B. GET weaver history — non-existent project
     → expect 404

  C. POST weaver message — check SSE content-type
     → expect Content-Type: text/event-stream

  D. POST weaver message — empty message body
     → expect 400

  E. POST weaver message — project not found
     → expect 404
```

---

### TODO: `e2e/specs/studio-web/navigation/navigation.spec.ts`

```
GUI Tests:
  1. Main nav renders: Projects, (Skills, Jobs if visible)
  2. Click Projects → /
  3. Project card click → navigates to /project/{uuid}/information or teaser
  4. Status filter (draft/in-review/published) filters list
  5. Search input narrows project list
  6. Pagination controls work (if >10 projects)
  7. "Create Project" / "Add Project" button navigates to /project/new
```

---

## UI (STUDENT PLATFORM) — TEST SPECS

### TODO: `e2e/specs/ui/courses/course-preview.spec.ts`

**Flow being tested:** Student views course detail page

```
GUI Tests:
  1. Navigate to /courses → course list loads
  2. Click a course card → navigates to /courses/{courseId}
  3. Course detail page shows: title, description, level badge
  4. "Start Course" button visible for not-started course
  5. Course sections list renders with section names
  6. Each section shows its asset names
  7. Progress bar shows 0% for new course
  8. Bookmark button is toggleable (add/remove bookmark)
  9. Course duration/metadata shown correctly
  10. Clicking "Start Course" navigates to first asset
  11. In-progress course shows "Continue" button instead
  12. Completed course shows "Retake" button

API Tests:
  A. GET /o/course?courseId={id} — valid published course
     → expect 200 + course object with sections array

  B. GET /o/course?courseId={id} — unpublished course
     → expect 403 or 404

  C. GET /o/course?courseId={id} — course not authorized for student's org
     → expect 403

  D. GET /o/general/dashboard/courses — authenticated request
     → expect 200 + array of course objects

  E. GET /o/general/dashboard/courses — unauthenticated (no token)
     → expect 401

  F. POST /o/user/bookmarks — add bookmark
     Body: { courseId }
     → expect 201

  G. DELETE /o/user/bookmarks/{id} — valid
     → expect 204

  H. DELETE /o/user/bookmarks/{id} — not-owned bookmark
     → expect 403
```

---

### TODO: `e2e/specs/ui/courses/asset-viewer.spec.ts`

**Flow being tested:** Student consumes a theory asset (video/audio/PDF)

```
GUI Tests:
  1. Navigate to /courses/{courseId}/section/{sId}/asset/{aId}
  2. Video asset: video player renders and plays
  3. Video asset: pause, seek, volume controls work
  4. Audio asset: audio player renders and plays
  5. PDF asset: PDF renders, page navigation works
  6. Right panel visible for theory asset (TheoryAssistantBot)
  7. Control bar visible at bottom of screen
  8. Asset name shown in top bar
  9. Prev/Next asset navigation buttons work
  10. Completing asset (video watches to end) shows completion indicator
  11. SCORM asset: renders in iframe

API Tests:
  A. POST /o/pub/conversation — start chat for theory asset
     Body: { courseId, assetId, key: "theory" }
     → expect 200 or 202 + conversationId

  B. POST /o/pub/conversation — invalid assetId
     → expect 404

  C. GET /o/pub/conversation?courseId={id}&assetId={id}
     → expect 200 + array of messages

  D. PATCH /o/user/progress/{courseId} — mark asset complete
     Body: { assetId, completed: true }
     → expect 200 + updated progress

  E. PATCH /o/user/progress/{courseId} — invalid assetId
     → expect 404 or 400
```

---

### TODO: `e2e/specs/ui/courses/modes.spec.ts`

**Flow being tested:** Switching between text / audio / avatar modes

```
GUI Tests:
  1. Mode selector in control bar shows: Text, Audio, Avatar options
  2. Default mode is Text — no audio playing, no avatar visible
  3. Switch to Audio mode:
     - Right panel updates (transcript visible)
     - Mic button appears in control bar
     - Audio player in right panel (TTS audio)
  4. Switch to Avatar mode:
     - Avatar container becomes visible
     - Mic button appears
     - Avatar readiness state checked before starting
  5. Switch back to Text — audio stops, avatar hidden
  6. Mode selection persists when navigating to next asset
  7. Mode selection persists on page reload (localStorage)

API Tests:
  A. POST /o/pub/conversation — with mode: "audio"
     → expect 200 + check response has audio_url or TTS fields

  B. POST /o/pub/conversation — with mode: "avatar"
     → expect 200 + check response for avatar-compatible data

  C. POST /o/pub/conversation — mode switch mid-conversation
     → expect 200 (new conversation starts, history preserved in UI)
```

---

### TODO: `e2e/specs/ui/auth/login.spec.ts`

```
GUI Tests:
  1. /auth/login renders email + password fields
  2. Submit empty → "Email required" and "Password required" errors
  3. Invalid email format → "Invalid email" error
  4. Valid credentials → redirect to dashboard
  5. Invalid credentials → "Invalid email or password" error
  6. Forgot password link visible and navigates to /auth/forgot-password
  7. "Remember me" checkbox visible
  8. SSO login button visible (if configured for domain)

API Tests:
  A. POST /o/auth/login — valid credentials
     → expect 200 + { access_token, refresh_token, expires_in }

  B. POST /o/auth/login — wrong password
     → expect 401 + error message

  C. POST /o/auth/login — non-existent email
     → expect 401 or 404

  D. POST /o/auth/login — missing email field
     → expect 400

  E. POST /o/auth/login — missing password field
     → expect 400

  F. POST /o/auth/login — SQL injection in email field
     Body: { email: "' OR '1'='1", password: "x" }
     → expect 400 or 401 (NOT 500 — no server crash)

  G. POST /o/auth/token — valid refresh token
     → expect 200 + new access_token

  H. POST /o/auth/token — expired refresh token
     → expect 401

  I. POST /o/auth/revoke — valid token
     → expect 200 or 204
```

---

## SECURITY & API CONTRACT TESTS

### TODO: `e2e/specs/ui/security/xss.spec.ts`

```
Tests that XSS payloads are sanitized and do NOT execute.

GUI Tests:
  1. Search input: enter <script>alert('xss')</script>
     → assert: alert never fires, input shows text escaped

  2. Course name field (MC): enter <img src=x onerror=alert(1)>
     → assert: saved as escaped text, no JS execution in UI

  3. User profile display name: enter <svg onload=alert(1)>
     → assert: rendered as text, no execution

  4. Chat input (AI panel): enter <script>document.cookie</script>
     → assert: bot response does not contain raw script tags

Console error check in all XSS tests:
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  // After test:
  expect(errors.filter(e => e.includes('XSS') || e.includes('script'))).toHaveLength(0);
```

---

### TODO: `e2e/specs/ui/security/auth-guards.spec.ts`

```
Tests that unauthenticated users cannot access protected routes.

GUI Tests:
  1. Navigate to /courses without auth → redirected to /auth/login
  2. Navigate to /courses/{id}/section/{s}/asset/{a} without auth → redirect
  3. Navigate to /admin/users without auth → redirect
  4. Direct navigate to /profile without auth → redirect

API Tests:
  A. GET /o/general/dashboard/courses — no Authorization header
     → expect 401

  B. GET /o/course — no Authorization header
     → expect 401

  C. GET /o/user/profile — expired token
     → expect 401

  D. PATCH /o/manage/brand — learner role (not admin)
     → expect 403

  E. DELETE /o/user/bookmarks/{id} — other user's bookmark id
     → expect 403 (IDOR prevention)
```

---

### TODO: `e2e/specs/ui/security/transport.spec.ts`

```
Tests that security headers are set correctly.

GUI Tests (response header checks via page.request):
  1. GET / → response headers include:
     - Content-Security-Policy (not empty)
     - X-Frame-Options or frame-ancestors in CSP
     - No Access-Control-Allow-Origin: * on authenticated endpoints

  2. POST /o/auth/login → response does NOT include:
     - Access-Control-Allow-Origin: * (credentials endpoint should not be open)

API Tests:
  A. GET /o/general/dashboard/courses — verify HTTPS used
     (test runner uses https:// URLs from .env.e2e)

  B. GET /o/auth/login — check Set-Cookie attributes:
     → accessToken cookie: HttpOnly should be false (client needs it)
     → refreshToken cookie: check SameSite=Lax
```

---

### TODO: `e2e/specs/mission-control/security/csp.spec.ts`

```
GUI Tests:
  1. Open MC app → inspect response headers
     → Content-Security-Policy header exists
     → default-src includes 'self'
     → script-src does NOT include 'unsafe-eval' in production

  2. No CSP violations in browser console during normal navigation
     const cspViolations = [];
     page.on('console', msg => {
       if (msg.text().includes('Content Security Policy')) {
         cspViolations.push(msg.text());
       }
     });
     // navigate through app
     expect(cspViolations).toHaveLength(0);

  3. iframe embedding of MC is blocked (frame-ancestors 'self')
```

---

## FULL END-TO-END PUBLISHING FLOW TEST

### TODO: `e2e/specs/e2e-flow/full-publish-flow.spec.ts`

This is the most important integration test — covers the entire journey.

```
PRE-CONDITION: MC auth cached, fnac token valid

STEP 1 (MC): Create course
  - Navigate to /course/new
  - Fill name, description, level
  - Submit → get courseId from URL

STEP 2 (MC): Add language
  - Navigate to /course/{courseId}/languages
  - Click Add Language → select English
  - Set as Main Language

STEP 3 (MC): Add section + asset
  (or verify that course overview shows sections already exist)

STEP 4 (MC): Publish
  - Navigate to /course/{courseId}/overview
  - Click Publish
  - Assert status badge = "published"

STEP 5 (UI): Verify course visible to student
  - Switch to UI project context
  - Navigate to /courses
  - Search for the course name
  - Assert course card appears

STEP 6 (UI): Preview course
  - Click the course card
  - Assert course detail page loads
  - Assert "Start Course" button visible

STEP 7 (MC): Unpublish + cleanup
  - Back in MC: click Unpublish → status = "draft"
  - Delete course → confirm → redirect to /courses

API Assertions Throughout:
  - Step 1: POST /a/course → 201
  - Step 2: PATCH /a/course/{id}/main-language → 200
  - Step 4: PATCH /a/course/{id}/publish → 200 + status: "published"
  - Step 5: GET /o/general/dashboard/courses → array includes courseId
  - Step 7: DELETE /a/course/{id} → 204
```

---

## TEST FILE LOCATIONS & PRIORITY

```
PRIORITY 1 (most critical — core flows):
e2e/specs/mission-control/courses/publish-flow.spec.ts
e2e/specs/mission-control/courses/languages.spec.ts
e2e/specs/ui/courses/course-preview.spec.ts
e2e/specs/e2e-flow/full-publish-flow.spec.ts

PRIORITY 2 (important features):
e2e/specs/mission-control/bundles/bundle-create.spec.ts
e2e/specs/mission-control/courses/authorizations.spec.ts
e2e/specs/studio-web/projects/project-create.spec.ts
e2e/specs/ui/courses/asset-viewer.spec.ts

PRIORITY 3 (extended coverage):
e2e/specs/ui/courses/modes.spec.ts
e2e/specs/studio-web/projects/asset-create.spec.ts
e2e/specs/studio-web/weaver/weaver.spec.ts
e2e/specs/ui/auth/login.spec.ts

PRIORITY 4 (security):
e2e/specs/ui/security/xss.spec.ts
e2e/specs/ui/security/auth-guards.spec.ts
e2e/specs/ui/security/transport.spec.ts
e2e/specs/mission-control/security/csp.spec.ts

PRIORITY 5 (navigation + read-only):
e2e/specs/mission-control/navigation/navigation.spec.ts
e2e/specs/studio-web/navigation/navigation.spec.ts
e2e/specs/mission-control/courses/reindex.spec.ts
```

---

## API TEST PATTERN (Playwright request context)

Use this pattern for all API-only tests inside spec files:

```typescript
import { test, expect } from '@playwright/test';

test.describe('API: POST /a/course', () => {
  let apiContext: APIRequestContext;
  let token: string;

  test.beforeAll(async ({ playwright }) => {
    // Read token from auth cache (set by global-setup)
    const authState = JSON.parse(fs.readFileSync('e2e/.auth/mc-user.json', 'utf-8'));
    token = authState.cookies.find(c => c.name === 'accessToken')?.value || '';

    apiContext = await playwright.request.newContext({
      baseURL: process.env.PLAYWRIGHT_MC_URL,
      extraHTTPHeaders: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
  });

  test.afterAll(async () => {
    await apiContext.dispose();
  });

  test('returns 201 with valid body', async () => {
    const res = await apiContext.post('/a/course', {
      data: { name: 'API Test Course', description: 'x'.repeat(50), level: 'beginner' }
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body.data?.id || body.id).toBeTruthy();
    // cleanup
    const id = body.data?.id || body.id;
    await apiContext.delete(`/a/course/${id}`);
  });

  test('returns 400 with missing name', async () => {
    const res = await apiContext.post('/a/course', {
      data: { description: 'x'.repeat(50) }
    });
    expect(res.status()).toBe(400);
    const body = await res.json();
    expect(body.errors || body.error?.message).toBeTruthy();
  });
});
```

---

## COMMON SELECTORS REFERENCE

```typescript
// Mission Control
'.ql-editor[contenteditable="true"]'     // RichText / Quill editor
'.mantine-Select-input'                  // Mantine select dropdown
'[role="alert"]'                         // Error/notification alerts
'.mantine-InputWrapper-error'            // Field-level error text
'.mantine-Notification-root'             // Toast notifications
'[data-testid]'                          // If data-testid attrs exist

// UI (student platform)
'.course-card'                           // Course listing cards (likely)
'[aria-label="Start Course"]'            // Start button
'[aria-label="Continue"]'                // Continue button
'.control-bar'                           // Bottom control bar
'.right-panel'                           // Chat/transcript panel

// Universal patterns
page.getByRole('button', { name: /submit/i })
page.getByRole('button', { name: /save/i })
page.getByRole('button', { name: /delete/i })
page.getByRole('button', { name: /publish/i })
page.getByLabel('Name')
page.getByLabel('Email')
page.getByLabel('Password')
page.getByPlaceholder('Search...')
```

---

## WHAT TO DO WHEN A TEST FAILS

1. **Open Playwright GUI** → find the failing test → click to see trace
2. **Network tab** in trace → look for 4xx/5xx API responses
3. **Console tab** → look for JavaScript errors
4. **DOM snapshots** → scrub through to see what was on screen
5. Common causes:
   - Selector changed → inspect element → update selector in page object
   - Auth expired → delete `e2e/.auth/*.json` → re-run global-setup
   - API returned unexpected data → check API test to isolate backend issue
   - Timeout → increase `timeout` in `test.use({})` or add explicit `waitFor`
