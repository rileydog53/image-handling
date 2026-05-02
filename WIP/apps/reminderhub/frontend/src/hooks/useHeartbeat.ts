// ─────────────────────────────────────────────
// hooks/useHeartbeat.ts — Keep the backend alive while the tab is open
//
// Every 5 seconds, this sends a tiny "I'm still here" ping to the backend.
// The backend's heartbeat monitor watches for these pings —
// if they stop for 30 seconds (because the tab was closed),
// the backend shuts itself down automatically.
// ─────────────────────────────────────────────

import { useEffect } from "react";

export function useHeartbeat() {
  useEffect(() => {
    // The ping function — a fire-and-forget POST request.
    // .catch(() => {}) silently ignores any errors
    // (e.g. if the backend is briefly unavailable).
    const ping = () =>
      fetch("/api/heartbeat", { method: "POST" }).catch(() => {});

    ping(); // send one immediately on app load (don't wait 5s for the first one)

    // Then repeat every 5000ms (5 seconds)
    const id = setInterval(ping, 5000);

    // Cleanup: when the component unmounts, stop the interval to avoid memory leaks.
    return () => clearInterval(id);
  }, []); // empty array = only run this effect once, when the app first loads
}
