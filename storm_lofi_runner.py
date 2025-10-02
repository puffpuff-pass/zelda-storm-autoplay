"""
Storm Lofi Auto-Player — Honolulu, HI
-------------------------------------
Plays your Song of Storms (lofi) track whenever it's raining in Honolulu.
Stops when the rain stops. Polls on a timer.

Requirements:
  pip install requests python-vlc
(Also install the VLC desktop app so python-vlc can find libvlc.)
"""

from __future__ import annotations

import time
import threading
import signal
import sys
from typing import Optional
from pathlib import Path

import requests

try:
    import vlc  # python-vlc (needs VLC desktop app installed)
except Exception as e:
    print("[!] python-vlc not available. Install the VLC app and run: pip install python-vlc")
    raise

# ===========================
# CONFIG (edit these)
# ===========================

# Use your local MP3 path (recommended). Raw string r"..." handles backslashes/spaces.
LOCAL_AUDIO_FILE: Optional[str] = r"***REMOVED***Mikel - Zelda & Chill - 04 Song of Storms.mp3"

# OR use a direct-playable URL (e.g., file:///C:/.../Song.mp3 or http://localhost:8000/Song.mp3)
STREAM_URL: Optional[str] = ""

# Check weather every N seconds
POLL_SECONDS = 60

# Test switch: set True to force playback now; set back to False after testing.
FORCE_RAIN = False

# Honolulu
LATITUDE = 21.3069
LONGITUDE = -157.8583
TIMEZONE = "Pacific/Honolulu"

# ===========================
# END CONFIG
# ===========================


def _resolve_source() -> str:
    """
    Return the media source string (local file path or URL).
    Raises with a helpful message if nothing is configured or file missing.
    """
    if LOCAL_AUDIO_FILE:
        p = Path(LOCAL_AUDIO_FILE)
        if not p.exists():
            raise FileNotFoundError(
                f"Local audio file not found:\n  {LOCAL_AUDIO_FILE}\n"
                "• Fix the path (watch for 'sarah' vs 'sara').\n"
                "• If the file is in OneDrive, right-click it in Explorer → 'Always keep on this device'."
            )
        return LOCAL_AUDIO_FILE
    if STREAM_URL:
        return STREAM_URL
    raise RuntimeError(
        "No audio source configured. Set LOCAL_AUDIO_FILE to a valid path or set STREAM_URL to a playable URL."
    )


def is_raining_honolulu() -> bool:
    """True if it's currently raining in Honolulu.
    Uses Open-Meteo current.rain / current.precipitation (mm).
    """
    if FORCE_RAIN:
        print("[weather] FORCE_RAIN=True → pretending it's raining")
        return True

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        "&current=precipitation,rain"
        f"&timezone={TIMEZONE}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        current = resp.json().get("current", {})
        rain = float(current.get("rain", 0) or 0)
        precip = float(current.get("precipitation", 0) or 0)
        raining = (rain > 0) or (precip > 0)
        print(f"[weather] rain={rain:.2f} mm, precip={precip:.2f} mm → raining={raining}")
        return raining
    except Exception as e:
        print(f"[weather] Error: {e}. Assuming not raining.")
        return False


class StormPlayer:
    def __init__(self) -> None:
        self._instance = vlc.Instance()
        self._player: Optional[vlc.MediaPlayer] = None
        self._media: Optional[vlc.Media] = None
        self._playing = False

    @property
    def is_playing(self) -> bool:
        return self._playing

    def _ensure_media(self) -> None:
        if self._media is None:
            src = _resolve_source()
            self._media = self._instance.media_new(src)
            try:
                self._media.add_option("input-repeat=-1")  # loop hint
            except Exception:
                pass

    def start(self) -> None:
        if self._playing:
            return
        self._ensure_media()
        self._player = self._instance.media_player_new()
        self._player.set_media(self._media)
        self._player.play()
        self._playing = True
        print("[player] Started playback.")

        def watchdog() -> None:
            while self._playing:
                try:
                    if self._player and self._player.get_state() == vlc.State.Ended:
                        print("[player] Track ended. Restarting…")
                        self._player.stop()
                        self._player.play()
                except Exception:
                    pass
                time.sleep(2)

        threading.Thread(target=watchdog, daemon=True).start()

    def stop(self) -> None:
        if not self._playing:
            return
        if self._player:
            try:
                self._player.stop()
                self._player.release()
            except Exception:
                pass
            self._player = None
        self._playing = False
        print("[player] Stopped playback.")


def main() -> None:
    # Validate source early so we fail fast with a clear message
    try:
        _resolve_source()
    except Exception as e:
        print(f"[config] {e}")
        sys.exit(1)

    sp = StormPlayer()
    running = True

    def handle_sig(signum, frame):
        nonlocal running
        running = False
        print("[main] Received stop signal. Exiting…")

    try:
        signal.signal(signal.SIGINT, handle_sig)
        signal.signal(signal.SIGTERM, handle_sig)
    except Exception:
        pass

    print("[main] Storm Lofi Auto-Player running. Polling Honolulu weather…")
    while running:
        try:
            if is_raining_honolulu():
                if not sp.is_playing:
                    sp.start()
            else:
                if sp.is_playing:
                    sp.stop()
        except Exception as e:
            print(f"[main] Unexpected error: {e}")

        # Sleep in one-second ticks so Ctrl+C exits promptly
        for _ in range(POLL_SECONDS):
            if not running:
                break
            time.sleep(1)

    sp.stop()
    print("[main] Bye.")


if __name__ == "__main__":
    main()
