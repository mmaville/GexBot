import discord
from discord.ext import commands, tasks
import asyncio
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

REQUIRED_ROLE = "Gexy"
LEADERBOARD_FILE = Path("leaderboard.json")


def parse_time(time_str: str) -> int | None:
    """Parse time string like '30m', '1h', '2h30m' into seconds."""
    total_seconds = 0
    pattern = r'(\d+)([hms])'
    matches = re.findall(pattern, time_str.lower())

    if not matches:
        # Try just a number (assume minutes)
        if time_str.isdigit():
            return int(time_str) * 60
        return None

    for value, unit in matches:
        value = int(value)
        if unit == 'h':
            total_seconds += value * 3600
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 's':
            total_seconds += value

    return total_seconds if total_seconds > 0 else None


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = []
        self.usage_stats = self.load_leaderboard()
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()
        self.save_leaderboard()

    def load_leaderboard(self) -> dict:
        """Load leaderboard data from file."""
        if LEADERBOARD_FILE.exists():
            try:
                with open(LEADERBOARD_FILE, 'r') as f:
                    return defaultdict(int, json.load(f))
            except (json.JSONDecodeError, IOError):
                return defaultdict(int)
        return defaultdict(int)

    def save_leaderboard(self):
        """Save leaderboard data to file."""
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(dict(self.usage_stats), f, indent=2)

    @tasks.loop(seconds=10)
    async def check_reminders(self):
        """Check and send due reminders."""
        now = datetime.now()
        due_reminders = [r for r in self.reminders if r['time'] <= now]

        for reminder in due_reminders:
            try:
                channel = self.bot.get_channel(reminder['channel_id'])
                if channel:
                    await channel.send(
                        f"⏰ {reminder['user_mention']} Reminder: **{reminder['message']}**"
                    )
            except Exception:
                pass
            self.reminders.remove(reminder)

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Track command usage for leaderboard."""
        user_id = str(ctx.author.id)
        self.usage_stats[user_id] += 1
        # Save periodically (every 10 commands)
        if sum(self.usage_stats.values()) % 10 == 0:
            self.save_leaderboard()

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    async def remindme(self, ctx, time_str: str, *, message: str):
        """Set a reminder. Usage: !remind 30m check the oven"""
        seconds = parse_time(time_str)

        if seconds is None:
            await ctx.send("❌ Invalid time format. Use formats like: `30m`, `1h`, `2h30m`, `90s`")
            return

        if seconds < 10:
            await ctx.send("❌ Reminder must be at least 10 seconds.")
            return

        if seconds > 86400:  # 24 hours
            await ctx.send("❌ Reminder cannot be more than 24 hours.")
            return

        remind_time = datetime.now() + timedelta(seconds=seconds)

        self.reminders.append({
            'user_id': ctx.author.id,
            'user_mention': ctx.author.mention,
            'channel_id': ctx.channel.id,
            'message': message,
            'time': remind_time
        })

        # Format the time nicely
        if seconds >= 3600:
            time_display = f"{seconds // 3600}h {(seconds % 3600) // 60}m"
        elif seconds >= 60:
            time_display = f"{seconds // 60}m"
        else:
            time_display = f"{seconds}s"

        await ctx.send(f"✅ I'll remind you in **{time_display}**: {message}")

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    async def leaderboard(self, ctx):
        """Show the bot usage leaderboard."""
        if not self.usage_stats:
            await ctx.send("No usage data yet! Start using commands to appear on the leaderboard.")
            return

        # Sort by usage count
        sorted_users = sorted(self.usage_stats.items(), key=lambda x: x[1], reverse=True)[:10]

        embed = discord.Embed(
            title="🏆 GexBot Leaderboard",
            description="Top users by command usage",
            color=discord.Color.gold()
        )

        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]

        for i, (user_id, count) in enumerate(sorted_users):
            try:
                user = await self.bot.fetch_user(int(user_id))
                username = user.display_name
            except Exception:
                username = f"User {user_id}"

            medal = medals[i] if i < 3 else f"**{i + 1}.**"
            leaderboard_text += f"{medal} {username} - {count} commands\n"

        embed.add_field(name="Rankings", value=leaderboard_text or "No data", inline=False)
        embed.set_footer(text="Keep using GexBot to climb the ranks!")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
