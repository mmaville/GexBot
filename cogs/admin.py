import discord
from discord.ext import commands

from config import REQUIRED_ROLE


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    async def status(self, ctx, action: str, *, text: str):
        action = action.lower()
        if action == "playing":
            act = discord.Game(name=text)
        elif action == "watching":
            act = discord.Activity(type=discord.ActivityType.watching, name=text)
        elif action == "listening":
            act = discord.Activity(type=discord.ActivityType.listening, name=text)
        else:
            return await ctx.send("❌ Use `playing`, `watching`, or `listening`.")
        await self.bot.change_presence(activity=act)
        await ctx.send(f"✅ Status updated!")


async def setup(bot):
    await bot.add_cog(Admin(bot))
