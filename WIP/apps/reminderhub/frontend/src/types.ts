export interface ParsedReminder {
  title: string | null;
  due_date: string | null;
  notes: string | null;
  type: "reminder" | "calendar";
  tags: string[] | null;
}
