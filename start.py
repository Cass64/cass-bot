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

# correspondance entre le résultat et les emojis de dés
DICE_EMOJIS = {
    1: "🎲1️⃣",
    2: "🎲2️⃣",
    3: "🎲3️⃣",
    4: "🎲4️⃣",
    5: "🎲5️⃣",
    6: "🎲6️⃣"
}
@bot.command(name="roll")
async def roll(ctx):
    # Lancer un dé (1 à 6)
    dice_result = random.randint(1, 6)
    # Récupérer l'emoji correspondant
    dice_emoji = DICE_EMOJIS[dice_result]
    # Envoyer le résultat sous forme d'emoji
    await ctx.send(f"🎲 Tu as obtenu : {dice_emoji} !")
# Quand le bot est prêt
@bot.event
async def on_ready():
    print(f"Le bot est prêt et connecté en tant que {bot.user}")

# Démarrer le bot
keep_alive()
bot.run(token)
