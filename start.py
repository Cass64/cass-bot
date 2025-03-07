import os  
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import random
from keep_alive import keep_alive
import json
import asyncio
import yt_dlp
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

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

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
AUTHORIZED_ROLES = ["・A-Keys", "Kage", "'⭐️", "・Garde Royale", "Azkaban"]

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
    """Permet de parier sur un cheval."""
    global pari_en_cours, paris, chevaux

    if not pari_en_cours:
        await ctx.send("❌ Les paris ne sont pas ouverts pour le moment.")
        return

    if cheval < 1 or cheval > len(chevaux):
        await ctx.send(f"❌ Cheval invalide ! Choisissez un numéro entre 1 et {len(chevaux)}.")
        return

    user = ctx.author
    paris[user.id] = {"cheval": cheval, "mise": mise}

    await ctx.send(f"✅ {user.mention} a parié {mise} points sur le cheval {cheval} {chevaux[cheval - 1]} !")

@bot.command(name="course")
async def horse_race(ctx):
    """Lance une course de chevaux où les chevaux avancent vers une ligne d'arrivée fixe."""
    global pari_en_cours, paris, chevaux

    chevaux = ["🐎", "🐴", "🦄", "🐐"]
    distance_totale = 30  # Nombre de cases fixes avant la ligne d'arrivée
    positions = [0] * len(chevaux)  # Positions initiales des chevaux
    pari_en_cours = True
    paris = {}

    # Phase des paris
    embed = discord.Embed(
        title="🎠 Course de chevaux !",
        description="📢 Placez vos paris avec `!!parier <numéro du cheval> <mise>`.\n"
                    "Exemple : `!!parier 2 50`\n\n"
                    "Les chevaux participants :",
        color=discord.Color.gold()
    )
    for i, cheval in enumerate(chevaux):
        embed.add_field(name=f"Cheval {i + 1}", value=cheval, inline=True)

    await ctx.send(embed=embed)
    await asyncio.sleep(15)  # Temps pour parier

    pari_en_cours = False
    await ctx.send("⏳ Les paris sont fermés ! La course commence 🏁 !")

    def construire_piste():
        piste = []
        for i, cheval in enumerate(chevaux):
            # Ajoute des espaces pour représenter la progression
            piste.append(f"{cheval} {'-' * positions[i]}{' ' * (distance_totale - positions[i])}🏁")
        return "\n".join(piste)

    # Crée l'embed de la course
    course_embed = discord.Embed(
        title="🚩 La course commence !",
        color=discord.Color.blue()
    )
    course_embed.description = construire_piste()
    message_course = await ctx.send(embed=course_embed)

    gagnant = None
    while not gagnant:
        await asyncio.sleep(1)  # Animation fluide
        for i in range(len(chevaux)):
            avance = random.randint(1, 2)  # Chaque cheval avance de 1 ou 2 cases
            positions[i] += avance
            if positions[i] >= distance_totale:
                gagnant = i + 1
                break

        course_embed.description = construire_piste()
        await message_course.edit(embed=course_embed)

    gagnants_paris = [
        user_id
        for user_id, pari in paris.items()
        if pari["cheval"] == gagnant
    ]
    gagnants_mentions = ", ".join([f"<@{user_id}>" for user_id in gagnants_paris])

    resultat_embed = discord.Embed(
        title=f"🏆 Le cheval {gagnant} {chevaux[gagnant - 1]} a gagné !",
        description=f"🎉 Félicitations aux gagnants : {gagnants_mentions}" if gagnants_mentions else "😢 Aucun pari gagnant cette fois-ci.",
        color=discord.Color.green()
    )
    await ctx.send(embed=resultat_embed)

#------------------------------------------------------------------------- Ban/unban

### Commande BAN (préfixe et slash)
@bot.command(name="ban")
async def ban(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    """Bannit un utilisateur avec !!ban"""
    
    if not has_authorized_role(ctx.author):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.", delete_after=5)
        return

    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} a été banni. Raison : {reason}")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de bannir cet utilisateur.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur est survenue : {e}")


@bot.tree.command(name="ban", description="Bannir un utilisateur du serveur.")
@app_commands.describe(member="L'utilisateur à bannir.", reason="Raison du bannissement (optionnelle).")
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison spécifiée"):
    """Bannit un utilisateur avec /ban"""
    
    if not has_authorized_role(interaction.user):
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        await member.ban(reason=reason)
        await interaction.followup.send(f"✅ {member.mention} a été banni. Raison : {reason}")
    except discord.Forbidden:
        await interaction.followup.send("❌ Je n'ai pas la permission de bannir cet utilisateur.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue : {e}", ephemeral=True)


