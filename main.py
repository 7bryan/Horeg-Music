import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import yt_dlp
import asyncio
from dataclasses import dataclass, field
from typing import Optional

# Config & Setup
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

logging.basicConfig(
    handlers=[logging.FileHandler("discord.log", encoding="utf-8", mode="w")],
    level=logging.INFO,
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Colors & Emoji Constants
COLOR_PRIMARY = 0x9B59B6  # purple  – normal responses
COLOR_SUCCESS = 0x2ECC71  # green   – joined / started playing
COLOR_ERROR = 0xE74C3C  # red     – errors
COLOR_WARNING = 0xF39C12  # orange  – warnings / skipped
COLOR_INFO = 0x3498DB  # blue    – queue / info

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


# Track Dataclass
@dataclass
class Track:
    query: str
    title: str
    url: str
    duration: Optional[int] = None  # seconds
    thumbnail: Optional[str] = None
    webpage: Optional[str] = None
    requester: Optional[discord.Member] = None

    def duration_str(self) -> str:
        if self.duration is None:
            return "?"
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"


# Per-Guild State
@dataclass
class GuildState:
    queue: list = field(default_factory=list)  # list[Track]
    current: Optional[Track] = None
    volume: float = 0.5  # 0.0 – 1.0


guild_states: dict[int, GuildState] = {}


def get_state(guild_id: int) -> GuildState:
    if guild_id not in guild_states:
        guild_states[guild_id] = GuildState()
    return guild_states[guild_id]


# yt-dlp helpers
YDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
    "extract_flat": False,
}


def fetch_track(query: str, requester: discord.Member) -> Track:
    """Blocking – run in executor."""
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(
            f"ytsearch:{query}" if not query.startswith("http") else query,
            download=False,
        )
        if "entries" in info:
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


FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

# Embed helpers


def embed(
    title: str, description: str = "", color: int = COLOR_PRIMARY, **kwargs
) -> discord.Embed:
    e = discord.Embed(title=title, description=description, color=color)
    if thumbnail := kwargs.get("thumbnail"):
        e.set_thumbnail(url=thumbnail)
    if footer := kwargs.get("footer"):
        e.set_footer(text=footer)
    if author := kwargs.get("author"):
        e.set_author(name=author.display_name, icon_url=author.display_avatar.url)
    for name, value in kwargs.get("fields", []):
        e.add_field(name=name, value=value, inline=kwargs.get("inline", True))
    return e


def now_playing_embed(track: Track) -> discord.Embed:
    e = discord.Embed(
        title=f"{EMOJI_PLAY} Now Playing",
        description=f"**[{track.title}]({track.webpage or '#'})**",
        color=COLOR_SUCCESS,
    )
    e.add_field(name="Duration", value=track.duration_str(), inline=True)
    e.add_field(
        name="Requested by",
        value=track.requester.mention if track.requester else "Unknown",
        inline=True,
    )
    if track.thumbnail:
        e.set_thumbnail(url=track.thumbnail)
    return e


def queued_embed(track: Track, position: int) -> discord.Embed:
    e = discord.Embed(
        title=f"{EMOJI_MUSIC} Added to Queue",
        description=f"**[{track.title}]({track.webpage or '#'})**",
        color=COLOR_PRIMARY,
    )
    e.add_field(name="Duration", value=track.duration_str(), inline=True)
    e.add_field(name="Position", value=f"#{position}", inline=True)
    e.add_field(
        name="Requested by",
        value=track.requester.mention if track.requester else "Unknown",
        inline=True,
    )
    if track.thumbnail:
        e.set_thumbnail(url=track.thumbnail)
    return e


# Core playback
async def play_next(ctx: commands.Context):
    state = get_state(ctx.guild.id)
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return

    if not state.queue:
        state.current = None
        await ctx.send(
            embed=embed(
                f"{EMOJI_QUEUE} Queue Finished",
                "No more songs. Add more with `!play`!",
                color=COLOR_INFO,
            )
        )
        return

    track = state.queue.pop(0)
    state.current = track

    # re-fetch a fresh stream URL in executor (URLs expire)
    try:
        fresh = await bot.loop.run_in_executor(
            None, fetch_track, track.query, track.requester
        )
        track.url = fresh.url
    except Exception as e:
        await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Skipped",
                f"Couldn't load **{track.title}**: {e}",
                color=COLOR_ERROR,
            )
        )
        if state.queue:
            await play_next(ctx)
        return

    source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(track.url, **FFMPEG_OPTIONS), volume=state.volume
    )

    def after_playing(error):
        if error:
            print(f"Playback error: {error}")
        asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

    vc.play(source, after=after_playing)
    await ctx.send(embed=now_playing_embed(track))


