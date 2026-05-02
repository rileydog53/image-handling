// ─────────────────────────────────────────────
// hooks/useSend.ts — Sending the reminder to Apple
//
// Handles the logic of calling /create and reporting success or failure.
// Separated into its own hook so both the Send button AND the
// Cmd+Enter keyboard shortcut can trigger the exact same behaviour.
// ─────────────────────────────────────────────

import { useState } from "react";
import type { ParsedReminder } from "../types";

export function useSend(parsed: ParsedReminder | null, onSuccess: () => void) {
  // True while the /create request is in-flight (shows "Sending…" on the button)
  const [sending, setSending] = useState(false);

  // Feedback message shown to the user after sending:
  //   { ok: true,  msg: "Added to Reminders!" }
  //   { ok: false, msg: "Could not reach the server" }
  const [feedback, setFeedback] = useState<{ ok: boolean; msg: string } | null>(null);

  async function send() {
    // Guard: don't send if there's nothing to send, or if already sending.
    if (!parsed?.title || sending) return;

    setSending(true);
    setFeedback(null);

    try {
      // POST the full parsed reminder object to the backend.
      const res = await fetch("/api/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });

      const data = await res.json();

      if (data.success) {
        // Show "Added to Reminders!" for 1.8 seconds, then clear the input.
        setFeedback({ ok: true, msg: "Added to Reminders!" });
        setTimeout(() => {
          setFeedback(null);
          onSuccess(); // this clears the text box in App.tsx
        }, 1800);
      } else {
        // The backend returned success: false — show what went wrong.
        setFeedback({ ok: false, msg: data.error ?? "Something went wrong" });
      }
    } catch {
      // Network error — backend probably isn't running.
      setFeedback({ ok: false, msg: "Could not reach the server" });
    } finally {
      setSending(false);
    }
  }

  return { send, sending, feedback };
}
