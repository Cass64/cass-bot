import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import random
from keep_alive import keep_alive
load_dotenv()
token = os.getenv('TOKEN_BOT_DISCORD')

# Intents et configuration du bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!!", intents=intents)

# Correspondance entre le résultat et les emojis de dés
DICE_EMOJIS = {
    1: "🎲1️⃣",
    2: "🎲2️⃣",
    3: "🎲3️⃣",
    4: "🎲4️⃣",
    5: "🎲5️⃣",
    6: "🎲6️⃣"
}

# Dictionnaire pour stocker les rôles des membres qui quittent
ancien_roles = {}

@bot.event
async def on_ready():
    """S'exécute lorsque le bot est prêt."""
    print(f"Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")


#------------------------------------------------------------------------- Rôles automatisés quand un membre rejoint/part
@bot.event
async def on_member_remove(member):
    """Quand un membre quitte le serveur, on stocke ses rôles."""
    ancien_roles[member.id] = [role.id for role in member.roles if role.id != member.guild.id]

@bot.event
async def on_member_join(member):
    """Quand un membre rejoint le serveur, on lui réattribue ses rôles."""
    if member.id in ancien_roles:
        roles_to_add = [discord.utils.get(member.guild.roles, id=role_id) for role_id in ancien_roles[member.id]]
        roles_to_add = [role for role in roles_to_add if role is not None]  # Filtrer les rôles valides

        if roles_to_add:
            await member.add_roles(*roles_to_add)
            print(f"Rôles réattribués à {member.display_name}")


#------------------------------------------------------------------------- Jeux : Lancer de dés
@bot.tree.command(name="roll", description="Lancer un ou plusieurs dés.")
@app_commands.describe(nombre="Nombre de dés à lancer (max 20)")
async def roll_slash(interaction: discord.Interaction, nombre: int = 1):
    await roll_logic(interaction, nombre, is_slash=True)


@bot.command(name="roll")
async def roll(ctx, nombre: int = 1):
    await roll_logic(ctx, nombre, is_slash=False)


async def roll_logic(target, nombre: int, is_slash: bool):
    """Logique commune pour le lancer de dés."""
    if nombre <= 0:
        message = "⚠️ Le nombre de dés doit être supérieur à 0."
        await (target.response.send_message(message, ephemeral=True) if is_slash else target.send(message))
        return
    if nombre > 20:
        message = "⚠️ Je ne peux pas lancer plus de 20 dés à la fois."
        await (target.response.send_message(message, ephemeral=True) if is_slash else target.send(message))
        return

    # Lancer les dés
    dice_results = [random.randint(1, 6) for _ in range(nombre)]
    dice_emojis = [DICE_EMOJIS[result] for result in dice_results]
    results_message = " | ".join(dice_emojis)
    total = sum(dice_results)  # Calculer la somme des dés

    message = f"🎲 Résultats des {nombre} dés : {results_message}\n✨ Total : {total}"
    await (target.response.send_message(message) if is_slash else target.send(message))


#------------------------------------------------------------------------- Jeux : Pierre, Feuille, Ciseaux
@bot.tree.command(name="pierre-feuille-ciseaux", description="Joue à Pierre-Feuille-Ciseaux avec le bot.")
@app_commands.describe(choix="Votre choix : pierre, feuille ou ciseaux")
async def pfc_slash(interaction: discord.Interaction, choix: str):
    await pfc_logic(interaction, choix, is_slash=True)


@bot.command(name="pfc")
async def pfc(ctx, choix: str):
    await pfc_logic(ctx, choix, is_slash=False)


async def pfc_logic(target, choix: str, is_slash: bool):
    """Logique commune pour Pierre-Feuille-Ciseaux."""
    options = {
        "pierre": "🪨",
        "feuille": "🧻",
        "ciseaux": "✂️"
    }

    # Vérifier si le choix est valide
    if choix.lower() not in options:
        message = "Choix invalide ! Choisissez entre `pierre`, `feuille` ou `ciseaux`."
        await (target.response.send_message(message, ephemeral=True) if is_slash else target.send(message))
        return

    # Le bot fait un choix aléatoire
    bot_choice = random.choice(list(options.keys()))

    # Déterminer le gagnant
    if choix.lower() == bot_choice:
        result = "Égalité ! 😐"
    elif (choix.lower() == "pierre" and bot_choice == "ciseaux") or \
         (choix.lower() == "feuille" and bot_choice == "pierre") or \
         (choix.lower() == "ciseaux" and bot_choice == "feuille"):
        result = "Tu as gagné ! 🎉"
    else:
        result = "Le bot a gagné ! 😎"

    message = (
        f"Tu as choisi {options[choix.lower()]} (`{choix}`), "
        f"le bot a choisi {options[bot_choice]} (`{bot_choice}`).\n{result}"
    )
    await (target.response.send_message(message) if is_slash else target.send(message))


#------------------------------------------------------------------------- Commandes de modération : addrole et removerole
@bot.tree.command(name="addrole", description="Ajouter un rôle à un utilisateur.")
@app_commands.describe(membre="L'utilisateur à qui ajouter le rôle", role="Le rôle à ajouter")
async def addrole_slash(interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
    await role_logic(interaction, membre, role, action="add", is_slash=True)


@bot.command(name="addrole")
async def addrole(ctx, membre: discord.Member, role: discord.Role):
    await role_logic(ctx, membre, role, action="add", is_slash=False)


@bot.tree.command(name="removerole", description="Retirer un rôle d'un utilisateur.")
@app_commands.describe(membre="L'utilisateur à qui retirer le rôle", role="Le rôle à retirer")
async def removerole_slash(interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
    await role_logic(interaction, membre, role, action="remove", is_slash=True)


@bot.command(name="removerole")
async def removerole(ctx, membre: discord.Member, role: discord.Role):
    await role_logic(ctx, membre, role, action="remove", is_slash=False)


async def role_logic(target, membre: discord.Member, role: discord.Role, action: str, is_slash: bool):
    """Logique commune pour ajouter ou retirer un rôle."""
    try:
        if action == "add":
            if role in membre.roles:
                message = f"{membre.mention} a déjà le rôle {role.mention}. ✅"
            else:
                await membre.add_roles(role)
                message = f"Le rôle {role.mention} a été ajouté à {membre.mention} avec succès ! 🎉"
        elif action == "remove":
            if role not in membre.roles:
                message = f"{membre.mention} n'a pas le rôle {role.mention}. ❌"
            else:
                await membre.remove_roles(role)
                message = f"Le rôle {role.mention} a été retiré à {membre.mention} avec succès ! ✅"

        await (target.response.send_message(message) if is_slash else target.send(message))
    except discord.Forbidden:
        message = "❌ Je n'ai pas les permissions nécessaires pour effectuer cette action."
        await (target.response.send_message(message, ephemeral=True) if is_slash else target.send(message))


#------------------------------------------------------------------------- Lancement du bot
keep_alive()
bot.run(token)
