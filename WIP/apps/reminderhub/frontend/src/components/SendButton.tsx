interface Props {
  onSend: () => void;
  disabled: boolean;
  sending: boolean;
  feedback: { ok: boolean; msg: string } | null;
}

export function SendButton({ onSend, disabled, sending, feedback }: Props) {
  return (
    <div className="send-row">
      {feedback && (
        <span className={`feedback ${feedback.ok ? "feedback-ok" : "feedback-err"}`}>
          {feedback.msg}
        </span>
      )}
      <button className="send-btn" onClick={onSend} disabled={disabled}>
        {sending ? "Sending…" : "Send to Apple"}
        <span className="send-hint">⌘↵</span>
      </button>
    </div>
  );
}
