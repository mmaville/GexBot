import os
import random
from pathlib import Path

import discord
from discord.ext import commands

# Load token from environment variable
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Configure intents (message_content required for prefix commands)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Paths
IMAGES_DIR = Path("images")
TEXT_FILE = Path("textlist.txt")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("-------")


@bot.command(name="gex")
async def random_gex(ctx: commands.Context):
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


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable not set")
    bot.run(DISCORD_TOKEN)