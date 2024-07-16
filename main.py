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
intents.members = True
client = commands.Bot(command_prefix = '!', intents=intents)
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True


@client.event
async def on_ready():
    await client.tree.sync()
    print ("The bot is now ready for use")
    print("------------------------------")

@client.command()
async def hello (ctx):
    await ctx.send("Hello I am your Discord bot")

@client.command()
async def bye (ctx):
    await ctx.send("Goodbye! take care!")

@client.event
async def on_member_join(member):
    channel = client.get_channel(channel_id)
    await channel.send(f"{member.mention}")
    myembed = discord.Embed(
        title = "Welcome to the server",
        description=f"| Check Out Other Channels to get started!! |\n <#1252240278257926207>",
        color =0x5900b3
        )
    myembed.set_author(name = member.display_name, icon_url = member.display_avatar.url)
    myembed.set_thumbnail(url = member.display_avatar)
    myembed.add_field(name="\u200b", value="❄ ENJOY YOUR STAY IN THE SERVER :DD ❄", inline=False)
    myembed.set_image(url=gif)
    await channel.send(embed=myembed)
    

@client.event
async def on_member_remove(member):
    channel = client.get_channel(channel_id)
    await channel.send(f"Goodbye {member}!", )
    
@client.command(pass_context = True)
async def join(ctx):
    pass

#Self roles section
async def on_ready():
    print('system rebboted!')
    client.add_view(Roles())

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





