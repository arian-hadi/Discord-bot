import discord
from discord.ext import tasks, commands
from apikey import channel_id, YOUTUBE_ID
from utils import check_new_video, get_pfp, get_api
import asyncio

class Notification(commands.Cog):
    def __init__(self, client):
        self.client = client        
        #self.check_new_videos.start()

    @tasks.loop(seconds = 30.0)
    async def check_new_videos(self):
        channel = self.client.get_channel(channel_id)  # replace with your YouTube channel ID
        message, id_video,channel_title,caption = check_new_video()
        print ("checking....")
        await asyncio.sleep(5)
        print(id_video)
        if message is None:
            return None
        result = get_api()
        channel_thumbnail = result['items'][0]['snippet']['thumbnails']['high']['url']
        channel_pfp = get_pfp(YOUTUBE_ID)
        embed = discord.Embed(
            title = f"{caption}",
            description= f"{channel_title} published a video on YouTube!",
            url = f"{message}",
            color = discord.Color.red()
        )
        embed.set_author(name = channel_title, icon_url = channel_pfp)
        embed.set_thumbnail(url = channel_pfp)
        embed.set_image(url = channel_thumbnail)
        await channel.send(
            content = f"@everyone {channel_title} shared a new video: ' {caption}'\n <{message}>",
            embed = embed         
        )


async def setup(client):
    await client.add_cog(Notification(client))