import discord
from discord.ext import commands

ancien_roles = {}

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Le bot est prêt ! Connecté en tant que {self.bot.user}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ancien_roles[member.id] = [role.id for role in member.roles if role.id != member.guild.id]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.id in ancien_roles:
            roles_to_add = [discord.utils.get(member.guild.roles, id=role_id) for role_id in ancien_roles[member.id]]
            roles_to_add = [role for role in roles_to_add if role is not None]
            if roles_to_add:
                await member.add_roles(*roles_to_add)

async def setup(bot):
    await bot.add_cog(Events(bot))
