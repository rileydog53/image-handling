// ─────────────────────────────────────────────
// components/MiniCalendar.tsx — Month grid with today highlighted
//
// A pure display component — no interactions, just shows the
// current month laid out in a standard Su-Sa grid with today circled.
// ─────────────────────────────────────────────

const DAY_LABELS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

export function MiniCalendar() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth(); // 0-indexed (0 = January)
  const today = now.getDate();  // 1-31

  // Month name for the header, e.g. "April 2026"
  const monthName = now.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });

  // How many days in this month?
  // Day 0 of next month = last day of this month.
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  // What day of the week does the 1st fall on? (0 = Sunday)
  const firstDayOfWeek = new Date(year, month, 1).getDay();

  // Build the grid cells: empty slots for padding, then 1..daysInMonth
  const cells: (number | null)[] = [];
  for (let i = 0; i < firstDayOfWeek; i++) cells.push(null); // empty padding
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);

  return (
    <div className="mini-cal">
      <div className="mini-cal-header">{monthName}</div>

      <div className="mini-cal-grid">
        {/* Day-of-week labels: Su Mo Tu ... */}
        {DAY_LABELS.map((d) => (
          <span key={d} className="mini-cal-label">
            {d}
          </span>
        ))}

        {/* Day numbers + empty padding cells */}
        {cells.map((day, i) => (
          <span
            key={i}
            className={`mini-cal-day${day === today ? " mini-cal-today" : ""}${day === null ? " mini-cal-empty" : ""}`}
          >
            {day ?? ""}
          </span>
        ))}
      </div>
    </div>
  );
}
