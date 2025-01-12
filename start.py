import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive

load_dotenv()
token = os.getenv('TOKEN_BOT_DISCORD')

class MonBot(commands.Bot):
    async def setup_hook(self):
   

intents = discord.Intents.all()
bot = MonBot(command_prefix='!', intents=intents)

# Démarre le bot une seule fois ici
keep_alive()
bot.run(token)