#  Auto-disconnect when channel is empty


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    vc = discord.utils.get(bot.voice_clients, guild=member.guild)
    if not vc:
        return
    # if bot is alone in the channel, disconnect after 60s
    if len(vc.channel.members) == 1:
        await asyncio.sleep(60)
        if len(vc.channel.members) == 1:
            await vc.disconnect()
            state = get_state(member.guild.id)
            state.current = None
            state.queue.clear()


# Events


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="!help | music 🎵"
        )
    )
    print(f"✅ Horeg Music is ready! Logged in as {bot.user}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Missing argument", str(error), color=COLOR_ERROR
            )
        )
    elif isinstance(error, commands.CommandNotFound):
        pass  # silently ignore unknown commands
    else:
        await ctx.send(
            embed=embed(f"{EMOJI_ERROR} Error", str(error), color=COLOR_ERROR)
        )


#  Commands


@bot.command(name="help")
async def help_cmd(ctx):
    """Show all commands."""
    e = discord.Embed(
        title=f"{EMOJI_MUSIC} Horeg Music – Commands",
        description="Stream music from YouTube into your voice channel.",
        color=COLOR_PRIMARY,
    )
    e.add_field(
        name=f"{EMOJI_JOIN}  `!join`", value="Join your voice channel", inline=False
    )
    e.add_field(
        name=f"{EMOJI_LEAVE} `!leave`", value="Leave the voice channel", inline=False
    )
    e.add_field(
        name=f"{EMOJI_PLAY}  `!play <song>`",
        value="Add a song to the queue and play",
        inline=False,
    )
    e.add_field(
        name=f"{EMOJI_PAUSE} `!pause`", value="Pause the current song", inline=False
    )
    e.add_field(name=f"{EMOJI_PLAY}  `!resume`", value="Resume playback", inline=False)
    e.add_field(
        name=f"{EMOJI_SKIP}  `!skip`", value="Skip the current song", inline=False
    )
    e.add_field(
        name=f"{EMOJI_STOP}  `!stop`", value="Stop and clear the queue", inline=False
    )
    e.add_field(
        name=f"{EMOJI_QUEUE} `!queue`", value="Show the current queue", inline=False
    )
    e.add_field(
        name=f"{EMOJI_TRASH} `!remove <#>`",
        value="Remove a song by queue position",
        inline=False,
    )
    e.add_field(
        name=f"{EMOJI_MUSIC} `!np`", value="Show what's currently playing", inline=False
    )
    e.add_field(
        name=f"{EMOJI_VOLUME}`!volume <0-100>`",
        value="Set the playback volume",
        inline=False,
    )
    e.add_field(name=f"{EMOJI_PING}  `!ping`", value="Check bot latency", inline=False)
    e.set_footer(text="Horeg Music 🎸")
    await ctx.send(embed=e)


@bot.command()
async def ping(ctx):
    """Check bot latency."""
    ms = round(bot.latency * 1000)
    color = COLOR_SUCCESS if ms < 100 else COLOR_WARNING if ms < 200 else COLOR_ERROR
    await ctx.send(
        embed=embed(f"{EMOJI_PING} Pong!", f"Latency: **{ms}ms**", color=color)
    )


@bot.command()
async def join(ctx):
    """Join the user's voice channel."""
    if not ctx.author.voice:
        return await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Not in a channel",
                "Join a voice channel first!",
                color=COLOR_ERROR,
            )
        )
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
    await ctx.send(
        embed=embed(
            f"{EMOJI_JOIN} Joined",
            f"Connected to **{channel.name}**",
            color=COLOR_SUCCESS,
        )
    )


@bot.command()
async def leave(ctx):
    """Leave the voice channel."""
    if not ctx.voice_client:
        return await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Not connected",
                "I'm not in a voice channel.",
                color=COLOR_ERROR,
            )
        )
    state = get_state(ctx.guild.id)
    state.queue.clear()
    state.current = None
    await ctx.voice_client.disconnect()
    await ctx.send(
        embed=embed(
            f"{EMOJI_LEAVE} Disconnected", "See you later! 🎸", color=COLOR_INFO
        )
    )


@bot.command()
async def play(ctx, *, query: str):
    """Add a song to the queue and start playing."""
    if not ctx.author.voice:
        return await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Not in a channel",
                "Join a voice channel first!",
                color=COLOR_ERROR,
            )
        )

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()

    # show a loading message while fetching
    loading_msg = await ctx.send(
        embed=embed(
            f"{EMOJI_MUSIC} Searching…", f"Looking up `{query}`…", color=COLOR_INFO
        )
    )

    try:
        track = await bot.loop.run_in_executor(None, fetch_track, query, ctx.author)
    except Exception as e:
        await loading_msg.delete()
        return await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Not found",
                f"Couldn't find **{query}**:\n{e}",
                color=COLOR_ERROR,
            )
        )

    await loading_msg.delete()

    state = get_state(ctx.guild.id)
    state.queue.append(track)

    if not ctx.voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(embed=queued_embed(track, len(state.queue)))


