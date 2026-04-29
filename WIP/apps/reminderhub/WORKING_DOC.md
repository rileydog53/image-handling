# reminderhub — Working Document
> Phases 4 & 5: Frontend + Polish

---

## Current State (as of Phase 3 complete)

### What's working
- `POST /parse` — Gemini 2.5-flash extracts title, due_date, notes, type, tags from natural language
- `POST /create` — AppleScript creates Apple Reminders with correct date, notes, tag-based list routing
- Tag detection: `#Family`, `#family`, or plain "family mention" → routes to "Family" list (auto-created)
- Vite + React + TypeScript scaffolded, `/api` proxy to `localhost:8000` configured
- Backend deps in shared `.venv` at `Desktop/Claude/.venv`

### How to start the backend
```bash
cd /Users/josephardizzone/Desktop/Claude/WIP/apps/reminderhub/backend
/Users/josephardizzone/Desktop/Claude/.venv/bin/uvicorn main:app --reload --port 8000
```

### How to start the frontend
```bash
cd /Users/josephardizzone/Desktop/Claude/WIP/apps/reminderhub/frontend
npm run dev
# opens at http://localhost:5173
```

---

## Phase 4 — Frontend (the entire UI)

### Goal
Replace the Vite boilerplate with a minimal, clean UI: one textarea, a live preview card, and a Send button.

### Files to create/replace

| File | Status | What it does |
|------|--------|-------------|
| `src/types.ts` | Create | TypeScript interface for ParsedReminder |
| `src/hooks/useLiveParse.ts` | Create | Debounce + fetch + state management |
| `src/components/ReminderInput.tsx` | Create | Auto-growing textarea |
| `src/components/PreviewPanel.tsx` | Create | Live structured preview card |
| `src/components/SendButton.tsx` | Create | Disabled until title exists, calls /create |
| `src/App.tsx` | Replace boilerplate | Wire all components together |
| `src/App.css` | Replace boilerplate | Clean minimal styles |
| `src/index.css` | Replace boilerplate | Base reset + fonts |

---

### types.ts

```typescript
export interface ParsedReminder {
  title: string | null;
  due_date: string | null;   // ISO-8601 or null
  notes: string | null;
  type: "reminder" | "calendar";
  tags: string[] | null;
}
```

---

### useLiveParse.ts — key logic

- **500ms debounce** after each keystroke
- **In-flight guard**: if a request is already pending, skip the next debounce fire (rate limit protection)
- **AbortController**: cancel pending request if input is cleared
- Returns: `{ parsed, isLoading, error }`

```
input change
  → clear debounce timer
  → if isLoading: skip (guard)
  → set 500ms timer
    → on fire: setIsLoading(true)
    → fetch POST /api/parse { text }
    → setParsed(result)
    → setIsLoading(false)
```

---

### PreviewPanel — what to show

```
┌─ Live Preview ─────────────────────────────┐
│  Title:   Call mom                         │
│  When:    Wed Apr 29, 2026 · 3:00 PM       │
│  Notes:   —                                │
│  Tags:    [Family]                         │
│  Type:    [Reminder]                       │
└────────────────────────────────────────────┘
```

- Show placeholder "..." in each field while loading
- Format due_date as human-readable (not raw ISO string)
- Tags render as small pill/badge components
- Type badge: "Reminder" (blue) vs "Calendar Event" (purple)

---

### SendButton — behavior

- **Disabled** when: `parsed === null` OR `parsed.title === null` OR `isLoading`
- On click:
  1. `POST /api/create` with current `parsed` object
  2. On success: clear the textarea, clear parsed state, show brief "Added!" confirmation
  3. On error: show error message inline (not alert)

---

### App layout

