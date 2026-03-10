# Ardoise — Full Architecture & Codebase Reference
_Last updated: 2026-03-05. Source: full codebase exploration._

---

## 1. MONOREPO OVERVIEW

```
C:\dhindsa\Ardoise\
├── mission-control/     Next.js 12.3.1   Admin CMS — courses, bundles, orgs, publishing
├── studio-web/          Next.js 12.3.1   Author tool — project/asset creation, Weaver AI
├── ui/                  Next.js 15.1.0   Student platform — course consumption
├── e2e/                 Playwright        Unified test suite (root-level)
├── .env.e2e             gitignored        E2E credentials
└── package.json         Monorepo root     Playwright scripts only
```

### Shared Tech Stack
- **UI Framework**: Mantine v5.5.4 (all three apps)
- **Data Fetching**: TanStack React Query v4 (all three)
- **State**: Zustand (studio-web), Redux Toolkit (ui), plain React state (MC)
- **Styling**: Emotion + Mantine theme system
- **i18n**: react-i18next, JSON files in `/src/translations/`
- **Auth**: NextAuth (MC/Google SSO), bearer JWT (UI/SW)

---

## 2. STUDIO-WEB — Deep Reference

### Purpose
Content authoring tool. Instructors create "projects" (drafts of courses). Projects get reviewed, then published in Mission Control.

### Key Page Routes
```
/                                              Dashboard / project list
/project/new                                   Step 1: Create project (name, type, level)
/project/[uuid]/teaser                         Step 2: Upload teaser image/video
/project/[uuid]/information                    Step 3: Title, description, objectives, prerequisites, target audience
/project/[uuid]/outline                        Step 4: Plan section structure
/project/[uuid]/manual                         Step 5: Create sections + assets manually
/project/[uuid]/context                        Step 6: Upload knowledge base files
/project/[uuid]/section/[sId]/asset/[aId]      Edit individual asset
/project/[uuid]/section/[sId]/asset/[aId]/weaver  Weaver AI editor for asset
/create/project/[uuid]/weaver/                 Full-project Weaver AI editor
```

### Two Creation Modes

#### Guided / Manual Mode
- User fills forms at each step
- Creates sections manually
- Adds assets to each section manually
- Uploads resources (video/audio/PDF) to assets
- No AI involvement in content generation

#### Agentic / AI Mode (Weaver)
- Weaver is an AI chat editor built on SSE streaming
- User describes what they want; AI generates structure
- Actions Weaver can perform:
  - `update_meta` — updates asset title/description/type
  - `update_instructions` — updates asset instructions (what AI says to students)
  - `update_settings` — updates AI mode settings
- Actions stored in `sessionStorage` for cross-component communication
- UI: accordion panels — Details, Instructions, Resources, Settings
- API: `POST /api/projects/{uuid}/weaver/{conversationId}` (streaming SSE)
- `useGetWeaverBotHistory()` — fetches past conversation
- Weaver is available at both project-level and asset-level

### Asset Types (10 types)
Defined via `GET /a/course/projects/options` — the API is the source of truth.

| Key | Name | Has Resources | Player/Renderer | AI Interaction |
|-----|------|---------------|-----------------|----------------|
| `theory` | Theory | YES | Media player (video/audio/PDF/link) + TheoryAssistantBot right panel | AI answers questions about resource content |
| `transition` | Transition | YES | Media player only | None |
| `simulation` | Simulation | NO | External Unity/game engine (iframe/WebGL) | Feedback asset generated after completion |
| `reflection` | Reflection | NO | AI dialogue interface | Full AI chat conversation |
| `quiz` | Quiz | NO | Built-in Q&A renderer (multiple choice, true/false) | None |
| `pre-assessment` | Pre-Assessment | NO | AI dialogue interface | Full AI chat |
| `feedback` | Feedback | NO | AI-generated review of simulation performance | AI chat |
| `intro` | Introduction | NO | Avatar-based (Unity WebGL) | Avatar speaks intro |
| `explore` | Explore | NO | AI dialogue interface | Full AI chat |
| `welcome` | Welcome | NO | Avatar/text | Avatar speaks welcome |

