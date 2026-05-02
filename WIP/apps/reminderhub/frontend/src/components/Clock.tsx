// ─────────────────────────────────────────────
// components/Clock.tsx — Live clock + date in the top bar
//
// Updates every second. Shows time on the left, date on the right.
// ─────────────────────────────────────────────

import { useEffect, useState } from "react";

export function Clock() {
  const [now, setNow] = useState(new Date());

  // Tick every second to keep the clock live.
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const time = now.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });

  const date = now.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="top-bar">
      <span className="top-bar-time">{time}</span>
      <span className="top-bar-date">{date}</span>
    </div>
  );
}
