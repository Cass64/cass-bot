import os  
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import random
from keep_alive import keep_alive
import json
import asyncio

SANCTION_FILE = "sanctions.json"

def load_sanctions():
    """Charge les sanctions depuis le fichier JSON."""
    try:
        with open(SANCTION_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_sanctions(data):
    """Sauvegarde les sanctions dans le fichier JSON."""
    with open(SANCTION_FILE, "w") as file:
        json.dump(data, file, indent=4)


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
     # Définir le statut du bot sur invisible
    await bot.change_presence(status=discord.Status.invisible)
    print(f"Bot connecté mais invisible en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")

#------------------------------------------------------------------------- Menu Help
bot.remove_command("help")
@bot.command(name="help")
async def help_command(ctx):
    """Affiche un joli message d'aide avec des catégories."""
    embed = discord.Embed(
        title="📖 Aide du Bot",
        description="Voici les différentes commandes disponibles :",
        color=discord.Color.blurple()  # Couleur principale de l'embed
    )

    # Catégorie Jeux
    embed.add_field(
        name="🎲 **Jeux**",
        value=(
            "`!!roll [nombre]` : Lance un ou plusieurs dés (max 20).\n"
            "`/roll [nombre]` : Variante slash pour lancer des dés.\n"
            "`!!pfc <pierre|feuille|ciseaux>` : Joue à Pierre-Feuille-Ciseaux.\n"
            "`/pierre-feuille-ciseaux` : Variante slash pour Pierre-Feuille-Ciseaux."
        ),
        inline=False
    )

    # Catégorie Modération
    embed.add_field(
        name="🔨 **Modération**",
        value=(
            "`!!addrole @utilisateur @role` : Ajoute un rôle à un utilisateur.\n"
            "`!!removerole @utilisateur @role` : Retire un rôle d'un utilisateur.\n"
            "`/addrole` : Variante slash pour ajouter un rôle.\n"
            "`/removerole` : Variante slash pour retirer un rôle."
        ),
        inline=False
    )

    # Ajouter une image ou un avatar
    embed.set_thumbnail(url=bot.user.avatar.url)

    # Note en bas du message
    embed.set_footer(text="Merciii d'utiliser mon bot !!!")

    # Envoyer l'embed
    await ctx.send(embed=embed)


@bot.tree.command(name="help", description="Affiche un joli message d'aide avec des catégories.")
async def help_slash(interaction: discord.Interaction):
    """Affiche un joli message d'aide en tant que commande slash."""
    embed = discord.Embed(
        title="📖 Aide du Bot",
        description="Voici les différentes commandes disponibles :",
        color=discord.Color.blurple()  # Couleur principale de l'embed
    )

    # Catégorie Jeux
    embed.add_field(
        name="🎲 **Jeux**",
        value=(
            "`!!roll [nombre]` : Lance un ou plusieurs dés (max 20).\n"
            "`/roll [nombre]` : Variante slash pour lancer des dés.\n"
            "`!!pfc <pierre|feuille|ciseaux>` : Joue à Pierre-Feuille-Ciseaux.\n"
            "`/pierre-feuille-ciseaux` : Variante slash pour Pierre-Feuille-Ciseaux."
        ),
        inline=False
    )

    # Catégorie Modération
    embed.add_field(
        name="🔨 **Modération**",
        value=(
            "`!!addrole @utilisateur @role` : Ajoute un rôle à un utilisateur.\n"
            "`!!removerole @utilisateur @role` : Retire un rôle d'un utilisateur.\n"
            "`/addrole` : Variante slash pour ajouter un rôle.\n"
            "`/removerole` : Variante slash pour retirer un rôle."
        ),
        inline=False
    )

    # Ajouter une image ou un avatar
    embed.set_thumbnail(url=bot.user.avatar.url)

    # Note en bas du message
    embed.set_footer(text="Merciii d'utiliser mon bot !!!")

    # Réponse de la commande slash
    await interaction.response.send_message(embed=embed)


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

    # Si c'est une commande slash, utiliser la méthode followup
    if is_slash:
        await target.response.send_message("Traitement en cours...")  # Réponse initiale
        await target.followup.send(message)  # Utilisation de followup pour envoyer les résultats
    else:
        await target.send(message)  # Envoi du message si ce n'est pas une commande slash

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

from discord.ext import commands

# Liste des rôles autorisés pour exécuter les commandes de modération
AUTHORIZED_ROLES = ["・A-Keys", "Kage", "'⭐️", "・Garde Royale"]

def check_permissions(ctx):
    """Vérifie si l'utilisateur a un rôle autorisé pour exécuter la commande."""
    for role in ctx.author.roles:
        if role.name in AUTHORIZED_ROLES:
            return True
    return False

async def role_logic(target, membre: discord.Member, role: discord.Role, action: str, is_slash: bool):
    """Logique commune pour ajouter ou retirer un rôle."""
    
    if not check_permissions(target):
        message = "❌ Vous n'avez pas les permissions nécessaires pour exécuter cette commande."
        await (target.response.send_message(message, ephemeral=True) if is_slash else target.send(message))
        return
    
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

# Commande "addrole"

@bot.command(name="addrole")
async def addrole(ctx, membre: discord.Member, role: discord.Role):
    await role_logic(ctx, membre, role, action="add", is_slash=False)

# Commande "removerole"

@bot.command(name="removerole")
async def removerole(ctx, membre: discord.Member, role: discord.Role):
    await role_logic(ctx, membre, role, action="remove", is_slash=False)

#------------------------------------------------------------------------- Commandes Slash : addrole et removerole


async def check_permissions(interaction: discord.Interaction) -> bool:
    """Vérifie si l'utilisateur a un rôle autorisé pour exécuter la commande."""
    user_roles = [role.name for role in interaction.user.roles]
    return any(role in AUTHORIZED_ROLES for role in user_roles)

async def role_logic_slash(interaction: discord.Interaction, membre: discord.Member, role: discord.Role, action: str):
    """Logique commune pour ajouter ou retirer un rôle avec une commande slash."""
    if not await check_permissions(interaction):
        await interaction.response.send_message(
            "❌ Vous n'avez pas les permissions nécessaires pour exécuter cette commande.",
            ephemeral=True,
        )
        return

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

        await interaction.response.send_message(message)
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Je n'ai pas les permissions nécessaires pour effectuer cette action.",
            ephemeral=True,
        )
    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"❌ Une erreur s'est produite lors de l'exécution de la commande : {e}",
            ephemeral=True,
        )

