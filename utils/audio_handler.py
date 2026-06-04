"""
Handles everything audio-related:
  - Fetching track metadata and stream URLs via yt-dlp
  - Managing per-guild playback state (queue, volume, current track)
  - Driving the play → after → play_next loop
"""

from __future__ import annotations
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional

import discord
from discord.ext import commands
import yt_dlp

import config
from models import Track
import utils.embed_factory as ef

logger = logging.getLogger(__name__)


# ── Per-guild state ───────────────────────────────────────────────────────────


@dataclass
class GuildState:
    """All mutable playback state for a single Discord server."""

    queue: list[Track] = field(default_factory=list)
    current: Optional[Track] = None
    volume: float = config.DEFAULT_VOLUME  # 0.0–1.0


_states: dict[int, GuildState] = {}


def get_state(guild_id: int) -> GuildState:
    """Return (creating if needed) the GuildState for the given guild."""
    if guild_id not in _states:
        _states[guild_id] = GuildState()
    return _states[guild_id]


# ── yt-dlp fetch (blocking — always run via executor) ─────────────────────────


def fetch_track(query: str, requester: discord.Member) -> Track:
    """
    Resolve a search query or URL to a Track with a live stream URL.

    This is a blocking network call — always run it with
    ``bot.loop.run_in_executor(None, fetch_track, query, requester)``.
    """
    search = f"ytsearch:{query}" if not query.startswith("http") else query

    with yt_dlp.YoutubeDL(config.YDL_OPTIONS) as ydl:
        info = ydl.extract_info(search, download=False)
        if "entries" in info:  # came back as a search-result list
            info = info["entries"][0]

    return Track(
        query=query,
        title=info.get("title", query),
        url=info["url"],
        duration=info.get("duration"),
        thumbnail=info.get("thumbnail"),
        webpage=info.get("webpage_url"),
        requester=requester,
    )


# ── Playback engine ───────────────────────────────────────────────────────────


async def play_next(ctx: commands.Context) -> None:
    """
    Pop the next track off the queue and start playing it.
    Called after each track finishes (via run_coroutine_threadsafe) and
    directly by the !play command when nothing is currently playing.
    """
    state = get_state(ctx.guild.id)
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return

    if not state.queue:
        state.current = None
        await ctx.send(
            embed=ef.info(
                f"{ef.EMOJI_QUEUE}  Queue Finished",
                "No more songs — add more with `!play`!",
            )
        )
        return

    track = state.queue.pop(0)
    state.current = track

    # Stream URLs expire; re-fetch a fresh one right before playing
    try:
        fresh = await ctx.bot.loop.run_in_executor(
            None, fetch_track, track.query, track.requester
        )
        track.url = fresh.url
    except Exception as exc:
        logger.warning("Failed to refresh stream URL for '%s': %s", track.title, exc)
        await ctx.send(
            embed=ef.error("Skipped", f"Couldn't load **{track.title}**: {exc}")
        )
        if state.queue:
            await play_next(ctx)
        return

    source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(track.url, **config.FFMPEG_OPTIONS),
        volume=state.volume,
    )

    def _after(error: Optional[Exception]) -> None:
        if error:
            logger.error("Playback error for '%s': %s", track.title, error)
        asyncio.run_coroutine_threadsafe(play_next(ctx), ctx.bot.loop)

    vc.play(source, after=_after)
    await ctx.send(embed=ef.now_playing(track))
