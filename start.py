import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import random
from keep_alive import keep_alive

load_dotenv()
token = os.getenv('TOKEN_BOT_DISCORD')

# Crée un objet bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

async def roll(ctx):
    result = random.randint(1, 6)  # Lancer un dé à 6 faces
    await ctx.send(f'{ctx.author.name} lance un dé et obtient : {result}')

# Quand le bot est prêt
@bot.event
async def on_ready():
    print(f"Le bot est prêt et connecté en tant que {bot.user}")

# Démarrer le bot
keep_alive()
bot.run(token)
