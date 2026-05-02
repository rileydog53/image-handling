# ─────────────────────────────────────────────
# routes/heartbeat.py — Auto-shutdown when the app is closed
#
# The frontend pings this endpoint every 5 seconds while the
# browser tab is open. A background thread watches those pings —
# if none arrive for 30 seconds (meaning the tab was closed),
# the server shuts itself down automatically.
# ─────────────────────────────────────────────

import os
import threading
import time

from fastapi import APIRouter

router = APIRouter()

# Track the timestamp of the last ping received from the frontend.
# Initialized to "now" so the server doesn't immediately shut down on startup.
_last_beat = time.time()

# How many seconds of silence before we consider the app closed.
_TIMEOUT = 30


def _monitor():
    # Wait 20 seconds before starting to watch — this gives the browser
    # time to load the React app and start sending pings after launch.
    time.sleep(20)

    while True:
        time.sleep(5)  # check every 5 seconds

        # If the last ping was more than 30 seconds ago, shut down.
        if time.time() - _last_beat > _TIMEOUT:
            print("No heartbeat for 30s — shutting down.")
            os._exit(0)  # hard exit — stops uvicorn and the whole process


# Start the monitor in a daemon thread.
# "daemon=True" means this thread won't prevent the program from exiting.
threading.Thread(target=_monitor, daemon=True).start()


@router.post("/heartbeat")
async def heartbeat():
    global _last_beat
    # Update the timestamp every time the frontend pings us.
    _last_beat = time.time()
    return {"ok": True}
