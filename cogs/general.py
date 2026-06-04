"""
General utility commands Cog: ping, help.
Loaded automatically by main.py at startup.
"""

from __future__ import annotations
import discord
from discord.ext import commands

import utils.embed_factory as ef


class General(commands.Cog, name="General"):
    """Utility and informational commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Check the bot's response latency."""
        ms = round(self.bot.latency * 1000)
        await ctx.send(embed=ef.latency(ms))

    @commands.command(name="help")
    async def help_cmd(self, ctx: commands.Context) -> None:
        """Show all available commands."""
        await ctx.send(embed=ef.help_menu())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