### Resource / Board Types (8 types)
Resources are uploaded files or links attached to `theory` and `transition` assets.

| Key | MIME Type | Can Be Paired With | Notes |
|-----|-----------|-------------------|-------|
| `video` | video/mp4 | summary, audio, transcript | Primary content; HLS streaming supported |
| `audio` | audio/mp3, audio/wav, audio/m4a | summary, transcript | Standalone audio lesson |
| `pdf` | application/pdf | summary, audio | Document viewer |
| `link` | link-preview | summary | URL embed / preview card |
| `transcript` | text/plain | summary, audio | Text version of spoken content |
| `summary` | text/plain | audio | Short text summary |
| `scorm` | application/scorm | nothing | Standalone SCORM package; no pairing allowed |
| `explore` | — | — | Discovery content |

#### Pairing Rules
A "paired" resource is a companion that supplements the primary resource. Example: a video can have a matching audio track and transcript. Pairings are set via `resource.paired_with` field.

### Key API Endpoints (Studio-Web)
Base: `STUDIO_API_URL` (same core API, different path prefix `/a/course/projects`)

```
# Projects
POST   /a/course/projects                              Create project
GET    /a/course/projects                              List projects
GET    /a/course/projects/{id}                         Get project details
PATCH  /a/course/projects/{id}                         Update project metadata
PATCH  /a/course/projects/{id}/init                    Initialize structure (after creation)
DELETE /a/course/projects/{id}                         Delete project
PATCH  /a/course/projects/{id}/submit-for-review       Submit to reviewer
PATCH  /a/course/projects/{id}/withdraw-from-review    Withdraw from review
PATCH  /a/course/projects/{id}/meta                    Update meta fields
PATCH  /a/course/projects/{id}/details                 Update detail fields
PATCH  /a/course/projects/{id}/objectives              Update objectives
PATCH  /a/course/projects/{id}/target-audience         Update target audience
PATCH  /a/course/projects/{id}/prerequisites           Update prerequisites
PATCH  /a/course/projects/{id}/teaser                  Upload teaser image/video
POST   /a/course/projects/{id}/translate               Auto-translate project
PATCH  /a/course/projects/{id}/translate               Update translation
GET    /a/course/projects/options                       Get asset types, resource types, languages dict

# Sections
POST   /a/course/projects/{id}/section                 Create section
PATCH  /a/course/projects/{id}/section/{sId}           Update section
DELETE /a/course/projects/{id}/section/{sId}           Delete section
PATCH  /a/course/projects/{id}/section/{sId}/asset/reorder  Reorder assets

# Assets
POST   /a/course/projects/{id}/section/{sId}/asset                 Create asset
PATCH  /a/course/projects/{id}/section/{sId}/asset/{aId}           Update asset
DELETE /a/course/projects/{id}/section/{sId}/asset/{aId}           Delete asset
PATCH  /a/course/projects/{id}/section/{sId}/asset/{aId}/settings  Update settings
PATCH  /a/course/projects/{id}/section/{sId}/asset/{aId}/instructions  Update instructions

# Resources
POST   /a/course/projects/{id}/section/{sId}/asset/{aId}/resource               Upload resource
PUT    /a/course/projects/{id}/section/{sId}/asset/{aId}/resource/{rId}/replace  Replace resource
PATCH  /a/course/projects/{id}/section/{sId}/asset/{aId}/resource/{rId}/description  Update description
DELETE /a/course/projects/{id}/section/{sId}/asset/{aId}/resource/{rId}          Delete resource
POST   /a/course/projects/{id}/section/{sId}/asset/{aId}/resource/{rId}/check    Verify upload complete

# Knowledge Bases
POST   /a/course/projects/{id}/kb                      Create KB
GET    /a/course/projects/{id}/kb                      List KBs
PATCH  /a/course/projects/{id}/kb/{kbId}               Update KB
DELETE /a/course/projects/{id}/kb/{kbId}               Delete KB
GET    /a/course/projects/{id}/kb/{kbId}/files         List KB files
GET    /a/course/projects/{id}/kb/{kbId}/files/{fId}/chunks  Get file chunks
POST   /a/course/projects/{id}/kb/{kbId}/upload-file   Upload file to KB
POST   /a/course/projects/{id}/kb/{kbId}/check-file/{rId}  Verify KB file upload
POST   /a/course/projects/chunk/update                 Update chunk metadata

# Topics
POST   /a/course/projects/{id}/topics/bulk             Add topics
POST   /a/course/projects/{id}/topics/delete/bulk      Delete topics
POST   /a/course/projects/{id}/topics/update/bulk      Update topics
PATCH  /a/course/projects/{id}/topics/reorder          Reorder topics

# Weaver AI
POST   /api/projects/{id}/weaver/{conversationId}      Send message (streaming SSE)
GET    /api/projects/{id}/weaver/history               Get conversation history
```

