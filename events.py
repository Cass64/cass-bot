import discord
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('TOKEN_BOT_DISCORD')

client = discord.Client(intents=discord.Intents.all())

class Events(client.event):
    def __init__(self, bot):
        self.bot = bot
        
        
ancien_roles = {}

@client.event
async def on_message(message: discord.Message):
  if message.author.bot:
    return
  elif message.content.lower().startswith("bonjour"):
    await message.channel.send("Bonjour, c'est le bot")


@client.event
async def on_message_delete(message: discord.Message):
  await message.channel.send(f"{message.author.name} a supprimé {message.content}")


@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
  await after.channel.send(f"{before.content} est devenu {after.content}")


@client.event
async def on_ready():
  print("Le bot est prêt")
  
 
  
@client.event
async def on_member_remove(member):
    # Sauvegarde des rôles de l'utilisateur quand il quitte, en excluant @everyone
    ancien_roles[member.id] = [role.id for role in member.roles if role.id != member.guild.id]

@client.event
async def on_member_join(member):
    if member.id in ancien_roles:
        # Récupère les rôles sauvegardés et les attribue à l'utilisateur
        roles_to_add = [discord.utils.get(member.guild.roles, id=role_id) for role_id in ancien_roles[member.id]]

        # Filtrer les rôles valides (s'assurer que le rôle existe toujours)
        roles_to_add = [role for role in roles_to_add if role is not None]

        if roles_to_add:
            await member.add_roles(*roles_to_add)  # Réattribue les rôles sauvegardés

def setup(bot):
    bot.add_cog(Events(bot))

client.run(token=token)
