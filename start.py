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

#------------------------------------------------------------------------- Rôles automatiser quand on rerejoint le serv

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

#------------------------------------------------------------------------- Jeux roll (rool1--> roll5)

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

#------------------------------------------------------------------------- Jeux personnalisés

@bot.command(name="rollp")
async def rollp(ctx, nombre: int = 1):
    """
    Lancer un nombre personnalisé de dés (par défaut 1).
    Utilisation : !!rollp<nombre>
    """
    if nombre <= 0:
        await ctx.send("⚠️ Le nombre de dés doit être supérieur à 0.")
        return
    if nombre > 20:
        await ctx.send("⚠️ Je ne peux pas lancer plus de 20 dés à la fois.")
        return

    # Lancer les dés
    dice_results = [random.randint(1, 6) for _ in range(nombre)]
    dice_emojis = [DICE_EMOJIS[result] for result in dice_results]
    results_message = " | ".join(dice_emojis)
    total = sum(dice_results)  # Calculer la somme des dés

    await ctx.send(f"🎲 Résultats des {nombre} dés : {results_message}\n✨ Total : {total}")

#------------------------------------------------------------------------- Jeux feuille, caillou, ciseau

@bot.command(name="pfc")
async def pierre_feuille_ciseaux(ctx, choix: str):
    """
    Joue à Pierre-Feuille-Ciseaux avec le bot.
    """
    # Liste des options avec les emojis correspondants
    options = {
        "pierre": "🪨",  # Emoji pour pierre
        "feuille": "🧻",  # Emoji pour feuille
        "ciseaux": "✂️"   # Emoji pour ciseaux
    }

    # Vérifier si le choix est valide
    if choix.lower() not in options:
        await ctx.send("Choix invalide ! Choisissez entre `pierre`, `feuille` ou `ciseaux`.")
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

    # Envoyer le résultat avec les emojis
    await ctx.send(
        f"Tu as choisi {options[choix.lower()]} (`{choix}`), "
        f"le bot a choisi {options[bot_choice]} (`{bot_choice}`).\n{result}"
    )

#------------------------------------------------------------------------- Commandes de modération

@bot.command(name="addrole")
@commands.has_any_role("':star:", "・A-Keys")  # Limite la commande à ces rôles
async def add_role(ctx, membre: discord.Member, role: discord.Role):
    """
    Ajoute un rôle spécifique à un utilisateur.
    Utilisation : !!addrole @utilisateur @role
    """
    try:
        # Vérifie si le rôle est déjà attribué
        if role in membre.roles:
            await ctx.send(f"{membre.mention} a déjà le rôle {role.mention}. ✅")
            return

        # Ajoute le rôle au membre
        await membre.add_roles(role)
        await ctx.send(f"Le rôle {role.mention} a été ajouté à {membre.mention} avec succès ! 🎉")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions nécessaires pour attribuer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Une erreur s'est produite : {str(e)}")
    except Exception as e:
        await ctx.send(f"❌ Une erreur inconnue est survenue : {str(e)}")

@add_role.error
async def add_role_error(ctx, error):
    """Gère les erreurs de la commande addrole."""
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Utilisation incorrecte de la commande. Exemple : `!!addrole @utilisateur @role`.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Membre ou rôle invalide. Mentionnez correctement l'utilisateur et le rôle.")
    else:
        await ctx.send("❌ Une erreur inconnue est survenue.")



# Démarrer le bot
keep_alive()
bot.run(token)
