import discord 
from  discord.ext import commands
import aiohttp
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from apikey import *
from discord.ext.commands import has_permissions, MissingPermissions
import json
import asyncio

intents = discord.Intents.all()

client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@client.event
async def on_ready():
    print('System rebooted')

class Roles(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
    @discord.ui.button(label = 'Videostar', custom_id= 'Role 1', style = discord.ButtonStyle.secondary)
    async def button1(self, interaction, button):
        role = 1259205800874999950
        user = interaction.user
        if role in [y.id for y in user.roles]:
            await user.remove_roles(user.guild.get_role(role))
            await interaction.response.send_message('You have remove a role!',
            epheneral = True)
        else:
            await user.add_roles(user.guild.get_role(role))
            await interaction.response.send_message('You have added a role!',
            epheneral = True)
    @discord.ui.button(label = 'Aftereffects', custom_id= 'Role 2', style = discord.ButtonStyle.secondary)
    async def button2(self, interaction, button):
        role = 1259205872173842545
        user = interaction.user
        if role in [y.id for y in user.roles]:
            await user.remove_roles(user.guild.get_role(role))
            await interaction.response.send_message('You have remove a role!',
            epheneral = True)
        else:
            await user.add_roles(user.guild.get_role(role))
            await interaction.response.send_message('You have added a role!',
            epheneral = True)

    @discord.ui.button(label = 'Capcut', custom_id= 'Role 3', style = discord.ButtonStyle.secondary)
    async def button3(self, interaction, button):
        role = 1259205868000645201
        user = interaction.user
        if role in [y.id for y in user.roles]:
            await user.remove_roles(user.guild.get_role(role))
            await interaction.response.send_message('You have remove a role!',
            epheneral = True)
        else:
            await user.add_roles(user.guild.get_role(role))
            await interaction.response.send_message('You have added a role!',
            epheneral = True)

    @discord.ui.button(label = 'Alight motion', custom_id= 'Role 4', style = discord.ButtonStyle.secondary)
    async def button4(self, interaction, button):
        role = 1259205864246738996
        user = interaction.user
        if role in [y.id for y in user.roles]:
            await user.remove_roles(user.guild.get_role(role))
            await interaction.response.send_message('You have remove a role!',
            epheneral = True)
        else:
            await user.add_roles(user.guild.get_role(role))
            await interaction.response.send_message('You have added a role!',
            epheneral = True)                        

@client.command()
async def roles(ctx):
    embed = discord.Embed(title = 'Role selection form.', description = 'Get your desired role!, press to add/Remove role!')
    await ctx.send(embed =  embed, view = Roles())                                      
client.run('MTI1MTg0ODk5MzY5NzE3MzYyNg.GauxMO.-URD6QWnU-dnQ1ZnTWDb39WkWVKFYdc9MN0uTs')





