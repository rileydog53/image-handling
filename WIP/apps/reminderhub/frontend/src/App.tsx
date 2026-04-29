import { useState } from "react";
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
      <header className="app-header">
        <h1>ReminderHub</h1>
      </header>

      <main className="app-main">
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
