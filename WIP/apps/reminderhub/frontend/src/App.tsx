// ─────────────────────────────────────────────
// App.tsx — Root of the React app (dashboard layout)
//
// Layout: top bar (clock + date) → calendar → reminder input → preview → send
// ─────────────────────────────────────────────

import { useState } from "react";
import { Clock } from "./components/Clock";
import { MiniCalendar } from "./components/MiniCalendar";
import { PreviewPanel } from "./components/PreviewPanel";
import { ReminderInput } from "./components/ReminderInput";
import { SendButton } from "./components/SendButton";
import { useHeartbeat } from "./hooks/useHeartbeat";
import { useLiveParse } from "./hooks/useLiveParse";
import { useSend } from "./hooks/useSend";
import "./App.css";

export default function App() {
  useHeartbeat();

  const [text, setText] = useState("");
  const { parsed, isLoading, error } = useLiveParse(text);
  const { send, sending, feedback } = useSend(parsed, () => setText(""));

  const sendDisabled = isLoading || sending || !parsed?.title;

  return (
    <div className="app">
      {/* ── Top bar: time on left, date on right ── */}
      <Clock />

      {/* ── Main content area ── */}
      <main className="app-main">
        <MiniCalendar />

        <ReminderInput
          value={text}
          onChange={setText}
          onSubmit={() => { if (!sendDisabled) send(); }}
        />

        {error && <p className="parse-error">{error}</p>}

        <PreviewPanel parsed={parsed} isLoading={isLoading} />

        <SendButton
          onSend={send}
          disabled={sendDisabled}
          sending={sending}
          feedback={feedback}
        />
      </main>
    </div>
  );
}
