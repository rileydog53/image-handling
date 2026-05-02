// ─────────────────────────────────────────────
// components/ReminderInput.tsx — The text box you type into
//
// A textarea that automatically grows taller as you type more text,
// and fires Cmd+Enter (or Ctrl+Enter) to submit.
// ─────────────────────────────────────────────

import { useEffect, useRef } from "react";

// Props = the "inputs" this component receives from its parent (App.tsx)
interface Props {
  value: string;                 // the current text (controlled by App)
  onChange: (val: string) => void; // called on every keystroke
  onSubmit?: () => void;         // called when Cmd+Enter is pressed
  disabled?: boolean;            // greys out the box when something is sending
}

export function ReminderInput({ value, onChange, onSubmit, disabled }: Props) {
  // ref gives us a direct handle to the actual DOM textarea element
  const ref = useRef<HTMLTextAreaElement>(null);

  // Auto-grow: every time the text changes, reset the height to "auto"
  // then immediately set it to the actual content height (scrollHeight).
  // This makes the box expand as you type more lines.
  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = "auto";
      ref.current.style.height = ref.current.scrollHeight + "px";
    }
  }, [value]);

  // Listen for Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux) to send.
  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault(); // prevent adding a newline in the text box
      onSubmit?.();       // the ?. means "only call if onSubmit was provided"
    }
  }

  return (
    <textarea
      ref={ref}
      className="reminder-input"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onKeyDown={handleKeyDown}
      placeholder="Type your reminder… e.g. call mom #family tomorrow at 3pm"
      disabled={disabled}
      rows={2}       // minimum height = 2 lines
      autoFocus      // cursor lands here automatically when the app opens
    />
  );
}
