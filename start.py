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
bot = commands.Bot(command_prefix='!!', intents=intents)

# Dictionnaire pour stocker les rôles des membres qui quittent
ancien_roles = {}

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
    print(f"Connecté en tant que {bot.user}")

@bot.event
async def on_member_remove(member):
    """Quand un membre quitte le serveur, on stocke ses rôles."""
    ancien_roles[member.id] = [role.id for role in member.roles if role.id != member.guild.id]

@bot.event
async def on_member_join(member):
    """Quand un membre rejoint le serveur, on lui réattribue ses rôles."""
    if member.id in ancien_roles:
        # Récupère les rôles sauvegardés et les attribue au membre
        roles_to_add = [discord.utils.get(member.guild.roles, id=role_id) for role_id in ancien_roles[member.id]]

        # Filtrer les rôles valides (s'assurer que le rôle existe toujours)
        roles_to_add = [role for role in roles_to_add if role is not None]

        if roles_to_add:
            await member.add_roles(*roles_to_add)  # Réattribue les rôles

@bot.command(name="roll")
async def roll(ctx):
    """Lance un dé (1 à 6)"""
    dice_result = random.randint(1, 6)
    dice_emoji = DICE_EMOJIS[dice_result]
    await ctx.send(f"🎲 Tu as obtenu : {dice_emoji} !")

@bot.command(name="roll2")
async def roll2(ctx):
    """Lance 2 dés."""
    dice_results = [random.randint(1, 6) for _ in range(2)]
    dice_emojis = [DICE_EMOJIS[result] for result in dice_results]
    results_message = " | ".join(dice_emojis)
    await ctx.send(f"🎲 Résultats des 2 dés : {results_message}")

@bot.command(name="roll3")
async def roll3(ctx):
    """Lance 3 dés."""
    dice_results = [random.randint(1, 6) for _ in range(3)]
    dice_emojis = [DICE_EMOJIS[result] for result in dice_results]
    results_message = " | ".join(dice_emojis)
    await ctx.send(f"🎲 Résultats des 3 dés : {results_message}")

@bot.command(name="roll4")
async def roll4(ctx):
    """Lance 4 dés."""
    dice_results = [random.randint(1, 6) for _ in range(4)]
    dice_emojis = [DICE_EMOJIS[result] for result in dice_results]
    results_message = " | ".join(dice_emojis)
    await ctx.send(f"🎲 Résultats des 4 dés : {results_message}")

@bot.command(name="roll5")
async def roll5(ctx):
    """Lance 5 dés."""
    dice_results = [random.randint(1, 6) for _ in range(5)]
    dice_emojis = [DICE_EMOJIS[result] for result in dice_results]
    results_message = " | ".join(dice_emojis)
    await ctx.send(f"🎲 Résultats des 5 dés : {results_message}")

# Démarrer le bot
keep_alive()
bot.run(token)
