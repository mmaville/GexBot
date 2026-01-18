import discord
from discord.ext import commands
from groq import AsyncGroq
import collections
import time
import re
import os
from pathlib import Path

# --- Configuration ---
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
REQUIRED_ROLE = "Gexy"
SYSTEM_PROMPT_FILE = Path("system_prompt.md")
SYSTEM_PROMPT = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()

# --- Model Configuration ---
SIMPLE_MODEL = 'llama-3.1-8b-instant'
COMPLEX_MODEL = 'llama-3.3-70b-versatile'

SIMPLE_PATTERNS = [
    r'^(hi|hello|hey|yo|sup|hiya|howdy)\b',
    r'^how are you',
    r'^what\'?s up',
    r'^good (morning|afternoon|evening|night)',
    r'^thanks?( you)?$',
    r'^(yes|no|ok|okay|sure|yep|nope)$',
    r'^(bye|goodbye|cya|later)$',
]

COMPLEX_KEYWORDS = [
    'explain', 'analyze', 'compare', 'describe in detail',
    'write a story', 'roleplay', 'pretend', 'imagine',
    'code', 'debug', 'help me understand', 'think about',
    'what do you think', 'give me advice', 'summarize',
]

def select_model(user_input: str) -> str:
    """Select the appropriate model based on message complexity."""
    lower_input = user_input.lower().strip()

    for keyword in COMPLEX_KEYWORDS:
        if keyword in lower_input:
            return COMPLEX_MODEL

    for pattern in SIMPLE_PATTERNS:
        if re.search(pattern, lower_input, re.IGNORECASE):
            return SIMPLE_MODEL

    if len(lower_input) < 20:
        return SIMPLE_MODEL

    return COMPLEX_MODEL


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.groq_client = AsyncGroq(api_key=GROQ_API_KEY)
        self.memory = collections.defaultdict(list)
        self.active_chat_sessions = {}
        self.CHAT_SESSION_TIMEOUT = 300  # 5 minutes

    async def process_chat(self, channel, user_input: str):
        """Process a chat message and return AI response."""
        channel_id = channel.id
        self.memory[channel_id].append({"role": "user", "content": user_input})
        if len(self.memory[channel_id]) > 10:
            self.memory[channel_id] = self.memory[channel_id][-10:]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.memory[channel_id]

        model = select_model(user_input)

        async with channel.typing():
            response = await self.groq_client.chat.completions.create(
                model=model,
                messages=messages
            )
            ai_response = response.choices[0].message.content
            self.memory[channel_id].append({"role": "assistant", "content": ai_response})

        self.active_chat_sessions[channel_id] = time.time()
        return ai_response

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def chat(self, ctx, *, user_input: str):
        try:
            ai_response = await self.process_chat(ctx.channel, user_input)
            await ctx.send(ai_response[:2000])
        except Exception as e:
            await ctx.send(f"⚠️ Error: {str(e)}")

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    async def clear(self, ctx):
        self.memory[ctx.channel.id] = []
        await ctx.send("🧹 **History cleared.**")

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def roast(self, ctx, member: discord.Member):
        """Roast a user in Gex's sarcastic style."""
        roast_prompt = f"You are Gex the Gecko, known for your sharp wit and pop culture references. Roast the user named '{member.display_name}' in your signature sarcastic style. Keep it playful and funny, not mean-spirited. Include a pop culture reference. Keep it under 200 words."

        async with ctx.typing():
            try:
                response = await self.groq_client.chat.completions.create(
                    model=COMPLEX_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": roast_prompt}
                    ]
                )
                roast = response.choices[0].message.content
                await ctx.send(f"🔥 {member.mention}\n\n{roast[:1900]}")
            except Exception as e:
                await ctx.send(f"⚠️ Error: {str(e)}")

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def vibecheck(self, ctx):
        """Analyze the current channel's vibe based on recent messages."""
        # Fetch last 20 messages
        messages_list = []
        async for msg in ctx.channel.history(limit=20):
            if not msg.author.bot and msg.content:
                messages_list.append(f"{msg.author.display_name}: {msg.content}")

        if len(messages_list) < 3:
            await ctx.send("Not enough messages to vibe check! Need at least 3 recent messages.")
            return

        messages_text = "\n".join(reversed(messages_list))
        vibe_prompt = f"You are Gex the Gecko. Analyze the vibe of this Discord channel based on these recent messages and give your sarcastic assessment. What's the energy? What kind of people hang out here? Include a pop culture reference. Keep it under 150 words.\n\nRecent messages:\n{messages_text}"

        async with ctx.typing():
            try:
                response = await self.groq_client.chat.completions.create(
                    model=COMPLEX_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": vibe_prompt}
                    ]
                )
                vibe = response.choices[0].message.content
                await ctx.send(f"🌡️ **Vibe Check**\n\n{vibe[:1900]}")
            except Exception as e:
                await ctx.send(f"⚠️ Error: {str(e)}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return

        # Check for ~ prefix in active chat sessions
        if message.content.startswith("~"):
            channel_id = message.channel.id

            if channel_id in self.active_chat_sessions:
                last_time = self.active_chat_sessions[channel_id]

                if time.time() - last_time <= self.CHAT_SESSION_TIMEOUT:
                    if isinstance(message.author, discord.Member):
                        role = discord.utils.get(message.author.roles, name=REQUIRED_ROLE)
                        if role:
                            user_input = message.content[1:].strip()
                            if user_input:
                                try:
                                    ai_response = await self.process_chat(message.channel, user_input)
                                    await message.channel.send(ai_response[:2000])
                                except Exception as e:
                                    await message.channel.send(f"⚠️ Error: {str(e)}")
                                return
                else:
                    del self.active_chat_sessions[channel_id]


async def setup(bot):
    await bot.add_cog(Chat(bot))