### Key Files (Studio-Web)
```
src/pages/project/new/index.tsx                   Project creation form
src/pages/project/[uuid]/teaser/index.tsx         Teaser upload
src/pages/project/[uuid]/information/index.tsx    Project details
src/pages/project/[uuid]/manual/index.tsx         Sections + assets editor
src/pages/project/[uuid]/context/index.tsx        Knowledge base manager
src/features/courses/                             Course/project feature modules
src/features/asset-weaver/index.tsx               Weaver AI editor component
src/features/resources/                           Resource upload/management
src/api/hooks/projects.ts                         All project API hooks
src/api/hooks/course-studio.ts                    Course studio API hooks
src/store/                                        Zustand stores
```

---

## 3. MISSION CONTROL — Deep Reference

### Purpose
Admin CMS. Admins create/configure courses (independently of Studio), manage bundles, organisations, users, and publish content to learners.

### Key Page Routes
```
/courses                               Course list
/course/new                            Create course form
/course/[uuid]/overview                Course detail hub (publish button here)
/course/[uuid]/information             Objectives, prerequisites, skills/roles
/course/[uuid]/languages               Language management
/course/[uuid]/translations            Translation settings
/course/[uuid]/authorizations          Access control
/course/[uuid]/add-authorization-to-course  Add new authorization
/course/[uuid]/knowledge-bases         KB management
/bundles                               Bundle list
/bundle/new                            Create bundle
/bundle/[uuid]/overview                Bundle details
/bundle/[uuid]/courses                 Courses in bundle
/bundle/[uuid]/courses/add-course-to-bundle  Add course to bundle
/organisations                         Org list
/configurations                        System configs (bots, avatars, translations)
```

### Course Creation Form Fields
```
name                string    required    Course title (max 100 chars)
description         RichText  required    Course description (min 50 chars, Quill editor)
level               Select    optional    beginner / intermediate / advanced / expert
ai_assistant        Checkbox  optional    Enable AI chat assistant for students
ai_instructor       Checkbox  optional    Enable AI instructor mode
regular             Checkbox  optional    Regular course mode (standard delivery)
authorize_for_all   Checkbox  optional    Make public to all organisations
ardoise_intelligence Checkbox optional   Enable Ardoise Intelligence features
```

### Publish Flow (Detailed)
```
Step 1: Create course → POST /a/course
         Returns: { id: uuid, status: "draft" }

Step 2: Set main language
         PATCH /a/course/{id}/main-language
         Body: { id: languageId }
         Required before publish. Without this, publish button is blocked.

Step 3: Add sections + assets
         (Sections via MC or linked from Studio)
         At least 1 section with 1 asset required.

Step 4: Click Publish button on /course/[uuid]/overview
         PATCH /a/course/{id}/publish
         Status changes: "draft" → "published"

Step 5: Course is now visible to:
         - All orgs (if authorize_for_all=true)
         - Only authorised orgs/teams (if authorize_for_all=false)
```

