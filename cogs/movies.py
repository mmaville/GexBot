import random
import re
import urllib.parse

import discord
import requests
from discord.ext import commands

from config import OMDB_KEY, REQUIRED_ROLE, TMDB_KEY, TRAKT_ID


class ShitFlags(commands.FlagConverter):
    curated: bool = False


async def get_youtube_link(title: str) -> str | None:
    """Scrape YouTube search results for a trailer link."""
    query = urllib.parse.quote(f"{title} official trailer")
    url = f"https://www.youtube.com/results?search_query={query}"
    response = requests.get(url).text
    video_ids = re.findall(r"watch\?v=(\S{11})", response)
    return f"https://www.youtube.com/watch?v={video_ids[0]}" if video_ids else None


async def fetch_trakt_item() -> tuple[str | None, str | None]:
    """Pull a random movie from community-vetted 'bad' lists."""
    headers = {'trakt-api-version': '2', 'trakt-api-key': TRAKT_ID}
    search = requests.get("https://api.trakt.tv/search/list?query=so bad its good", headers=headers).json()
    if not search:
        return None, None

    chosen_list = random.choice(search[:10])
    user_slug = chosen_list['user']['ids']['slug']
    list_id = chosen_list['list']['ids']['trakt']

    items = requests.get(f"https://api.trakt.tv/users/{user_slug}/lists/{list_id}/items/movies", headers=headers).json()
    movie = random.choice(items)['movie']
    return movie['title'], movie['year']


class Movies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    async def shitmovie(self, ctx, *, flags: ShitFlags):
        """Finds a terrible movie. Use -curated for the 'good' bad ones."""
        if flags.curated:
            title, year = await fetch_trakt_item()
            source = "Community Cult Classic List"
        else:
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_KEY}&vote_average.lte=4&vote_count.gte=300&sort_by=popularity.desc"
            data = requests.get(url).json()
            movie = random.choice(data['results'][:20])
            title, year, source = movie['title'], movie['release_date'][:4], "The TMDb Dungeon"

        await ctx.send(f"💩 **Found some total shit:** {title} ({year})\n*Source: {source}*\nType `!judge {title}` for the stats.")

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    async def shitroulette(self, ctx, *, flags: ShitFlags):
        """Drops a trailer for a random disaster. -curated for the 'Best of the Worst'."""
        if flags.curated:
            title, _ = await fetch_trakt_item()
        else:
            hall_of_shame = ["Foodfight!", "Mac and Me", "Birdemic", "The Room", "Troll 2", "Battlefield Earth"]
            title = random.choice(hall_of_shame)

        await ctx.send(f"🎲 **Roulette Spin...** You're watching: **{title}**")
        trailer = await get_youtube_link(title)
        await ctx.send(trailer if trailer else "The trailer was too shitty to find.")

    @commands.command()
    @commands.has_role(REQUIRED_ROLE)
    async def judge(self, ctx, *, movie_title: str):
        """Calculates the 'Irony Gap' (Critic vs Audience)."""
        url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_KEY}"
        data = requests.get(url).json()

        if data.get('Response') == 'False':
            return await ctx.send("I couldn't find that movie to judge it.")

        try:
            critic = int(data['Metascore']) if data['Metascore'] != 'N/A' else 0
            audience = int(float(data['imdbRating']) * 10) if data['imdbRating'] != 'N/A' else 0
            gap = abs(critic - audience)

            status = "Just Regular Bad."
            color = discord.Color.light_grey()

            if gap >= 30:
                status = "⚠️ SCIENTIFICALLY SHIT-GOOD (High Irony Gap)"
                color = discord.Color.gold()
            elif critic < 25 and audience < 25:
                status = "💀 WEAPONIZED SHIT (Unwatchable)"
                color = discord.Color.dark_red()

            embed = discord.Embed(title=f"The Verdict: {data['Title']}", color=color)
            embed.set_thumbnail(url=data['Poster'])
            embed.add_field(name="Critics", value=f"{critic}%", inline=True)
            embed.add_field(name="Audience", value=f"{audience}%", inline=True)
            embed.add_field(name="Irony Gap", value=f"{gap} pts", inline=False)
            embed.set_footer(text=f"Rating: {status}")

            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("⚠️ Error: Ratings data is too messy for this one.")


async def setup(bot):
    await bot.add_cog(Movies(bot))
