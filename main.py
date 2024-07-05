from asyncio import tasks
import discord 
from  discord.ext import commands, tasks
from apikey import *
import requests
import aiohttp
import re
import json
import time,asyncio


intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = '!', intents=intents)

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


def check_new_video():
    # Make a request to the YouTube API to check for a new video
    response = requests.get(url)
    result = response.json()
    video_id = result['items'][0]['id']['videoId']
    channel_title = result['items'][0]['snippet']['channelTitle']
    description = result['items'][0]['snippet']['description']
    with open("data/YouTubedata.json","w") as f:
        json.dump(result, f)
    try:       
        with open("data/video_id.json", "r") as read_file:
            json_data = json.load(read_file)
        json_value = json_data["video_id"]
        print(f"json_value: {json_value}")
        print(f"Video_id : {video_id}")
        print(f"channel title: {channel_title}")
        print(f"description: {description}")

        if json_value == video_id:
            return None,None,channel_title,description
        
        with open("data/video_id.json", "w") as file:
            json.dump({"video_id": video_id}, file)
        return base_video_url + video_id, video_id, channel_title,description
    except Exception as e:
        print(f"An error occured, type error: {e}")


@tasks.loop(seconds=30.0)  # adjust this as needed
async def check_new_videos():
    channel = client.get_channel(channel_id)  # replace with your channel ID
    message, id_video,channel_title,caption = check_new_video()
    print ("checking....")
    await asyncio.sleep(5)
    print(id_video)
    if message is None:
        return None
    await channel.send(f"@everyone {channel_title} shared a new video:'{caption}'\n {message}")


@client.event
async def on_ready():
    check_new_videos.start()
    print ("The bot is now ready for use")
    print("------------------------------")

client.run(token)

 