### Commande UNBAN (préfixe et slash)
@bot.command(name="unban")
async def unban(ctx, user_id: int):
    """Débannit un utilisateur avec !!unban"""
    
    if not has_authorized_role(ctx.author):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.", delete_after=5)
        return

    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.mention} a été débanni.")
    except discord.NotFound:
        await ctx.send("❌ L'utilisateur avec cet ID n'est pas banni ou n'existe pas.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de débannir cet utilisateur.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur est survenue : {e}")


@bot.tree.command(name="unban", description="Débannir un utilisateur du serveur.")
@app_commands.describe(user_id="L'ID de l'utilisateur à débannir.")
async def slash_unban(interaction: discord.Interaction, user_id: str):
    """Débannit un utilisateur avec /unban"""
    
    if not has_authorized_role(interaction.user):
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        user = await bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.followup.send(f"✅ {user.mention} a été débanni.")
    except discord.NotFound:
        await interaction.followup.send("❌ L'utilisateur avec cet ID n'est pas banni ou n'existe pas.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("❌ Je n'ai pas la permission de débannir cet utilisateur.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue : {e}", ephemeral=True)

#-------------------------------------------------------------------------------------------------------------------------------------------------- MUSIQUE

# Options pour yt-dlp (pour extraire l'audio)
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

# Fonction pour extraire les infos d'une musique
def extract_info(query, download=False):
    try:
        info = ytdl.extract_info(query, download=download)
    except Exception as e:
        print(f"Erreur d'extraction: {e}")
        return None
    if 'entries' in info:
        # Si c'est une playlist, on prend le premier résultat
        info = info['entries'][0]
    return info

# Classe pour représenter une musique
class Song:
    def __init__(self, info):
        self.source = info['url']              # URL pour FFmpeg
        self.title = info.get('title')
        self.webpage_url = info.get('webpage_url')
        self.duration = info.get('duration')    # en secondes
        self.uploader = info.get('uploader')
        self.thumbnail = info.get('thumbnail')

    def formatted_duration(self):
        mins, secs = divmod(self.duration, 60)
        return f"{mins}:{secs:02}"

# Classe pour gérer la lecture et la file d'attente par serveur (guild)
class MusicPlayer:
    def __init__(self, bot, interaction: discord.Interaction):
        self.bot = bot
        self.queue = []           # file d'attente
        self.current = None       # musique en cours
        self.voice_client = None  # connexion vocale
        self.text_channel = interaction.channel
        self.guild = interaction.guild
        self.lock = asyncio.Lock()

    # Se connecter à un salon vocal
    async def connect(self, voice_channel: discord.VoiceChannel):
        if self.voice_client is None or not self.voice_client.is_connected():
            self.voice_client = await voice_channel.connect()
        return self.voice_client

    # Lancer la lecture d'une musique
    async def play_song(self, song: Song):
        self.current = song
        if not self.voice_client:
            return
        source = discord.FFmpegPCMAudio(song.source, **ffmpeg_options)
        def after_playing(error):
            if error:
                print(f"Erreur pendant la lecture: {error}")
            # Lancer la lecture de la musique suivante
            asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop)
        self.voice_client.play(source, after=after_playing)
        await self.send_now_playing(song)

    # Passer à la musique suivante
    async def play_next(self):
        async with self.lock:
            if self.queue:
                next_song = self.queue.pop(0)
                await self.play_song(next_song)
            else:
                self.current = None
                if self.voice_client:
                    await self.voice_client.disconnect()
                    self.voice_client = None

    # Ajouter une musique à la file (limite à 10 titres)
    async def add_to_queue(self, song: Song):
        if len(self.queue) >= 10:
            return False
        self.queue.append(song)
        return True

    # Envoyer un embed "Lecture en cours" avec les boutons
    async def send_now_playing(self, song: Song):
        embed = discord.Embed(
            title="Lecture en cours",
            description=f"[{song.title}]({song.webpage_url})",
            color=discord.Color.blue()
        )
        embed.add_field(name="Auteur", value=song.uploader or "Inconnu", inline=True)
        embed.add_field(name="Durée", value=song.formatted_duration(), inline=True)
        if song.thumbnail:
            embed.set_thumbnail(url=song.thumbnail)
        view = NowPlayingView(self)
        await self.text_channel.send(embed=embed, view=view)

# Dictionnaire pour stocker un MusicPlayer par guild
music_players = {}

