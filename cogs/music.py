"""
Music commands Cog: play, pause, resume, skip, stop, queue, remove, np, volume, join, leave.
Loaded automatically by main.py at startup.
"""

from __future__ import annotations
import asyncio
import logging

import discord
from discord.ext import commands

import utils.embed_factory as ef
from utils.audio_handler import get_state, fetch_track, play_next

logger = logging.getLogger(__name__)


class Music(commands.Cog, name="Music"):
    """All music playback and queue management commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── Voice helpers ─────────────────────────────────────────────────────────

    async def _ensure_voice(self, ctx: commands.Context) -> bool:
        """
        Make sure the bot is in the same voice channel as the author.
        Returns True if ready, False (+ sends error embed) if not.
        """
        if not ctx.author.voice:
            await ctx.send(
                embed=ef.error("Not in a Channel", "Join a voice channel first!")
            )
            return False

        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        elif ctx.voice_client.channel != channel:
            await ctx.voice_client.move_to(channel)
        return True

    # ── Auto-disconnect ───────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        """Disconnect and clear state when the bot is left alone in a channel."""
        if member.bot:
            return

        vc = discord.utils.get(self.bot.voice_clients, guild=member.guild)
        if not vc:
            return

        # Wait, then check again — a user might rejoin within the grace period
        if len(vc.channel.members) == 1:
            await asyncio.sleep(60)
            if vc.is_connected() and len(vc.channel.members) == 1:
                state = get_state(member.guild.id)
                state.current = None
                state.queue.clear()
                await vc.disconnect()
                logger.info(
                    "Auto-disconnected from guild %s (empty channel)", member.guild.id
                )

    # ── Commands ──────────────────────────────────────────────────────────────

    @commands.command()
    async def join(self, ctx: commands.Context) -> None:
        """Join your voice channel."""
        if not ctx.author.voice:
            return await ctx.send(
                embed=ef.error("Not in a Channel", "Join a voice channel first!")
            )

        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(
            embed=ef.success(
                f"{ef.EMOJI_JOIN}  Joined", f"Connected to **{channel.name}**"
            )
        )

    @commands.command()
    async def leave(self, ctx: commands.Context) -> None:
        """Leave the voice channel and clear the queue."""
        if not ctx.voice_client:
            return await ctx.send(
                embed=ef.error("Not Connected", "I'm not in a voice channel.")
            )

        state = get_state(ctx.guild.id)
        state.queue.clear()
        state.current = None
        await ctx.voice_client.disconnect()
        await ctx.send(
            embed=ef.info(f"{ef.EMOJI_LEAVE}  Disconnected", "See you later! 🎸")
        )

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        """Add a song to the queue by name or YouTube URL."""
        if not await self._ensure_voice(ctx):
            return

        loading = await ctx.send(embed=ef.searching(query))

        try:
            track = await self.bot.loop.run_in_executor(
                None, fetch_track, query, ctx.author
            )
        except Exception as exc:
            await loading.delete()
            logger.warning("Track fetch failed for query '%s': %s", query, exc)
            return await ctx.send(
                embed=ef.error("Not Found", f"Couldn't find **{query}**:\n{exc}")
            )

        await loading.delete()

        state = get_state(ctx.guild.id)
        state.queue.append(track)

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            await play_next(ctx)
        else:
            await ctx.send(embed=ef.track_queued(track, len(state.queue)))

    @commands.command()
    async def pause(self, ctx: commands.Context) -> None:
        """Pause the current song."""
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send(
                embed=ef.warning(
                    f"{ef.EMOJI_PAUSE}  Paused", "Use `!resume` to continue."
                )
            )
        else:
            await ctx.send(
                embed=ef.error("Nothing Playing", "There's nothing to pause.")
            )

    @commands.command()
    async def resume(self, ctx: commands.Context) -> None:
        """Resume paused playback."""
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send(
                embed=ef.success(f"{ef.EMOJI_PLAY}  Resumed", "Back to the music!")
            )
        else:
            await ctx.send(embed=ef.error("Not Paused", "Playback isn't paused."))

    @commands.command()
    async def skip(self, ctx: commands.Context) -> None:
        """Skip the current song."""
        vc = ctx.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            state = get_state(ctx.guild.id)
            title = state.current.title if state.current else "track"
            vc.stop()  # triggers after_playing → play_next
            await ctx.send(
                embed=ef.warning(f"{ef.EMOJI_SKIP}  Skipped", f"Skipped **{title}**.")
            )
        else:
            await ctx.send(
                embed=ef.error("Nothing Playing", "There's nothing to skip.")
            )

    @commands.command()
    async def stop(self, ctx: commands.Context) -> None:
        """Stop playback and clear the entire queue."""
        state = get_state(ctx.guild.id)
        state.queue.clear()
        state.current = None
        if ctx.voice_client:
            ctx.voice_client.stop()
        await ctx.send(
            embed=ef.warning(
                f"{ef.EMOJI_STOP}  Stopped", "Playback stopped and queue cleared."
            )
        )

    @commands.command(name="queue", aliases=["q"])
    async def queue_cmd(self, ctx: commands.Context) -> None:
        """Show the current song queue."""
        state = get_state(ctx.guild.id)
        if not state.current and not state.queue:
            return await ctx.send(
                embed=ef.info(
                    f"{ef.EMOJI_QUEUE}  Queue Empty",
                    "Nothing queued. Use `!play` to add songs!",
                )
            )
        await ctx.send(embed=ef.queue_list(state.current, state.queue))

    @commands.command()
    async def remove(self, ctx: commands.Context, position: int) -> None:
        """Remove a song from the queue by its position number."""
        state = get_state(ctx.guild.id)
        if not state.queue:
            return await ctx.send(
                embed=ef.error("Queue Empty", "There's nothing in the queue to remove.")
            )
        if position < 1 or position > len(state.queue):
            return await ctx.send(
                embed=ef.error(
                    "Invalid Position",
                    f"Pick a number between **1** and **{len(state.queue)}**.",
                )
            )
        removed = state.queue.pop(position - 1)
        await ctx.send(
            embed=ef.warning(
                f"{ef.EMOJI_TRASH}  Removed",
                f"Removed **{removed.title}** from the queue.",
            )
        )

    @commands.command(aliases=["nowplaying"])
    async def np(self, ctx: commands.Context) -> None:
        """Show what's currently playing."""
        state = get_state(ctx.guild.id)
        if not state.current:
            return await ctx.send(
                embed=ef.info(
                    f"{ef.EMOJI_MUSIC}  Nothing Playing",
                    "Use `!play` to start the music!",
                )
            )
        await ctx.send(embed=ef.now_playing(state.current))

    @commands.command()
    async def volume(self, ctx: commands.Context, vol: int) -> None:
        """Set the playback volume (0–100)."""
        if not 0 <= vol <= 100:
            return await ctx.send(
                embed=ef.error(
                    "Invalid Volume", "Enter a number between **0** and **100**."
                )
            )

        state = get_state(ctx.guild.id)
        state.volume = vol / 100

        vc = ctx.voice_client
        if vc and vc.source:
            vc.source.volume = state.volume

        await ctx.send(embed=ef.volume_set(vol))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