### Language & Translation Flow
```
Add additional languages:
  PATCH /a/course/{id}/language
  Body: [{ id: languageId }, ...]
  Effect: creates language-specific versions of content

Set main language (required before publish):
  PATCH /a/course/{id}/main-language
  Body: { id: languageId }

Auto-translate all content:
  POST /a/course/{id}/translate
  Effect: AI translates all text fields to all added languages

Manual translation:
  PATCH /a/course/{id}/translate
  Body: { ... translation overrides ... }
```

### Re-indexing
```
POST /a/course/{id}/reindex

What it does:
  1. Rebuilds the course's search index (Elasticsearch/vector DB)
  2. Refreshes AI knowledge base embeddings
  3. Updates content cache for the AI assistant

When to use:
  - After bulk content changes
  - If AI assistant gives stale responses
  - If search results seem outdated
  - After uploading new knowledge base files
  - After translation updates
```

### Authorization Management
```
Page: /course/[uuid]/authorizations

Authorisation types:
  - organisation  → entire org gets access
  - team          → specific team within an org
  - role          → by role (admin / content-creator / learner)

Endpoints:
  GET    /a/course/{id}/authorizations          List current authorisations
  POST   /a/course/{id}/authorizations          Add authorisation
  PATCH  /a/course/{id}/authorizations          Update authorisation
  DELETE /a/course/{id}/authorizations/{authId} Revoke authorisation

Toggle public:
  PATCH /a/course/{id}
  Body: { authorize_for_all: true/false }
```

### Bundle Management
```
Bundles group related courses. Students see bundles on dashboard.

Create bundle:
  POST /a/bundles
  Body: { name, description, level, ... }

Add course to bundle:
  POST /a/bundles/{bundleId}/courses
  Body: { courseId }
  Constraint: course must be published first

Remove course from bundle:
  DELETE /a/bundles/{bundleId}/courses/{courseId}
  Constraint: cannot remove published courses from active bundles

Bundle status:
  draft → published → archived

Endpoints:
  GET    /a/bundles                              List bundles
  POST   /a/bundles                              Create bundle
  GET    /a/bundles/{id}                         Get bundle
  PATCH  /a/bundles/{id}                         Update bundle
  DELETE /a/bundles/{id}                         Delete bundle
  POST   /a/bundles/{id}/courses                 Add course
  DELETE /a/bundles/{id}/courses/{courseId}      Remove course
```

### Key API Endpoints (Mission Control)
```
# Courses
POST   /a/course                               Create course
GET    /a/course                               List courses (search, filter, paginate)
GET    /a/course/{id}                          Get course details
PATCH  /a/course/{id}                          Update course fields
DELETE /a/course/{id}                          Delete course
PATCH  /a/course/{id}/publish                  Publish / unpublish toggle
PATCH  /a/course/{id}/archive                  Archive / unarchive toggle
PATCH  /a/course/{id}/override                 Override course from Studio project

# Content
PATCH  /a/course/{id}/objectives               Set learning objectives
PATCH  /a/course/{id}/prerequisites            Set prerequisites
PATCH  /a/course/{id}/skills-and-roles         Assign skills and job roles

# Languages
PATCH  /a/course/{id}/language                 Add language(s)
PATCH  /a/course/{id}/main-language            Set main language
POST   /a/course/{id}/translate                Auto-translate

# Knowledge Bases
POST   /a/course/{id}/knowledge-bases          Add KB
GET    /a/course/{id}/knowledge-bases          List KBs
DELETE /a/course/{id}/knowledge-bases/{kbId}   Remove KB

# Authorizations
GET    /a/course/{id}/authorizations           List
POST   /a/course/{id}/authorizations           Add
PATCH  /a/course/{id}/authorizations           Update
DELETE /a/course/{id}/authorizations/{authId}  Revoke

# Misc
POST   /a/course/{id}/reindex                  Reindex for search/AI
PATCH  /a/course/{id}/public-catalog           Toggle public catalog listing
PATCH  /a/course/featured                      Add to featured courses
DELETE /a/course/{id}/featured                 Remove from featured
GET    /a/course/{id}/ai/analytics             AI usage analytics

# Bundles
GET    /a/bundles                              List
POST   /a/bundles                              Create
GET    /a/bundles/{id}                         Get
PATCH  /a/bundles/{id}                         Update
DELETE /a/bundles/{id}                         Delete
POST   /a/bundles/{id}/courses                 Add course
DELETE /a/bundles/{id}/courses/{courseId}      Remove course
```

