import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import asyncio
import itertools
import os

load_dotenv()

# --- Configuration ---
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
REQUIRED_ROLE = "Gexy"

# Initialize Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- Status Loop ---
STATUS_LIST = itertools.cycle([
    discord.Activity(type=discord.ActivityType.watching, name="the Gexy Elite"),
    discord.Game(name="with your mind"),
    discord.Activity(type=discord.ActivityType.listening, name="to Groq speed")
])

@tasks.loop(minutes=5.0)
async def change_status():
    await bot.change_presence(activity=next(STATUS_LIST))

@bot.event
async def on_ready():
    change_status.start()
    print(f'{bot.user} is online!')

# --- Custom Help Command ---
@bot.command()
@commands.has_role(REQUIRED_ROLE)
async def help(ctx):
    embed = discord.Embed(
        title="🤖 Gexy-Bot Command Center",
        description="Welcome to the AI interface. Here is how to use my systems:",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="💬 `!chat [message]`",
        value="Starts a conversation with the AI. I'll remember the last 10 messages in this channel.\nAfter using `!chat`, you can continue with `~message` for 5 minutes.",
        inline=False
    )
    embed.add_field(
        name="🧹 `!clear`",
        value="Wipes the conversation history for this channel.",
        inline=False
    )
    embed.add_field(
        name="🔄 `!status [action] [text]`",
        value="Changes my current status (e.g., `!status playing games`).",
        inline=False
    )
    embed.add_field(
        name="🦎 `!gex`",
        value="Sends a random Gex image and quote.",
        inline=False
    )
    embed.add_field(
        name="⏳ Cooldown",
        value="There is a **10-second cooldown** between chat messages.",
        inline=False
    )

    embed.set_footer(text=f"Authorized Access Only: {REQUIRED_ROLE} Role Required")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)

    await ctx.send(embed=embed)

# --- Error Handling ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ **Cooldown:** {error.retry_after:.1f}s remaining.")
    elif isinstance(error, commands.MissingRole):
        await ctx.send(f"🚫 Only the **{REQUIRED_ROLE}** role can use me.")

# --- Load Cogs ---
async def load_cogs():
    await bot.load_extension("cogs.chat")
    await bot.load_extension("cogs.gex")
    await bot.load_extension("cogs.admin")

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN environment variable not set")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")

    asyncio.run(load_cogs())
    bot.run(TOKEN)
