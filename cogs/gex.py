import discord
from discord.ext import commands
import random
from pathlib import Path

REQUIRED_ROLE = "Gexy"
IMAGES_DIR = Path("images")
TEXT_FILE = Path("textlist.txt")


class Gex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gex")
    @commands.has_role(REQUIRED_ROLE)
    async def random_gex(self, ctx):
        """Send a random Gex image and quote."""
        if not TEXT_FILE.exists():
            await ctx.send("Error: textlist.txt not found.")
            return

        if not IMAGES_DIR.exists() or not any(IMAGES_DIR.iterdir()):
            await ctx.send("Error: No images found.")
            return

        with open(TEXT_FILE, encoding="utf-8") as f:
            lines = f.read().splitlines()

        text = random.choice(lines)
        image_path = random.choice(list(IMAGES_DIR.iterdir()))

        await ctx.send(file=discord.File(image_path))
        await ctx.send(text)


async def setup(bot):
    await bot.add_cog(Gex(bot))
