"""
Centralized configuration for Horeg Music.
All tuneable values live here — no magic numbers scattered across the codebase.
"""

from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()


# ── Bot ───────────────────────────────────────────────────────────────────────

DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
COMMAND_PREFIX: str = "!"

# ── Audio ─────────────────────────────────────────────────────────────────────

DEFAULT_VOLUME: float = 0.5  # 50 % — range 0.0–1.0
AUTO_DISCONNECT_DELAY: int = 60  # seconds before leaving an empty channel

FFMPEG_OPTIONS: dict = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

YDL_OPTIONS: dict = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
    "extract_flat": False,
}

# ── Embed colors ──────────────────────────────────────────────────────────────

COLOR_PRIMARY: int = 0x9B59B6  # purple  — general responses
COLOR_SUCCESS: int = 0x2ECC71  # green   — joined / now playing
COLOR_ERROR: int = 0xE74C3C  # red     — errors
COLOR_WARNING: int = 0xF39C12  # orange  — skip / pause / warning
COLOR_INFO: int = 0x3498DB  # blue    — queue / info

# ── Queue display ─────────────────────────────────────────────────────────────

QUEUE_PAGE_SIZE: int = 10  # max tracks shown per !queue page