### Key Selectors (for tests)
```
RichText (Quill):   .ql-editor[contenteditable="true"]
Select dropdown:    .mantine-Select-input
Error messages:     [role="alert"], .mantine-InputWrapper-error
Name field:         getByLabel('Name') or input[name="name"]
Submit / Save:      getByRole('button', { name: /^save$/i })
Publish button:     getByRole('button', { name: /publish/i })
Delete button:      getByRole('button', { name: /delete/i })
Course name (overview appears TWICE): always use .first()
```

### Key Files (Mission Control)
```
src/pages/course/new/index.tsx             Course creation form
src/pages/course/[uuid]/overview.tsx       Course hub (publish, delete, status)
src/pages/course/[uuid]/languages.tsx      Language management
src/pages/course/[uuid]/authorizations.tsx Authorization management
src/pages/course/[uuid]/translations.tsx   Translation settings
src/pages/bundle/new.tsx                   Bundle creation
src/pages/bundle/[uuid]/overview.tsx       Bundle hub
src/features/course-studios/              Course feature modules
src/features/bundle-studio/               Bundle feature modules
src/api/hooks/course-studio.ts            Course API hooks
src/api/hooks/studio-projects.ts          Studio project hooks
src/components/RichText.tsx               Quill-based rich text editor
src/middleware.ts                          CSP headers + auth middleware
```

---

## 4. UI (STUDENT PLATFORM) — Deep Reference

### Purpose
End-user learning platform. Students browse assigned/available courses, preview course details, and consume course content through various AI-assisted modes.

### Key Page Routes
```
/                                                     Dashboard
/courses                                              Course catalogue
/courses/[courseId]                                   Course detail / preview page
/courses/[courseId]/section/[sId]/asset/[aId]         Asset viewer (course player)
/search                                               Search
/bookmarks                                            Saved bookmarks
/profile                                              User profile
/manage/courses                                       Learner's course management
/admin/users                                          User management (admin)
/admin/teams                                          Team management (admin)
/admin/branding                                       Branding config (admin)
/admin/skills                                         Skills management (admin)
/admin/job-roles                                      Job roles management (admin)
```

### Course Detail Page — What It Shows
```
- Course title, level badge, duration
- Description
- Start / Continue / Retake button (state-aware)
  - Not started → "Start Course" → creates progress record → navigates to first asset
  - In progress  → "Continue"    → navigates to last viewed asset
  - Completed    → "Retake"      → option to restart from beginning
- Progress percentage bar
- Course sections list with asset names
- Bookmark button (toggle)
- Enrolled learners count
```

### Three Viewing Modes

#### Text Mode (default)
```
selectedAiMode = "" (empty string)

What happens:
- Bot responses appear as text in right panel
- No audio generated
- No avatar
- Student types messages in text input

Components:
- Right panel: TheoryAssistantBot (for theory assets)
- Right panel: AudioHistoryTextStreams (for interactive assets)
- No microphone component rendered
```

