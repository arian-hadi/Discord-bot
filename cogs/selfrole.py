import discord
from discord.ext import commands, tasks
class Roles(commands.Cog):
    pass


async def setup(client):
    await client.add_cog(Roles(client))