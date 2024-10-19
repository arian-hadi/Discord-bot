import discord
from discord.ext import commands, tasks
from discord import app_commands
from apikey import *  
import asyncio   
import os
from utils import *

# Replace with your specific server's ID
TARGET_GUILD_ID = 1197828306565873755  # Replace this with your server ID

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)
client.start_time = discord.utils.utcnow()

@client.event
async def on_ready():
    print("The bot is now ready for use")
    
    # Send a message to a specific channel when the bot is online
    channel = client.get_channel(channel_id)  # Ensure channel_id is defined elsewhere
    await channel.send("Teletraan Online")
    
    # Update bot's activity status
    activity = discord.Activity(type=discord.ActivityType.watching, name="over Cybertron")
    await client.change_presence(status=discord.Status.online, activity=activity)
    print(f'Logged in as {client.user}')
    
    # Leave any servers except the target one
    for guild in client.guilds:
        if guild.id != TARGET_GUILD_ID:
            await guild.leave()
            print(f"Left guild: {guild.name} ({guild.id})")

    # Sync slash commands to the specific guild
    guild = discord.Object(id=TARGET_GUILD_ID)
    try:
        synced = await client.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to the guild.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # Sync global commands
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} global commands.")
    except Exception as e:
        print(f"Failed to sync global commands: {e}")

@client.event
async def on_guild_join(guild):
    """Automatically leave any guild that is not the target one."""
    if guild.id != TARGET_GUILD_ID:
        await guild.leave()
        print(f"Left guild: {guild.name} ({guild.id})")

# Example slash command
@client.tree.command(name="ps", description="ps")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("**Error Handling:**\n"
                                            "If you get the error: 'application did not respond' Make sure to retry the command and it should work!."
        )

# Example ping command
@client.command()
async def ping(ctx):
    start = discord.utils.utcnow()  # Get the current time at the start
    latency = round(client.latency * 1000)  # Convert latency to milliseconds
    current_time = discord.utils.utcnow()  # Get current time
    uptime = discord.utils.utcnow() - client.start_time  # Calculate uptime

    # Create an embed for the response
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latency: `{latency} ms`\nUser: `{ctx.author}`\nTime: `{current_time.strftime('%Y-%m-%d %H:%M:%S')}`",
        color=discord.Color.blue()  # You can change the color if you want
    )
    
    msg = await ctx.send(embed=embed)

    end = discord.utils.utcnow()  # Get the time after sending the message
    total_time = (end - start).total_seconds() * 1000  # Total command time in ms

    # Update the embed with the total time taken and bot uptime
    embed.add_field(name="Total Time", value=f"`{total_time:.2f} ms`", inline=False)
    embed.add_field(name="Uptime", value=f"`{uptime.total_seconds():.2f} seconds`", inline=False)
    
    await msg.edit(embed=embed)

# Load cogs
async def load():
    cogs_directory = './cogs'
    if not os.path.exists(cogs_directory):
        print(f"Directory '{cogs_directory}' does not exist.")
        return

    for filename in os.listdir(cogs_directory):
        if filename.endswith('.py') and filename != '__init__.py':
            cog_name = filename[:-3]  # Strip .py extension
            try:
                await client.load_extension(f"cogs.{cog_name}")
                print(f"Loaded {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

# Main entry point
if __name__ == "__main__":
    async def main():
        await load()
        async with client:
            await client.start(token)

    asyncio.run(main())