@bot.tree.command(name="addrole", description="Ajoute un rôle à un utilisateur.")
@app_commands.describe(membre="Le membre à qui ajouter le rôle", role="Le rôle à ajouter")
async def addrole_slash(interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
    await role_logic_slash(interaction, membre, role, action="add")

@bot.tree.command(name="removerole", description="Retire un rôle d'un utilisateur.")
@app_commands.describe(membre="Le membre à qui retirer le rôle", role="Le rôle à retirer")
async def removerole_slash(interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
    await role_logic_slash(interaction, membre, role, action="remove")

#------------------------------------------------------------------------- Sanction lister


@bot.tree.command(name="sanction", description="Afficher les sanctions émises pour un utilisateur.")
@app_commands.describe(member="L'utilisateur dont vous voulez voir les sanctions.")
async def sanction(interaction: discord.Interaction, member: discord.Member):
    """Affiche les sanctions depuis les logs d'audit pour un membre et les sauvegarde dans un fichier JSON."""
    guild = interaction.guild

    # Vérification des permissions par rôle
    user_roles = [role.name for role in interaction.user.roles]
    if not any(role in AUTHORIZED_ROLES for role in user_roles):
        await interaction.response.send_message(
            "Vous n'avez pas la permission d'utiliser cette commande.", 
            ephemeral=True
        )
        return

    await interaction.response.defer()  # Évite les timeouts de Discord

    # Charger les sanctions existantes
    sanctions_data = load_sanctions()
    sanctions_count = 0
    embed = discord.Embed(
        title=f"Sanctions pour {member.display_name}",
        description=f"Historique des sanctions appliquées à {member.mention}.",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else guild.icon.url if guild.icon else None)
    embed.set_footer(text=f"Commande exécutée par {interaction.user}", icon_url=interaction.user.avatar.url)

    try:
        async for log in guild.audit_logs(limit=50):  # Limitez à 50 logs pour éviter la surcharge
            if log.target.id == member.id and log.action in [
                discord.AuditLogAction.kick,
                discord.AuditLogAction.ban,
                discord.AuditLogAction.unban,
                discord.AuditLogAction.mute,
                discord.AuditLogAction.unmute
            ]:
                sanctions_count += 1
                action_name = log.action.name.replace("_", " ").capitalize()
                reason = log.reason if log.reason else "Aucune raison fournie"

                # Ajouter au fichier JSON
                if str(member.id) not in sanctions_data:
                    sanctions_data[str(member.id)] = []

                sanctions_data[str(member.id)].append({
                    "action": action_name,
                    "moderator": log.user.id,
                    "date": log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "reason": reason
                })

                # Ajouter à l'embed pour afficher en temps réel
                embed.add_field(
                    name=f"Action : {action_name}",
                    value=f"Effectuée par : {log.user.mention}\nDate : {log.created_at.strftime('%Y-%m-%d %H:%M:%S')}\nRaison : {reason}",
                    inline=False
                )

        # Sauvegarder les sanctions mises à jour
        save_sanctions(sanctions_data)

    except Exception as e:
        embed.description = f"Erreur lors de l'analyse des logs : {e}"
        sanctions_count = 0

    if sanctions_count == 0:
        embed.description = "Aucune sanction trouvée pour cet utilisateur."

    await interaction.followup.send(embed=embed)
    
#------------------------------------------------------------------------- Course de cheveaux


@bot.command(name="parier")
async def parier(ctx, cheval: int, mise: int):
    """Permet aux utilisateurs de parier sur un cheval."""
    global pari_en_cours

    chevaux = ["🐎", "🐴", "🦄", "🐐"]  # Les chevaux disponibles

    if not pari_en_cours:
        await ctx.send("❌ Les paris ne sont pas ouverts pour le moment.")
        return

    if cheval < 1 or cheval > len(chevaux):
        await ctx.send(f"❌ Cheval invalide ! Choisissez un numéro entre 1 et {len(chevaux)}.")
        return

    user = ctx.author

    # Enregistrer le pari
    paris[user.id] = {"cheval": cheval, "mise": mise}
    await ctx.send(f"✅ {user.mention} a parié {mise} points sur le cheval {cheval} {chevaux[cheval - 1]} !")

@bot.command(name="course")
async def horse_race(ctx):
    """Lance une course de chevaux avec animation !"""
    global pari_en_cours, paris

    chevaux = ["🐎", "🐴", "🦄", "🐐"]  # Les chevaux
    piste_longueur = 20  # Longueur de la piste
    positions = [0] * len(chevaux)  # Positions de départ
    pari_en_cours = True  # Les paris sont ouverts
    paris = {}  # Réinitialiser les paris

    # Annonce de début et ouverture des paris
    await ctx.send(
        "🎉 **La course de chevaux commence !** 🎉\n\n"
        "📢 Placez vos paris avec `!!parier <numéro du cheval> <mise>`.\n"
        "Exemple : `!!parier 2 50`\n\n"
        "Les chevaux participants :\n"
        + "\n".join([f"{i + 1}. {chevaux[i]}" for i in range(len(chevaux))])
    )
    await asyncio.sleep(20)  # Temps pour les paris rallongé

    pari_en_cours = False  # Fermeture des paris
    await ctx.send("⏳ Les paris sont fermés ! La course commence maintenant ! 🏁")

    # Construire une représentation visuelle initiale
    def construire_piste():
        piste = []
        for i, cheval in enumerate(chevaux):
            progress = "—" * positions[i]  # La progression du cheval
            space = " " * (piste_longueur - positions[i] - 1)  # Reste de la piste
            piste.append(f"|{progress}{cheval}{space}| 🏁")  # Ligne d'arrivée fixe
        return "\n".join(piste)

    # Envoyer le message initial
    message = await ctx.send("🚩 **La course commence !** 🚩\n" + construire_piste())

    # Animation de la course
    gagnant = None
    while not gagnant:
        await asyncio.sleep(0.5)  # Temps plus court pour plus de fluidité
        for i in range(len(chevaux)):
            avance = random.randint(1, 2)  # Les chevaux avancent aléatoirement
            positions[i] += avance
            if positions[i] >= piste_longueur:
                gagnant = i + 1  # Le gagnant est trouvé
                break

        # Mettre à jour le message avec la nouvelle position
        await message.edit(content="🚩 **La course continue !** 🚩\n" + construire_piste())

    # Annoncer le gagnant
    gagnants_paris = [
        user_id
        for user_id, pari in paris.items()
        if pari["cheval"] == gagnant
    ]
    gagnants_mentions = ", ".join([f"<@{user_id}>" for user_id in gagnants_paris])

    resultat_message = (
        f"🏆 **Le cheval {gagnant} {chevaux[gagnant - 1]} a gagné la course !** 🥇\n"
    )
    if gagnants_mentions:
        resultat_message += (
            f"🎉 Félicitations aux gagnants : {gagnants_mentions} !\n"
        )
    else:
        resultat_message += "😢 Aucun pari gagnant cette fois-ci."

    await ctx.send(resultat_message)


#------------------------------------------------------------------------- Lancement du bot
keep_alive()
bot.run(token)
