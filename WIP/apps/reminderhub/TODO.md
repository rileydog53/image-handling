# ReminderHub — To-Do List

Generated from Gemini review (2026-05-02). Items grouped by priority and type.

---

## Improvements

### UX
- [ ] **Error handling** — Show clear visual feedback when Gemini fails (rate limits, parse errors) or AppleScript fails (list doesn't exist, calendar error). Currently fails silently.
- [ ] **Direct preview editing** — Let users click into Title, When, Tags, or Type fields in the preview card and correct them directly, without rewording the whole input.
- [ ] **Timezone clarity** — Make explicit how timezones are handled for calendar events. Add a way to confirm or adjust the inferred timezone.
- [ ] **Contextual defaults** — Let users configure preferences: default Reminder list, preferred calendar, frequent tags.

### Performance
- [ ] **Live preview latency** — Show a "thinking" indicator while Gemini processes. Tune debounce timing and consider caching repeated phrases.
- [ ] **Backend startup speed** — Reduce cold-start time so the app feels instant when the tab first opens.

### Reliability
- [ ] **Heartbeat edge cases** — Handle browser crashes, system sleep, and network interruptions so the backend never leaves orphaned processes.
- [ ] **Offline / degraded mode** — If Gemini is unreachable, fall back to a manual field-entry mode so the app still works.
- [ ] **API key security** — Move the Gemini API key from `.env` into macOS Keychain.

---

## Consistency Checks

- [ ] **"Send to Apple" label** — Verify the button label accurately reflects behavior for both Reminders and Calendar events in context.
- [ ] **Tag syntax rules** — Confirm `#family` and plain `family` both route correctly. Add a tooltip explaining expected syntax.
- [ ] **Cmd+Enter vs. button parity** — Verify both trigger the exact same flow and produce identical feedback.
- [ ] **Multi-tag routing** — Define and enforce a precedence rule when an input has multiple tags (e.g. `#family` and `#work`).
- [ ] **Calendar fallback** — Document which calendar is used when the user doesn't specify one. Should be consistent every time.
- [ ] **Relative date parsing** — Regularly test phrases like "next Tuesday", "in two weeks", "end of day" for consistent Gemini interpretation.
- [ ] **Mini calendar role** — Confirm it is intentionally display-only. If so, make that clear; if not, add click-to-prefill behavior.
- [ ] **Visual states** — Verify loading, success, and error states all have distinct, consistent visual treatments.

---

## New Features

- [ ] **Upcoming items panel** — Show next few Reminders and Calendar events pulled from macOS directly on the dashboard.
- [ ] **Settings page** — Default list, default calendar, custom tag→list mappings, API key management, default reminder time.
- [ ] **Templates / quick actions** — Save common reminders ("daily standup", "grocery item") and trigger them with a button or keyword.
- [ ] **Edit existing entries** — Mark reminders complete, reschedule events, sync changes back to Apple apps.
- [ ] **Voice input** — Use macOS dictation or a speech API to speak reminders directly into the app.
- [ ] **Smart suggestions** — Autocomplete tags, contacts, and locations as you type based on past entries.
- [ ] **Recurring reminders** — Handle "every Monday", "monthly on the 15th" with UI controls to fine-tune recurrence.
- [ ] **Menu bar extra** — Lightweight menubar icon that opens the input field without needing the browser tab.
- [ ] **Background themes** — Customizable backgrounds for the dashboard (noted as a future task during development).
