"""
main.py
-------
Entry point for Horeg Music.
Responsible for one thing only: creating the bot, loading cogs, and running it.
All logic lives in cogs/ and utils/.
"""

from __future__ import annotations
import asyncio
import logging
import sys
import os

# Ensure the project root is always on sys.path so that imports like
# "from models import Track" work correctly regardless of how Python
# resolves the working directory when loading cog extensions.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import discord
from discord.ext import commands

import config

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    handlers=[
        logging.FileHandler("discord.log", encoding="utf-8", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Cogs to load ──────────────────────────────────────────────────────────────

COGS = [
    "cogs.music",
    "cogs.general",
]

# ── Bot setup ─────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=config.COMMAND_PREFIX,
    intents=intents,
    help_command=None,  # replaced by our custom !help in general.py
)


@bot.event
async def on_ready() -> None:
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{config.COMMAND_PREFIX}help | music 🎵",
        )
    )
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    if isinstance(error, commands.MissingRequiredArgument):
        from utils import embed_factory as ef

        await ctx.send(embed=ef.error("Missing Argument", str(error)))
    elif isinstance(error, commands.CommandNotFound):
        pass  # silently ignore unknown commands
    else:
        logger.error("Unhandled command error: %s", error)
        from utils import embed_factory as ef

        await ctx.send(embed=ef.error("Error", str(error)))


# ── Startup ───────────────────────────────────────────────────────────────────


async def main() -> None:
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
            logger.info("Loaded cog: %s", cog)
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
