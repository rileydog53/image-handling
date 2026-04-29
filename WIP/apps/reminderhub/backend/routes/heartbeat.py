import os
import threading
import time

from fastapi import APIRouter

router = APIRouter()

_last_beat = time.time()
_TIMEOUT = 30  # seconds without a heartbeat before shutting down


def _monitor():
    # give the frontend time to load before we start watching
    time.sleep(20)
    while True:
        time.sleep(5)
        if time.time() - _last_beat > _TIMEOUT:
            print("No heartbeat for 30s — shutting down.")
            os._exit(0)


threading.Thread(target=_monitor, daemon=True).start()


@router.post("/heartbeat")
async def heartbeat():
    global _last_beat
    _last_beat = time.time()
    return {"ok": True}
