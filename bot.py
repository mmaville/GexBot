import discord
from discord.ext import commands, tasks
from groq import AsyncGroq
from dotenv import load_dotenv
import collections
import itertools
import random
import re
import os
import time
from pathlib import Path

load_dotenv()

# --- Configuration ---
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
REQUIRED_ROLE = "Gexy"
SYSTEM_PROMPT_FILE = Path("system_prompt.md")
SYSTEM_PROMPT = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()

# --- Model Configuration ---
SIMPLE_MODEL = 'llama-3.1-8b-instant'      # Fast, cheap for simple messages
COMPLEX_MODEL = 'llama-3.3-70b-versatile'  # Powerful for complex requests

# Patterns that indicate a simple message (case-insensitive)
SIMPLE_PATTERNS = [
    r'^(hi|hello|hey|yo|sup|hiya|howdy)\b',
    r'^how are you',
    r'^what\'?s up',
    r'^good (morning|afternoon|evening|night)',
    r'^thanks?( you)?$',
    r'^(yes|no|ok|okay|sure|yep|nope)$',
    r'^(bye|goodbye|cya|later)$',
]

# Keywords that force the complex model
COMPLEX_KEYWORDS = [
    'explain', 'analyze', 'compare', 'describe in detail',
    'write a story', 'roleplay', 'pretend', 'imagine',
    'code', 'debug', 'help me understand', 'think about',
    'what do you think', 'give me advice', 'summarize',
]

def select_model(user_input: str) -> str:
    """Select the appropriate model based on message complexity."""
    lower_input = user_input.lower().strip()

    # Check for complex keywords first (override simple patterns)
    for keyword in COMPLEX_KEYWORDS:
        if keyword in lower_input:
            return COMPLEX_MODEL

    # Check if it's a simple greeting/response
    for pattern in SIMPLE_PATTERNS:
        if re.search(pattern, lower_input, re.IGNORECASE):
            return SIMPLE_MODEL

    # Short messages (under 20 chars) without complex keywords → simple model
    if len(lower_input) < 20:
        return SIMPLE_MODEL

    # Default to complex model for longer/ambiguous messages
    return COMPLEX_MODEL

# Paths for Gex command
IMAGES_DIR = Path("images")
TEXT_FILE = Path("textlist.txt")

# Initialize Clients
groq_client = AsyncGroq(api_key=GROQ_API_KEY)
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

# --- Memory ---
memory = collections.defaultdict(list)
active_chat_sessions = {}  # {channel_id: last_interaction_timestamp}
CHAT_SESSION_TIMEOUT = 300  # 5 minutes in seconds

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

# --- Chat Logic ---
async def process_chat(channel, user_input: str):
    """Process a chat message and return AI response."""
    channel_id = channel.id
    memory[channel_id].append({"role": "user", "content": user_input})
    if len(memory[channel_id]) > 10:
        memory[channel_id] = memory[channel_id][-10:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + memory[channel_id]

    # Select model based on input complexity
    model = select_model(user_input)

    async with channel.typing():
        response = await groq_client.chat.completions.create(
            model=model,
            messages=messages
        )
        ai_response = response.choices[0].message.content
        memory[channel_id].append({"role": "assistant", "content": ai_response})

    # Update session timestamp
    active_chat_sessions[channel_id] = time.time()
    return ai_response

@bot.command()
@commands.has_role(REQUIRED_ROLE)
@commands.cooldown(1, 10, commands.BucketType.user)
async def chat(ctx, *, user_input: str):
    try:
        ai_response = await process_chat(ctx.channel, user_input)
        await ctx.send(ai_response[:2000])
    except Exception as e:
        await ctx.send(f"⚠️ Error: {str(e)}")

# --- Tilde Message Listener ---
@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return

    # Check for ~ prefix in active chat sessions
    if message.content.startswith("~"):
        channel_id = message.channel.id

        # Check if there's an active session
        if channel_id in active_chat_sessions:
            last_time = active_chat_sessions[channel_id]

            # Check if session is still valid (within 5 minutes)
            if time.time() - last_time <= CHAT_SESSION_TIMEOUT:
                # Check if user has the required role
                if isinstance(message.author, discord.Member):
                    role = discord.utils.get(message.author.roles, name=REQUIRED_ROLE)
                    if role:
                        user_input = message.content[1:].strip()  # Remove ~ prefix
                        if user_input:
                            try:
                                ai_response = await process_chat(message.channel, user_input)
                                await message.channel.send(ai_response[:2000])
                            except Exception as e:
                                await message.channel.send(f"⚠️ Error: {str(e)}")
                            return
            else:
                # Session expired, remove it
                del active_chat_sessions[channel_id]

    # Process commands normally
    await bot.process_commands(message)

# --- Gex Command ---
@bot.command(name="gex")
@commands.has_role(REQUIRED_ROLE)
async def random_gex(ctx):
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

# --- Clear & Status Commands ---
@bot.command()
@commands.has_role(REQUIRED_ROLE)
async def clear(ctx):
    memory[ctx.channel.id] = []
    await ctx.send("🧹 **History cleared.**")

@bot.command()
@commands.has_role(REQUIRED_ROLE)
async def status(ctx, action: str, *, text: str):
    action = action.lower()
    if action == "playing": act = discord.Game(name=text)
    elif action == "watching": act = discord.Activity(type=discord.ActivityType.watching, name=text)
    elif action == "listening": act = discord.Activity(type=discord.ActivityType.listening, name=text)
    else: return await ctx.send("❌ Use `playing`, `watching`, or `listening`.")
    await bot.change_presence(activity=act)
    await ctx.send(f"✅ Status updated!")

# --- Error Handling ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ **Cooldown:** {error.retry_after:.1f}s remaining.")
    elif isinstance(error, commands.MissingRole):
        await ctx.send(f"🚫 Only the **{REQUIRED_ROLE}** role can use me.")

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN environment variable not set")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")
    bot.run(TOKEN)