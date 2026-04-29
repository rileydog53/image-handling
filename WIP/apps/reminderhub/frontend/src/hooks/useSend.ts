import { useState } from "react";
import type { ParsedReminder } from "../types";

export function useSend(parsed: ParsedReminder | null, onSuccess: () => void) {
  const [sending, setSending] = useState(false);
  const [feedback, setFeedback] = useState<{ ok: boolean; msg: string } | null>(null);

  async function send() {
    if (!parsed?.title || sending) return;
    setSending(true);
    setFeedback(null);

    try {
      const res = await fetch("/api/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });
      const data = await res.json();

      if (data.success) {
        setFeedback({ ok: true, msg: "Added to Reminders!" });
        setTimeout(() => {
          setFeedback(null);
          onSuccess();
        }, 1800);
      } else {
        setFeedback({ ok: false, msg: data.error ?? "Something went wrong" });
      }
    } catch {
      setFeedback({ ok: false, msg: "Could not reach the server" });
    } finally {
      setSending(false);
    }
  }

  return { send, sending, feedback };
}
