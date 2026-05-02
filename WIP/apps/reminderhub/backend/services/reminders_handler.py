# ─────────────────────────────────────────────
# services/reminders_handler.py — AppleScript integration
#
# This is where Python talks to macOS.
# It builds AppleScript strings and runs them via the `osascript`
# command, which tells the Apple Reminders or Calendar app to
# create a new entry.
#
# Key quirk: AppleScript can't parse date strings like "2026-04-29T15:00:00".
# Instead, we have to set each date component (year, month, day, hour...)
# individually on a `current date` object. That's what _build_date_block does.
# ─────────────────────────────────────────────

import subprocess
import textwrap
from datetime import datetime
from typing import Optional


def _find_or_create_list(list_name: str) -> str:
    """
    Returns a block of AppleScript that finds an existing Reminders list
    by name, or creates a new one if it doesn't exist yet.
    The result is stored in the AppleScript variable `targetList`.
    """
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
    """Create a new reminder in Apple Reminders, routing it to the right list based on tags."""

    # Convert the ISO date string to a Python datetime object (if present).
    dt = datetime.fromisoformat(due_date) if due_date else None

    # Build the AppleScript block that sets the due date (or blank if no date).
    date_block = _build_date_block(dt, "newReminder", "due date") if dt else ""

    # Build the line that sets the notes body (or blank if no notes).
    notes_line = f'set body of newReminder to "{_esc(notes)}"' if notes else ""

    # Use the first tag to decide which list the reminder goes into.
    # If no tags, it goes into the default "Reminders" list.
    tag = tags[0] if tags else None
    if tag:
        list_block = _find_or_create_list(tag)  # find or create e.g. "Family"
        reminder_target = "targetList"
    else:
        list_block = ""
        reminder_target = "default list"

    # Build the full AppleScript. Python f-strings fill in all the variables.
    script = textwrap.dedent(f"""
        tell application "Reminders"
            {list_block}
            set newReminder to make new reminder in {reminder_target}
            set name of newReminder to "{_esc(title)}"
            {date_block}
            {notes_line}
        end tell
    """)

    # Run osascript (the macOS command that executes AppleScript).
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return {"success": True, "id": result.stdout.strip()}


def create_calendar_event(title: str, due_date: Optional[str], notes: Optional[str]) -> dict:
    """Create a new event in Apple Calendar, using the first writable calendar found."""

    dt = datetime.fromisoformat(due_date) if due_date else datetime.now()

    # For Calendar events, startDate is a standalone variable (not a property of the event yet).
    start_block = _build_date_block(dt, "startDate", None)
    notes_line = f'set description of newEvent to "{_esc(notes)}"' if notes else ""

    script = textwrap.dedent(f"""
        tell application "Calendar"
            -- Find the first calendar the user can write to.
            -- This avoids hardcoding a calendar name like "Home" which may not exist.
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
                set endDate to startDate + 3600  -- default 1 hour duration
                set newEvent to make new event at end with properties {{summary:"{_esc(title)}", start date:startDate, end date:endDate}}
                {notes_line}
            end tell
        end tell
    """)

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=60,  # Calendar can be slow to respond
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return {"success": True, "id": result.stdout.strip()}


def _build_date_block(dt: datetime, target_var: str, prop_name: Optional[str]) -> str:
    """
    Returns an AppleScript snippet that builds a date by setting each
    component individually on a `current date` object.

    We do it this way because AppleScript's date string parsing is
    locale-sensitive and unreliable — setting components one by one
    always works regardless of system language or region settings.

    target_var: the AppleScript variable that will receive the result
                (e.g. "newReminder" or "startDate")
    prop_name:  if set, assigns the date as a property (e.g. "due date")
                if None, assigns it directly to target_var
    """
    date_var = "targetDate"  # temporary AppleScript variable we build the date in

    if prop_name:
        # e.g. "set due date of newReminder to targetDate"
        set_prop = f"set {prop_name} of {target_var} to {date_var}"
    else:
        # e.g. "set startDate to targetDate"
        set_prop = f"set {target_var} to {date_var}"

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
    """
    Escape special characters before inserting user text into an AppleScript string.
    Without this, a reminder title containing a quote like "dentist's"
    would break the AppleScript syntax.
    """
    return s.replace("\\", "\\\\").replace('"', '\\"')
