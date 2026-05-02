// ─────────────────────────────────────────────
// components/SendButton.tsx — The "Send to Apple" button
//
// A purely visual component — all the actual send logic lives in
// useSend.ts. This component just displays the button state and
// any success/error feedback message.
// ─────────────────────────────────────────────

// Props passed down from App.tsx
interface Props {
  onSend: () => void;   // function to call when the button is clicked
  disabled: boolean;    // true when there's nothing ready to send
  sending: boolean;     // true while the request is in-flight
  feedback: { ok: boolean; msg: string } | null; // success or error message
}

export function SendButton({ onSend, disabled, sending, feedback }: Props) {
  return (
    <div className="send-row">

      {/* Show feedback message ("Added to Reminders!" or an error) if present.
          Green for success, red for error — controlled by CSS classes. */}
      {feedback && (
        <span className={`feedback ${feedback.ok ? "feedback-ok" : "feedback-err"}`}>
          {feedback.msg}
        </span>
      )}

      <button className="send-btn" onClick={onSend} disabled={disabled}>
        {/* Label changes to "Sending…" while the request is running */}
        {sending ? "Sending…" : "Send to Apple"}

        {/* Small keyboard shortcut hint inside the button */}
        <span className="send-hint">⌘↵</span>
      </button>

    </div>
  );
}
