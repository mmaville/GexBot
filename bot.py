import random
from discord.ext.commands import Bot
from discord import File
import os
import math

discord_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

bot = Bot(command_prefix='!')

@bot.event
async def on_ready():
    print("Login as")
    print(bot.user.name)
    print("-------")

@bot.command(name='gex')
async def random_gex(ctx):
    if os.path.exists('textlist.txt'):
        lines = open('textlist.txt', encoding='utf-8').read().splitlines()
        text = random.choice(lines)

        image = os.listdir('./images/')
        imgString = random.choice(image)
        path = "./images/" + imgString

    await ctx.send(file=File(path))
    await ctx.send(text)

bot.run(discord_token)