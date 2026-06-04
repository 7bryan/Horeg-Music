"""
Factory functions for every Discord embed the bot sends.
Centralising embed construction means visual changes only ever need to happen here.
"""

from __future__ import annotations
import discord
from config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_WARNING,
    COLOR_INFO,
    QUEUE_PAGE_SIZE,
)
from models import Track

# ── Emoji constants ───────────────────────────────────────────────────────────

EMOJI_MUSIC = "🎵"
EMOJI_PLAY = "▶️"
EMOJI_PAUSE = "⏸️"
EMOJI_SKIP = "⏭️"
EMOJI_STOP = "⏹️"
EMOJI_QUEUE = "📋"
EMOJI_VOLUME = "🔊"
EMOJI_PING = "🏓"
EMOJI_JOIN = "🎤"
EMOJI_LEAVE = "👋"
EMOJI_ERROR = "❌"
EMOJI_TRASH = "🗑️"
EMOJI_SEARCH = "🔍"

# ── Generic helper ────────────────────────────────────────────────────────────


def simple(
    title: str,
    description: str = "",
    color: int = COLOR_PRIMARY,
) -> discord.Embed:
    """One-liner embed for short status messages."""
    return discord.Embed(title=title, description=description, color=color)


# ── Music embeds ──────────────────────────────────────────────────────────────


def now_playing(track: Track) -> discord.Embed:
    """Full Now Playing card with thumbnail, duration, and requester."""
    e = discord.Embed(
        title=f"{EMOJI_PLAY}  Now Playing",
        description=f"**[{track.title}]({track.webpage or '#'})**",
        color=COLOR_SUCCESS,
    )
    e.add_field(name="Duration", value=track.duration_str(), inline=True)
    e.add_field(
        name="Requested by",
        value=track.requester.mention if track.requester else "—",
        inline=True,
    )
    if track.thumbnail:
        e.set_thumbnail(url=track.thumbnail)
    return e


def track_queued(track: Track, position: int) -> discord.Embed:
    """Confirmation embed when a track is added behind an already-playing song."""
    e = discord.Embed(
        title=f"{EMOJI_MUSIC}  Added to Queue",
        description=f"**[{track.title}]({track.webpage or '#'})**",
        color=COLOR_PRIMARY,
    )
    e.add_field(name="Duration", value=track.duration_str(), inline=True)
    e.add_field(name="Position", value=f"#{position}", inline=True)
    e.add_field(
        name="Requested by",
        value=track.requester.mention if track.requester else "—",
        inline=True,
    )
    if track.thumbnail:
        e.set_thumbnail(url=track.thumbnail)
    return e


def queue_list(current: Track | None, queue: list[Track]) -> discord.Embed:
    """Full queue embed: shows current track + up to QUEUE_PAGE_SIZE upcoming tracks."""
    e = discord.Embed(title=f"{EMOJI_QUEUE}  Current Queue", color=COLOR_INFO)

    if current:
        e.add_field(
            name=f"{EMOJI_PLAY}  Now Playing",
            value=f"[{current.title}]({current.webpage or '#'}) `{current.duration_str()}`",
            inline=False,
        )

    if queue:
        lines = [
            f"`{i}.` [{t.title}]({t.webpage or '#'}) `{t.duration_str()}`"
            for i, t in enumerate(queue[:QUEUE_PAGE_SIZE], 1)
        ]
        if len(queue) > QUEUE_PAGE_SIZE:
            lines.append(f"…and **{len(queue) - QUEUE_PAGE_SIZE}** more")
        e.add_field(name="Up Next", value="\n".join(lines), inline=False)

    e.set_footer(text=f"{len(queue)} song(s) in queue")
    return e


def volume_set(vol: int) -> discord.Embed:
    """Volume confirmation with a visual progress bar."""
    filled = round(vol / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return simple(f"{EMOJI_VOLUME}  Volume Set", f"`{bar}` **{vol}%**", COLOR_SUCCESS)


def latency(ms: int) -> discord.Embed:
    """Ping embed with color that reflects the connection quality."""
    color = COLOR_SUCCESS if ms < 100 else COLOR_WARNING if ms < 200 else COLOR_ERROR
    return simple(f"{EMOJI_PING}  Pong!", f"Latency: **{ms}ms**", color)


def searching(query: str) -> discord.Embed:
    """Temporary loading embed shown while yt-dlp searches."""
    return simple(f"{EMOJI_SEARCH}  Searching…", f"Looking up `{query}`…", COLOR_INFO)


# ── Status / error embeds ─────────────────────────────────────────────────────


def error(title: str, description: str = "") -> discord.Embed:
    return simple(f"{EMOJI_ERROR}  {title}", description, COLOR_ERROR)


def warning(title: str, description: str = "") -> discord.Embed:
    return simple(title, description, COLOR_WARNING)


def info(title: str, description: str = "") -> discord.Embed:
    return simple(title, description, COLOR_INFO)


def success(title: str, description: str = "") -> discord.Embed:
    return simple(title, description, COLOR_SUCCESS)


# ── Help embed ────────────────────────────────────────────────────────────────


def help_menu() -> discord.Embed:
    """Full command reference embed."""
    e = discord.Embed(
        title=f"{EMOJI_MUSIC}  Horeg Music — Commands",
        description="Stream music from YouTube into your voice channel.",
        color=COLOR_PRIMARY,
    )
    commands = [
        (f"{EMOJI_JOIN}   `!join`", "Join your voice channel"),
        (f"{EMOJI_LEAVE}  `!leave`", "Leave the voice channel"),
        (f"{EMOJI_PLAY}   `!play <song>`", "Add a song to the queue and play"),
        (f"{EMOJI_PAUSE}  `!pause`", "Pause the current song"),
        (f"{EMOJI_PLAY}   `!resume`", "Resume playback"),
        (f"{EMOJI_SKIP}   `!skip`", "Skip the current song"),
        (f"{EMOJI_STOP}   `!stop`", "Stop and clear the entire queue"),
        (f"{EMOJI_QUEUE}  `!queue` / `!q`", "Show the current queue"),
        (f"{EMOJI_TRASH}  `!remove <#>`", "Remove a song by queue position"),
        (f"{EMOJI_MUSIC}  `!np`", "Show what's currently playing"),
        (f"{EMOJI_VOLUME} `!volume <0-100>`", "Set the playback volume"),
        (f"{EMOJI_PING}   `!ping`", "Check bot latency"),
    ]
    for name, value in commands:
        e.add_field(name=name, value=value, inline=False)
    e.set_footer(text="Horeg Music 🎸")
    return e