#### Audio Mode
```
selectedAiMode = "audio" or "voice"

What happens:
- Bot responses are spoken via TTS (Text-to-Speech)
- Audio streamed in real-time (SSE/streaming)
- Transcript panel shows text alongside audio
- Student can optionally use microphone (speech-to-text)
- Audio controls appear in control bar (play/pause, volume, speed)

Components:
- LegacyAudio.tsx / ArdoiseIntelligenceAudio.tsx
- useStreamingAudio() hook for TTS streaming
- react-speech-recognition for microphone input
- Transcript panel on right side

When audio streaming starts:
  useStreamingAudio() → POST /o/pub/conversation (SSE)
  Bot text arrives → piped to TTS API → audio chunks streamed to browser
  useEffect in asset-preview pauses audio when assetId changes
```

#### Avatar Mode
```
selectedAiMode = "avatar"

What happens:
- Animated 3D avatar appears (Unity WebGL)
- Avatar speaks bot responses (synchronized lip sync)
- Student can speak to avatar via microphone
- Transcript panel also visible alongside avatar

Components:
- AvatarPlayerCard.tsx — Unity WebGL container
- AvatarActions.tsx — avatar state/action management
- react-unity-webgl — bridge to Unity engine
- SendMessageToUnity — sends text to Unity for lip sync
- isAvatarReady (Redux state) — avatar readiness check before starting
- Microphone via react-speech-recognition

Avatar flow:
  1. Check isAvatarReady === true
  2. Bot generates response text
  3. Text sent to TTS → audio generated
  4. Audio + text sent to Unity via SendMessageToUnity bridge
  5. Unity plays lip-synced animation + audio
  6. Student speaks → speech-recognition → text sent to bot
```

### Mode Switching Mechanism
```
Stored in: Redux state (appSlice.selectedAiMode) + localStorage

How to switch:
  dispatch(setSelectedAiMode('avatar')) // or 'audio' or ''
  saveState("selectedAiMode", mode)     // persists to localStorage

Effects of switching:
  1. Bot chat restarts (new conversation with new mode)
  2. Transcript panel visibility toggles
     if ['voice','avatar'].includes(mode) → dispatch(setIsTranscript(true))
     else                                 → dispatch(setIsTranscript(false))
  3. Currently playing audio/video is paused
     useEffect in asset-preview: mediaRef.current.pause() on mode change
  4. Mode persists between assets within the same session
```

### Asset Type → UI Behaviour

| Asset Type | Right Panel | Mode Available | Special Behaviour |
|------------|-------------|----------------|-------------------|
| `theory` | TheoryAssistantBot | text/audio/avatar | AI answers Qs about resources |
| `pre-assessment` | AudioHistoryTextStreams | text/audio/avatar | AI asks student questions |
| `simulation` | AudioHistoryTextStreams | text/audio/avatar | External game loads in iframe |
| `reflection` | AudioHistoryTextStreams | text/audio/avatar | AI reflects on student's learning |
| `feedback` | AudioHistoryTextStreams | text/audio/avatar | AI reviews simulation performance |
| `explore` | AudioHistoryTextStreams | text/audio/avatar | AI guides exploration |
| `welcome` | AudioHistoryTextStreams | text/audio/avatar | Avatar/bot welcomes student |
| `transition` | None | none | Just plays media, no AI |
| `quiz` | None | none | Renders Q&A form |
| `intro` | None | none | Avatar intro, no chat |

### Player → Component Mapping

| Resource Type | Component | Controls Available |
|---------------|-----------|-------------------|
| `video` | `VideoControls.tsx` + `video-player/` | Play/pause, seek bar, volume, resolution switching, fullscreen, playback speed |
| `audio` | `AudioControls.tsx` + `audio-player/` | Play/pause, seek bar, volume, playback speed (0.5x–2x) |
| `pdf` | `PdfControls.tsx` + `pdf-renderer/` | Page prev/next, page number input, zoom in/out, single/multi-page |
| `transcript` | `SummaryControls.tsx` | Scrollable text display |
| `summary` | `SummaryControls.tsx` | Scrollable text display |
| `scorm` | `ScormControls.tsx` | SCORM-specific (suspend/resume/complete) |
| `link` | Link preview component | Open in new tab button + embed preview |

