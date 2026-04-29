import { useEffect, useRef } from "react";

interface Props {
  value: string;
  onChange: (val: string) => void;
  onSubmit?: () => void;
  disabled?: boolean;
}

export function ReminderInput({ value, onChange, onSubmit, disabled }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = "auto";
      ref.current.style.height = ref.current.scrollHeight + "px";
    }
  }, [value]);

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      onSubmit?.();
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
      rows={2}
      autoFocus
    />
  );
}
