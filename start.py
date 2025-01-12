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

 # Liste des emojis de dé (un pour chaque face)
dice_emojis = {
    1: "gifs/dice_111.gif",
    2: "⚁",
    3: "⚂",
    4: "⚃",
    5: "⚄",
    6: "⚆"
}
@bot.command()
async def roll(ctx):
    result = random.randint(1, 6)  # Lancer un dé à 6 faces
    dice_face = dice_emojis[result]
    await ctx.send(f'{ctx.author.name} lance un dé et obtient : {dice_face} {result}')  # Affiche l'emoji et le résultat

# Quand le bot est prêt
@bot.event
async def on_ready():
    print(f"Le bot est prêt et connecté en tant que {bot.user}")

# Démarrer le bot
keep_alive()
bot.run(token)
