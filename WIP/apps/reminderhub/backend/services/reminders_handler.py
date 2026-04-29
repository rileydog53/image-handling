import subprocess
import textwrap
from datetime import datetime
from typing import Optional


def _find_or_create_list(list_name: str) -> str:
    """Returns AppleScript snippet that resolves `targetList` to the named list, creating it if needed."""
    escaped = _esc(list_name)
    return textwrap.dedent(f"""
        set targetList to missing value
        repeat with l in lists
            if name of l is "{escaped}" then
                set targetList to l
                exit repeat
            end if
        end repeat
        if targetList is missing value then
            set targetList to make new list with properties {{name:"{escaped}"}}
        end if
    """).strip()


def create_reminder(title: str, due_date: Optional[str], notes: Optional[str], tags: Optional[list] = None) -> dict:
    dt = datetime.fromisoformat(due_date) if due_date else None
    date_block = _build_date_block(dt, "newReminder", "due date") if dt else ""
    notes_line = f'set body of newReminder to "{_esc(notes)}"' if notes else ""

    tag = tags[0] if tags else None
    if tag:
        list_block = _find_or_create_list(tag)
        reminder_target = "targetList"
    else:
        list_block = ""
        reminder_target = "default list"

    script = textwrap.dedent(f"""
        tell application "Reminders"
            {list_block}
            set newReminder to make new reminder in {reminder_target}
            set name of newReminder to "{_esc(title)}"
            {date_block}
            {notes_line}
        end tell
    """)
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return {"success": True, "id": result.stdout.strip()}


def create_calendar_event(title: str, due_date: Optional[str], notes: Optional[str]) -> dict:
    dt = datetime.fromisoformat(due_date) if due_date else datetime.now()
    start_block = _build_date_block(dt, "startDate", None)
    notes_line = f'set description of newEvent to "{_esc(notes)}"' if notes else ""

    script = textwrap.dedent(f"""
        tell application "Calendar"
            -- pick the first writable calendar
            set targetCal to missing value
            repeat with c in calendars
                if writable of c is true then
                    set targetCal to c
                    exit repeat
                end if
            end repeat
            if targetCal is missing value then
                error "No writable calendar found"
            end if
            tell targetCal
                {start_block}
                set endDate to startDate + 3600
                set newEvent to make new event at end with properties {{summary:"{_esc(title)}", start date:startDate, end date:endDate}}
                {notes_line}
            end tell
        end tell
    """)
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return {"success": True, "id": result.stdout.strip()}


def _build_date_block(dt: datetime, target_var: str, prop_name: Optional[str]) -> str:
    date_var = "targetDate"
    set_prop = f"set {prop_name} of {target_var} to {date_var}" if prop_name else f"set {target_var} to {date_var}"
    return textwrap.dedent(f"""
        set {date_var} to current date
        set year of {date_var} to {dt.year}
        set month of {date_var} to {dt.month}
        set day of {date_var} to {dt.day}
        set hours of {date_var} to {dt.hour}
        set minutes of {date_var} to {dt.minute}
        set seconds of {date_var} to 0
        {set_prop}
    """).strip()


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')