@bot.command()
async def pause(ctx):
    """Pause playback."""
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send(
            embed=embed(
                f"{EMOJI_PAUSE} Paused",
                "Use `!resume` to continue.",
                color=COLOR_WARNING,
            )
        )
    else:
        await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Nothing playing",
                "There's nothing to pause.",
                color=COLOR_ERROR,
            )
        )


@bot.command()
async def resume(ctx):
    """Resume playback."""
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send(
            embed=embed(
                f"{EMOJI_PLAY} Resumed", "Back to the music!", color=COLOR_SUCCESS
            )
        )
    else:
        await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Not paused", "Playback isn't paused.", color=COLOR_ERROR
            )
        )


@bot.command()
async def skip(ctx):
    """Skip the current song."""
    vc = ctx.voice_client
    if vc and (vc.is_playing() or vc.is_paused()):
        state = get_state(ctx.guild.id)
        title = state.current.title if state.current else "track"
        vc.stop()
        await ctx.send(
            embed=embed(
                f"{EMOJI_SKIP} Skipped", f"Skipped **{title}**.", color=COLOR_WARNING
            )
        )
    else:
        await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Nothing playing",
                "There's nothing to skip.",
                color=COLOR_ERROR,
            )
        )


@bot.command()
async def stop(ctx):
    """Stop playback and clear the queue."""
    state = get_state(ctx.guild.id)
    state.queue.clear()
    state.current = None
    if ctx.voice_client:
        ctx.voice_client.stop()
    await ctx.send(
        embed=embed(
            f"{EMOJI_STOP} Stopped",
            "Playback stopped and queue cleared.",
            color=COLOR_WARNING,
        )
    )


@bot.command(name="queue", aliases=["q"])
async def queue_cmd(ctx):
    """Show the current queue."""
    state = get_state(ctx.guild.id)

    if not state.current and not state.queue:
        return await ctx.send(
            embed=embed(
                f"{EMOJI_QUEUE} Queue Empty",
                "Nothing in the queue. Use `!play` to add songs!",
                color=COLOR_INFO,
            )
        )

    e = discord.Embed(title=f"{EMOJI_QUEUE} Current Queue", color=COLOR_INFO)

    if state.current:
        e.add_field(
            name=f"{EMOJI_PLAY} Now Playing",
            value=f"[{state.current.title}]({state.current.webpage or '#'}) `{state.current.duration_str()}`",
            inline=False,
        )

    if state.queue:
        # show up to 10 upcoming tracks
        lines = []
        for i, track in enumerate(state.queue[:10], 1):
            lines.append(
                f"`{i}.` [{track.title}]({track.webpage or '#'}) `{track.duration_str()}`"
            )
        if len(state.queue) > 10:
            lines.append(f"…and **{len(state.queue) - 10}** more")
        e.add_field(name="Up Next", value="\n".join(lines), inline=False)

    e.set_footer(text=f"{len(state.queue)} song(s) in queue")
    await ctx.send(embed=e)


@bot.command()
async def remove(ctx, position: int):
    """Remove a song from the queue by position."""
    state = get_state(ctx.guild.id)
    if position < 1 or position > len(state.queue):
        return await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Invalid position",
                f"Position must be between 1 and {len(state.queue)}.",
                color=COLOR_ERROR,
            )
        )
    removed = state.queue.pop(position - 1)
    await ctx.send(
        embed=embed(
            f"{EMOJI_TRASH} Removed",
            f"Removed **{removed.title}** from the queue.",
            color=COLOR_WARNING,
        )
    )


@bot.command(aliases=["nowplaying"])
async def np(ctx):
    """Show what's currently playing."""
    state = get_state(ctx.guild.id)
    if not state.current:
        return await ctx.send(
            embed=embed(
                f"{EMOJI_MUSIC} Nothing Playing",
                "Use `!play` to start the music!",
                color=COLOR_INFO,
            )
        )
    await ctx.send(embed=now_playing_embed(state.current))


@bot.command()
async def volume(ctx, vol: int):
    """Set volume (0–100)."""
    if not 0 <= vol <= 100:
        return await ctx.send(
            embed=embed(
                f"{EMOJI_ERROR} Invalid volume",
                "Please enter a number between 0 and 100.",
                color=COLOR_ERROR,
            )
        )

    state = get_state(ctx.guild.id)
    state.volume = vol / 100

    vc = ctx.voice_client
    if vc and vc.source:
        vc.source.volume = state.volume

    bar_filled = round(vol / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    await ctx.send(
        embed=embed(
            f"{EMOJI_VOLUME} Volume set", f"`{bar}` **{vol}%**", color=COLOR_SUCCESS
        )
    )


bot.run(TOKEN)
