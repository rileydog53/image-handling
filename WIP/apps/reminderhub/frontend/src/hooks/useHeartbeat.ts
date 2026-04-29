import { useEffect } from "react";

export function useHeartbeat() {
  useEffect(() => {
    const ping = () =>
      fetch("/api/heartbeat", { method: "POST" }).catch(() => {});

    ping(); // immediate on mount
    const id = setInterval(ping, 5000);
    return () => clearInterval(id);
  }, []);
}
