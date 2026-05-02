// ─────────────────────────────────────────────
// types.ts — Shared TypeScript types
//
// This file defines the shape of a parsed reminder.
// TypeScript uses this as a contract — if any part of the app
// passes the wrong kind of data, it gets flagged as an error
// before the code even runs.
//
// This mirrors the ParsedReminder model in backend/models.py.
// ─────────────────────────────────────────────

export interface ParsedReminder {
  title: string | null;      // what needs to be done, e.g. "Call mom"
  due_date: string | null;   // ISO-8601 format: "2026-04-29T15:00:00", or null if no date
  notes: string | null;      // any extra detail beyond the title
  type: "reminder" | "calendar"; // which Apple app to create it in
  tags: string[] | null;     // category list, e.g. ["Family"] or null
}
