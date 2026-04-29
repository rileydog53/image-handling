import type { ParsedReminder } from "../types";

interface Props {
  parsed: ParsedReminder | null;
  isLoading: boolean;
}

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
  if (!parsed && !isLoading) return null;

  const dot = isLoading ? "…" : null;

  return (
    <div className="preview-panel">
      <div className="preview-header">Live Preview</div>

      <div className="preview-row">
        <span className="preview-label">Title</span>
        <span className="preview-value">{dot ?? parsed?.title ?? "—"}</span>
      </div>

      <div className="preview-row">
        <span className="preview-label">When</span>
        <span className="preview-value">
          {dot ?? formatDate(parsed?.due_date ?? null)}
        </span>
      </div>

      {(parsed?.notes || isLoading) && (
        <div className="preview-row">
          <span className="preview-label">Notes</span>
          <span className="preview-value">{dot ?? parsed?.notes ?? "—"}</span>
        </div>
      )}

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

      <div className="preview-row">
        <span className="preview-label">Type</span>
        <span className={`type-badge type-${parsed?.type ?? "reminder"}`}>
          {dot ?? (parsed?.type === "calendar" ? "Calendar Event" : "Reminder")}
        </span>
      </div>
    </div>
  );
}
