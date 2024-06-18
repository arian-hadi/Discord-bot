import discord 
from  discord.ext import commands
from apikey import *

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = '!', intents=intents)

@client.event
async def on_ready():
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


client.run(token)

 

