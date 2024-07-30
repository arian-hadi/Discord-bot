import discord 
from discord.ext import commands
from apikey import channel_id, gif

class Greetings(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_member_join(self,member):
            channel = self.client.get_channel(channel_id)
            if channel:
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
    

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.client.get_channel(channel_id)
        await channel.send(f"Goodbye {member}!")

async def setup(client):
    await client.add_cog(Greetings(client))
