// ─────────────────────────────────────────────
// components/PreviewPanel.tsx — The live preview card
//
// Shows the structured fields Gemini extracted from your text:
// title, date, notes, tags, and type.
// While a request is in-flight, shows "…" placeholders instead.
// ─────────────────────────────────────────────

import type { ParsedReminder } from "../types";

interface Props {
  parsed: ParsedReminder | null; // the latest parsed result (null if nothing typed yet)
  isLoading: boolean;            // true while waiting for Gemini's response
}


// Converts an ISO-8601 date string like "2026-04-29T15:00:00"
// into a human-readable format like "Wed, Apr 29, 2026, 3:00 PM".
function formatDate(iso: string | null): string {
  if (!iso) return "No date set";
  const d = new Date(iso);
  return d.toLocaleString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}


export function PreviewPanel({ parsed, isLoading }: Props) {
  // Don't render anything if there's no data and nothing is loading yet.
  // The card appears only after you start typing.
  if (!parsed && !isLoading) return null;

  // While loading, show "…" in every field instead of stale data.
  const dot = isLoading ? "…" : null;

  return (
    <div className="preview-panel">
      <div className="preview-header">Live Preview</div>

      {/* Title row — shows "…" while loading, then the parsed title */}
      <div className="preview-row">
        <span className="preview-label">Title</span>
        <span className="preview-value">{dot ?? parsed?.title ?? "—"}</span>
      </div>

      {/* Date row — formats the ISO string into readable text */}
      <div className="preview-row">
        <span className="preview-label">When</span>
        <span className="preview-value">
          {dot ?? formatDate(parsed?.due_date ?? null)}
        </span>
      </div>

      {/* Notes row — only shown if notes exist or we're loading */}
      {(parsed?.notes || isLoading) && (
        <div className="preview-row">
          <span className="preview-label">Notes</span>
          <span className="preview-value">{dot ?? parsed?.notes ?? "—"}</span>
        </div>
      )}

      {/* Tags row — each tag becomes a small blue pill badge */}
      <div className="preview-row">
        <span className="preview-label">Tags</span>
        <span className="preview-value preview-tags">
          {dot ??
            (parsed?.tags?.length
              ? parsed.tags.map((t) => (
                  <span key={t} className="tag-pill">
                    {t}
                  </span>
                ))
              : "—")}
        </span>
      </div>

      {/* Type row — shows "Reminder" or "Calendar Event" with different colours */}
      <div className="preview-row">
        <span className="preview-label">Type</span>
        <span className={`type-badge type-${parsed?.type ?? "reminder"}`}>
          {dot ?? (parsed?.type === "calendar" ? "Calendar Event" : "Reminder")}
        </span>
      </div>
    </div>
  );
}