### Control Bar (Bottom of Screen)
Component: `src/features/courses/control-bar/index.tsx`

```
Always visible:
  - Mode selector (text / audio / avatar)
  - Language selector
  - Settings gear (opens ContentModeSettings)
  - Accessibility options

Media-conditional:
  - Video: play/pause, progress bar, volume, resolution, fullscreen
  - Audio: play/pause, progress bar, volume, speed
  - PDF: page navigation, zoom level

Interactive asset:
  - Submit answer button
  - Restart button (post-completion)

Mic controls (audio/avatar mode only):
  - Mic enable/disable toggle
  - Speaking/listening indicator
  - Transcript toggle button
```

### Chat/Transcript Panel (Right Side)
```
Right panel content determined by:
  1. assetDetails.data.type.key  (asset type)
  2. selectedAiMode              (text/audio/avatar)

Decision logic:
  Interactive types [pre-assessment, simulation, reflection, feedback, explore, welcome, study]
    → AudioHistoryTextStreams  (full chat history with bot)

  Theory + any mode
    → TheoryAssistantBot  (theory-specific AI assistant)

  Other types [transition, quiz, intro]
    → null (no right panel)

AudioHistoryTextStreams features:
  - Displays full conversation history
  - Auto-scrolls to latest message
  - Shows user messages + bot responses
  - Streaming indicator (... animation) while bot is typing
  - Timestamps optional

TheoryAssistantBot features:
  - Answers questions specifically about the current resource content
  - Uses course knowledge base if available
  - Maintains context of what resource is currently being viewed
```

### Key API Endpoints (UI)
```
# Auth
POST   /o/auth/login                         Login
POST   /o/auth/token                         Refresh token
POST   /o/auth/revoke                        Logout
POST   /o/private/auth/social/login          Social login

# Dashboard
GET    /o/general/dashboard/courses          All available courses
GET    /o/general/dashboard/courses/assigned Assigned courses
GET    /o/general/dashboard/courses/completed Completed courses
GET    /o/general/dashboard/course/featured  Featured courses
GET    /o/general/dashboard/search           Search courses
GET    /o/general/dashboard/learner          Learner stats dashboard
GET    /o/general/dashboard/manager          Manager view dashboard

# Course Consumption
GET    /o/course                             Get course details (with sections/assets)
POST   /o/pub/conversation                   Start / continue AI conversation (SSE stream)
GET    /o/pub/conversation                   Get conversation history

# Progress
GET    /o/user/progress                      Get all progress records
POST   /o/user/progress/{courseId}           Create/update progress
PATCH  /o/user/progress/{courseId}           Update progress

# User
GET    /o/user/profile                       Get user profile
PATCH  /o/user/profile                       Update profile
GET    /o/settings/user-attributes           User attributes list
POST   /o/user/onboarding                    Set onboarding status

# Bookmarks
GET    /o/user/bookmarks                     List bookmarks
POST   /o/user/bookmarks                     Add bookmark
DELETE /o/user/bookmarks/{id}                Remove bookmark

# Manage Courses (admin in UI)
GET    /o/manage/course                      Manage course list
GET    /o/manage/team                        Team list
GET    /o/manage/brand                       Branding config
PATCH  /o/manage/brand                       Update branding

# Settings
GET    /o/settings/skills                    Skills list
GET    /o/settings/roles                     Job roles list
GET    /o/pub/brand                          Get public branding
```