```
┌─────────────────────────────────────────────────┐
│  ReminderHub                                    │
│  ─────────────────────────────────────────────  │
│  [ textarea: type your reminder...            ] │
│                                                 │
│  ┌─ Live Preview ──────────────────────────┐   │
│  │  Title:  Call mom                       │   │
│  │  When:   Wed Apr 29, 2026 · 3:00 PM     │   │
│  │  Notes:  —                              │   │
│  │  Tags:   [Family]                       │   │
│  │  Type:   [Reminder]                     │   │
│  └─────────────────────────────────────────┘   │
│                           [ Send to Apple  ]   │
└─────────────────────────────────────────────────┘
```

---

### Style notes
- Font: system-ui or Inter (no external font import needed for personal use)
- Background: light neutral (#f5f5f5 or similar)
- Preview card: white, subtle border-radius, light shadow
- Keep it tight — this is a utility app, not a portfolio piece

---

## Phase 5 — Polish

### P5-A: Clean up test reminders
Delete the "safe to delete" reminders created during development:
- "reminderhub test — safe to delete"
- "reminderhub phase 2 test — safe to delete" (×2)
- "curl test reminder — safe to delete"
- "Call mom — safe to delete" (in Family list)
- "#test-tag" list (created during list-creation test) — delete the list too

### P5-B: Launcher script
A single double-clickable shell script so you never have to open a terminal:

```bash
#!/bin/bash
# launch-reminderhub.sh
cd /Users/josephardizzone/Desktop/Claude/WIP/apps/reminderhub/backend
/Users/josephardizzone/Desktop/Claude/.venv/bin/uvicorn main:app --port 8000 &
cd ../frontend
npm run dev &
sleep 2
open http://localhost:5173
```

Make executable: `chmod +x launch-reminderhub.sh`

### P5-C: Fix the Calendar event target
In `reminders_handler.py`, the Calendar event is hardcoded to the "Home" calendar.
Needs to be verified against your actual calendar names, or made dynamic.

### P5-D: UX niceties (optional)
- Clear textarea + show "Added to Reminders!" toast for 2s after successful send
- Show loading spinner in preview panel while Gemini is thinking
- Handle the case where Gemini returns a title but no date (show "No date set" not a blank)
- Keyboard shortcut: `Cmd+Enter` to send

---

## Open questions / decisions

| Question | Decision |
|----------|----------|
| Multiple tags → which list? | First tag wins |
| No tag → which list? | Default "Reminders" list |
| Calendar event → which calendar? | "Home" (needs verification — P5-C) |
| Tag list naming | Title Case, no hash (e.g. "Family" not "#family") |

---

## File map (full project)

```
reminderhub/
├── .env                          ← GEMINI_API_KEY (do not commit)
├── .gitignore
├── WORKING_DOC.md                ← this file
├── backend/
│   ├── main.py                   ← FastAPI app + CORS
│   ├── models.py                 ← Pydantic: ParseRequest, ParsedReminder, CreateRequest, CreateResponse
│   ├── requirements.txt
│   ├── routes/
│   │   ├── parse.py              ← POST /parse → ParsedReminder JSON
│   │   └── create.py             ← POST /create → CreateResponse JSON
│   └── services/
│       ├── gemini_client.py      ← Gemini structured output, tag extraction
│       └── reminders_handler.py  ← AppleScript: create_reminder(), create_calendar_event()
└── frontend/
    ├── vite.config.ts            ← /api proxy → localhost:8000
    └── src/
        ├── main.tsx
        ├── App.tsx               ← [Phase 4] root layout
        ├── App.css               ← [Phase 4] styles
        ├── index.css             ← [Phase 4] reset
        ├── types.ts              ← [Phase 4] ParsedReminder interface
        ├── components/
        │   ├── ReminderInput.tsx ← [Phase 4] auto-grow textarea
        │   ├── PreviewPanel.tsx  ← [Phase 4] live structured card
        │   └── SendButton.tsx    ← [Phase 4] send + feedback
        └── hooks/
            └── useLiveParse.ts   ← [Phase 4] debounce + fetch + state
```
