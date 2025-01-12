import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive

load_dotenv()
token = os.getenv('TOKEN_BOT_DISCORD')

class MonBot(commands.Bot):
    async def setup_hook(self):
        cogs = ['cogs.games', 'cogs.moderation', 'cogs.events']
        for cog in cogs:
            if cog not in self.extensions:  # Vérifie si le cog est déjà chargé
                try:
                    await self.load_extension(cog)
                    print(f"Extension {cog} chargée avec succès.")
                except Exception as e:
                    print(f"Échec du chargement de {cog}: {str(e)}")
            else:
                print(f"Extension {cog} déjà chargée.")

intents = discord.Intents.all()
bot = MonBot(command_prefix='!', intents=intents)

keep_alive()

bot.run(token)
