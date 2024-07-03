from asyncio import tasks
import discord 
from  discord.ext import commands, tasks
from apikey import *
import requests
import aiohttp
import re
import json


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


# @tasks.loop(seconds = 30)
# async def checkforvideos():
#     with open("data/YouTubedata.json","r") as f:
#         data = json.load(f)
#     print ("checking....")

#     # for youtube_channel in data:
#     #     channel = f"https://www.youtube.com/channel/{youtube_channel}"
#     #     html = requests.get(channel+"/videos").text
#     #     try:
#     #         latest_video_url = f"https://www.youtube.com/watch?v=" + re.search('(?<="videoId":").*?(?=")', html).group()
#     #     except Exception as e:
#     #         print("An error occured")
#     async with aiohttp.ClientSession() as session:
#         for youtube_channel in data:
#             try:
#                 url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={YOUTUBE_ID}&part=id&order=date&maxResults=1"
#                 async with session.get(url) as resp:
#                     r = await resp.json()
#                     videoId = r['items'][0]['id']['videoId']
#                     latest_video_url = f"https://www.youtube.com/watch?v={videoId}" 
            
#                 if not str(data[youtube_channel]["latest_video_url"]) == latest_video_url:
#                     data[str(youtube_channel)]['latest_video_url'] = latest_video_url

#                 with open("data/YouTubedata.json","w") as f:
#                     json.dump(data, f) 

#                 discord_channel_id = data[str(youtube_channel)]['notifying_discord_channel']
#                 discord_channel = client.get_channel(int(discord_channel_id))   

#                 msg = f"@everone {data[str(youtube_channel)]['channel_name']} Just Uploaded A Video Or He is Live Go Check It Out: {latest_video_url}"

#                 await discord_channel.send(msg)

#             except Exception as e:
#                 print(f"an error occured: {e}")

def check_new_video():
    # Make a request to the YouTube API to check for a new video
    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    url = base_search_url + 'key={}&channelId={}&part=snippet,id&order=date&maxResults=1'.format(API_KEY, YOUTUBE_ID)
    response = requests.get(url)
    result = response.json()
    with open("data/YouTubedata.json","w") as f:
        json.dump(result, f)
    try: 
        video_id = result['items'][0]['id']['videoId']
        #second_video_id = result['items'][1]['id']['videoId']
        # if video_id == second_video_id:
        #     return None
        return base_video_url + video_id
    except (KeyError, IndexError):
        return None
    
@tasks.loop(seconds=30.0)  # adjust this as needed
async def check_new_videos():
    channel = client.get_channel(channel_id)  # replace with your channel ID
    message = check_new_video()
    await channel.send(f"@everyone 2.0Transformers shared a new video\n {message}")


@client.event
async def on_ready():
    check_new_videos.start()
    print ("The bot is now ready for use")
    print("------------------------------")

client.run(token)

 

