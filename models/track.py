"""
Data model representing a single audio track in the queue.
Keeps all track-related data and formatting in one place.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import discord


@dataclass
class Track:
    """Represents a single audio track fetched from YouTube."""

    query: str  # original search term or URL
    title: str  # resolved video title
    url: str  # direct stream URL (expires — re-fetched before play)
    duration: Optional[int] = None  # length in seconds
    thumbnail: Optional[str] = None  # cover art URL
    webpage: Optional[str] = None  # YouTube watch URL
    requester: Optional[discord.Member] = None  # who queued this track

    def duration_str(self) -> str:
        """Return duration as a human-readable string (e.g. '3:45' or '1:02:30')."""
        if self.duration is None:
            return "?"
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def __str__(self) -> str:
        return f"{self.title} ({self.duration_str()})"
