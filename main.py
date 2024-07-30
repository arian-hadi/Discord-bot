import discord 
from  discord.ext import commands
from apikey import *
import asyncio, os


intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = '!', intents=intents)



@client.event
async def on_ready():
    channel = client.get_channel(channel_id)
    # check_new_videos.start()
    print("The bot is now ready for use")
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
# @client.event
# async def on_ready():
#     channel = client.get_channel(channel_id)
#     #check_new_videos.start()
#     print ("The bot is now ready for use")
#     print("------------------------------")

# initial_extentions = []

# for filename in os.listdir("./cogs"):
#     if filename.endswith(".py"):
#         initial_extentions.append("cogs." + filename[:-3])
    


# if __name__ == "__main__":
#     async def main():
#         for extention in initial_extentions:
#             await client.load_extension(extention)
#             await client.start(token)
            

#     asyncio.run(main())