# Vue avec les boutons pour le "Lecture en cours"
class NowPlayingView(discord.ui.View):
    def __init__(self, player: MusicPlayer):
        super().__init__(timeout=None)
        self.player = player

    @discord.ui.button(label="Pause / Reprendre", style=discord.ButtonStyle.secondary, custom_id="pause_song")
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.player.voice_client
        if vc is None or not vc.is_playing():
            await interaction.response.send_message("Aucune musique en cours.", ephemeral=True)
            return
        if vc.is_paused():
            vc.resume()
            await interaction.response.send_message("La musique a été reprise !", ephemeral=True)
        else:
            vc.pause()
            await interaction.response.send_message("La musique a été mise en pause !", ephemeral=True)

    @discord.ui.button(label="Passer", style=discord.ButtonStyle.primary, custom_id="skip_song")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.player.voice_client
        if vc is None or not vc.is_playing():
            await interaction.response.send_message("Aucune musique n'est en cours.", ephemeral=True)
            return
        vc.stop()  # Cela déclenchera le callback et lancera la musique suivante
        await interaction.response.send_message("Musique passée !", ephemeral=True)

    @discord.ui.button(label="Stop / Quitter", style=discord.ButtonStyle.danger, custom_id="stop_song")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.player.voice_client
        if vc is None:
            await interaction.response.send_message("Aucune musique n'est en cours.", ephemeral=True)
            return
        self.player.queue.clear()
        vc.stop()
        await vc.disconnect()
        self.player.voice_client = None
        await interaction.response.send_message("La musique a été arrêtée et le bot a quitté le salon vocal !", ephemeral=True)

# Vue avec boutons pour la commande /queue
class QueueView(discord.ui.View):
    def __init__(self, player: MusicPlayer):
        super().__init__(timeout=None)
        self.player = player

    @discord.ui.button(label="Vider la file", style=discord.ButtonStyle.danger, custom_id="clear_queue")
    async def clear_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.queue.clear()
        await interaction.response.send_message("La file d'attente a été vidée !", ephemeral=True)

    @discord.ui.button(label="Ajouter une musique", style=discord.ButtonStyle.primary, custom_id="add_queue")
    async def add_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Pour ajouter une musique, utilisez la commande `/play <url|nom>` !", ephemeral=True)

# Création du bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Fonction d'autocomplétion pour la commande /play (exemple basique)
async def play_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=f"{current} - Artiste1", value=f"{current} - Artiste1"),
        app_commands.Choice(name=f"{current} - Artiste2", value=f"{current} - Artiste2"),
        app_commands.Choice(name=f"{current} - Artiste3", value=f"{current} - Artiste3"),
    ]

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}!')
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commandes synchronisées.")
    except Exception as e:
        print(e)

# Commande slash /play
@bot.tree.command(name="play", description="Joue une musique ou l'ajoute à la file d'attente.")
@app_commands.describe(query="URL ou nom de la musique")
@app_commands.autocomplete(query=play_autocomplete)
async def play(interaction: discord.Interaction, query: str):
    # Vérification que l'utilisateur est dans un salon vocal
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        await interaction.response.send_message("Vous devez être dans un salon vocal pour utiliser cette commande !", ephemeral=True)
        return
    voice_channel = interaction.user.voice.channel

    # Récupérer ou créer le MusicPlayer pour ce serveur
    player = music_players.get(interaction.guild.id)
    if player is None:
        player = MusicPlayer(bot, interaction)
        music_players[interaction.guild.id] = player

    await interaction.response.send_message(f"Recherche de **{query}** en cours…", ephemeral=True)

    # Extraction des informations de la musique
    info = extract_info(query, download=False)
    if info is None:
        await interaction.followup.send("Impossible de récupérer les informations de la musique.")
        return
    song = Song(info)

    # Connexion au salon vocal si besoin
    await player.connect(voice_channel)

    # Si une musique est déjà en cours, on ajoute à la file d'attente
    if player.voice_client.is_playing() or player.current is not None:
        success = await player.add_to_queue(song)
        if not success:
            await interaction.followup.send("La file d'attente est pleine (limite de 10 musiques)!")
        else:
            await interaction.followup.send(f"**{song.title}** a été ajoutée à la file d'attente.")
    else:
        await player.play_song(song)

# Commande slash /queue
@bot.tree.command(name="queue", description="Affiche la file d'attente actuelle.")
async def queue(interaction: discord.Interaction):
    player = music_players.get(interaction.guild.id)
    if player is None or (player.current is None and not player.queue):
        await interaction.response.send_message("Il n'y a aucune musique dans la file d'attente !", ephemeral=True)
        return

    embed = discord.Embed(title="File d'attente", color=discord.Color.green())
    description = ""
    if player.current:
        description += f"**En cours :** [{player.current.title}]({player.current.webpage_url}) - {player.current.formatted_duration()}\n"
    if player.queue:
        for idx, song in enumerate(player.queue, start=1):
            description += f"{idx}. [{song.title}]({song.webpage_url}) - {song.formatted_duration()}\n"
    embed.description = description
    view = QueueView(player)
    await interaction.response.send_message(embed=embed, view=view)

#------------------------------------------------------------------------- Lancement du bot
keep_alive()
bot.run(token)
