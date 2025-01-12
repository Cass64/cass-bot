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

@bot.event
async def on_ready():
    bot.remove_command("roll")  # Supprime les doublons éventuels
    print(f"Connecté en tant que {bot.user}")
@bot.command(name="roll")
async def roll(ctx):
    # Lancer un dé (1 à 6)
    dice_result = random.randint(1, 6)
    # Récupérer l'emoji correspondant
    dice_emoji = DICE_EMOJIS[dice_result]
    # Envoyer le résultat sous forme d'emoji
    await ctx.send(f"🎲 Tu as obtenu : {dice_emoji} !")
@bot.command(name="roll")
async def roll5(ctx):
    """Lance 5 dés."""
    dice_results = [random.randint(1, 6) for _ in range(5)]  # Lancer 5 dés
    dice_emojis = [DICE_EMOJIS[result] for result in dice_results]  # Convertir en emojis
    results_message = " | ".join(dice_emojis)  # Joindre les résultats avec des séparateurs
    await ctx.send(f"🎲 Résultats des 5 dés : {results_message}")
# Quand le bot est prêt
@bot.event
async def on_ready():
    print(f"Le bot est prêt et connecté en tant que {bot.user}")

# Démarrer le bot
keep_alive()
bot.run(token)