### Key Files (UI)
```
src/pages/courses/[courseId]/index.tsx                         Course detail page
src/pages/courses/[courseId]/section/[sId]/asset/[aId]/index  Asset viewer
src/features/courses/details/                                  Course detail components
src/features/courses/control-bar/index.tsx                     Control bar
src/features/courses/control-bar/settings/ContentModeSettings  Mode switcher
src/features/courses/course-panels/CourseRightPanel.tsx        Right panel router
src/components/avatar/AvatarPlayerCard.tsx                     Avatar (Unity WebGL)
src/components/avatar/AvatarActions.tsx                        Avatar state mgmt
src/components/audio-player/                                   Audio playback
src/components/audio-streams/                                  Streaming TTS audio
src/components/video-player/index.tsx                          Video player (HLS)
src/components/pdf-renderer/                                   PDF viewer
src/components/chat-streams/AudioHistoryTextStreams.tsx         Chat history panel
src/components/chat-streams/TheoryAssistantBot.tsx             Theory AI panel
src/store/features/appSlice.ts                                 selectedAiMode, isTranscript, isAvatarReady
src/api/hooks/courses.ts                                       Course API hooks
src/api/hooks/bot-history.ts                                   Bot conversation hooks
src/api/env/dev.env.js                                         BASE_URL, CORE_URL, ARDOISE_DOMAIN
```

---

## 5. AUTHENTICATION ARCHITECTURE

### Mission Control (Google SSO via NextAuth)
```
Flow:
  User → /auth/signIn → clicks "Google" → Google OAuth → callback → NextAuth session created
  Cookies set:
    next-auth.session-token  (session identifier, HttpOnly)
    accessToken              (API bearer token)
    refreshToken             (for renewal)
    accessTokenExpires       (expiry timestamp)

SSR pages (getServerSideProps) check:
  next-auth.session-token → if missing/expired → redirect to /auth/signIn

E2E approach:
  global-setup opens headed browser → user clicks Google → full session saved via
  context.storageState() → mc-user.json includes ALL cookies including session-token
```

### UI / Studio-Web (Bearer JWT)
```
Flow:
  POST /o/auth/login { email, password, domain }
  Returns: { access_token, refresh_token, expires_in }
  Cookies set: accessToken, refreshToken, accessTokenExpires

E2E approach:
  Token injected directly from .env.e2e (PLAYWRIGHT_UI_TOKEN / PLAYWRIGHT_SW_TOKEN)
  global-setup builds storageState with token as cookie + localStorage
  Token format: JWT with { iss, id, email, locale, app, domain, exp, iat, sub }

Token fields:
  domain: "fnac"   (tenant/organisation)
  app:    "platform"
  locale: "eu"
```

### Token Refresh
```
All three apps: on 401 response, attempt refresh
  POST /o/auth/token with refreshToken
  On success: store new accessToken, retry original request
  On failure: redirect to login
```

---

## 6. INTEGRATION BETWEEN PRODUCTS

### Studio → Mission Control
```
CURRENT STATE: Independent systems — no direct API link.

Manual workflow:
  1. Author creates project in Studio-Web
  2. Author submits for review → PATCH /a/course/projects/{id}/submit-for-review
  3. Reviewer approves
  4. Admin in MC creates a new course manually
  5. Admin adds sections/assets to match Studio project content

Future (override endpoint exists):
  PATCH /a/course/{id}/override  → likely imports Studio project into MC course
```

### Mission Control → UI
```
Clear API integration:
  MC publishes course → status = "published"
  UI fetches /o/course (or /o/general/dashboard/courses) → returns published courses
  Student can access course only if:
    - authorize_for_all = true   OR
    - student's org/team is in course authorizations

Progress flows back:
  UI POST /o/user/progress/{courseId} → stored in backend
  MC GET /a/course/{id}/ai/analytics → shows aggregated analytics
```

### Shared Concepts
```
Languages:   Same language codes across all three apps
Asset types: Defined by core API (/a/course/projects/options), consumed by all apps
KBs:         Knowledge bases exist on both Studio projects and MC courses
Domain:      Multi-tenant (fnac, engie, contoso etc.) — each URL subdomain = domain
```
