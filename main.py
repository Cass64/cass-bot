import os
import discord

from discord.ext import commands


# Initialisation des intents
intents = discord.Intents.default()
intents.members = True  # Permet d'écouter les événements relatifs aux membres
intents.message_content = True  # Permet de lire le contenu des messages pour les commandes
bot = commands.Bot(command_prefix="!!", intents=intents)

# Commande de test pour répondre "Bonjour"
@bot.command()
async def bonjour(ctx):
    await ctx.send(f"Bonjour {ctx.author} !")

# Dictionnaire pour stocker les anciens rôles
ancien_roles = {}

@bot.event
async def on_member_remove(member):
    # Sauvegarde des rôles de l'utilisateur quand il quitte, en excluant @everyone
    ancien_roles[member.id] = [role.id for role in member.roles if role.id != member.guild.id]

@bot.event
async def on_member_join(member):
    if member.id in ancien_roles:
        # Récupère les rôles sauvegardés et les attribue à l'utilisateur
        roles_to_add = [discord.utils.get(member.guild.roles, id=role_id) for role_id in ancien_roles[member.id]]

        # Filtrer les rôles valides (s'assurer que le rôle existe toujours)
        roles_to_add = [role for role in roles_to_add if role is not None]

        if roles_to_add:
            await member.add_roles(*roles_to_add)  # Réattribue les rôles sauvegardés

# Récupère le token à partir des variables d'environnement
token = os.environ['TOKEN_BOT_DISCORD']
bot.run(token)
