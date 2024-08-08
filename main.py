import discord 
from  discord.ext import commands
from apikey import channel_id,token 
import asyncio, os

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = '!', intents=intents)

@client.event
async def on_ready():
    channel = client.get_channel(channel_id)
    print ("The bot is now ready for use")
    print("------------------------------")
    await channel.send(f"{client.user} online")

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f"cogs.{filename[:-3]}")


if __name__ == "__main__":
    async def main():
        await load()
        async with client:
            await client.start(token)
    asyncio.run (main())



