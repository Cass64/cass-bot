import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive

load_dotenv()
token = os.getenv('TOKEN_BOT_DISCORD')

class MonBot(commands.Bot):
  async def setup_hook(self):
    for extension in ['games', 'moderation','events']:
      await self.load_extension(f'cogs.{extension}')
      for cog in cogs:
        if cog not in bot.extensions:
            try:
                bot.load_extension(cog)
                print(f"Extension {cog} chargée avec succès.")
            except Exception as e:
                print(f"Échec du chargement de {cog}: {str(e)}")
        else:
            print(f"Extension {cog} déjà chargée.")
    

      


intents = discord.Intents.all()
bot = MonBot(command_prefix='!', intents=intents)

keep_alive()

print(f"Token récupéré : {token}")  # Afficher le token

bot.run(token)
