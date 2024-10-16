import discord
from discord.ext import commands
from apikey import channel_id, gif,welcome_id

class Greetings(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Replace 'channel_id' with the actual channel ID
        channel = member.guild.get_channel(welcome_id)  # Get the channel object

        if channel:
            await channel.send(f"{member.mention}")
            
            # Create the embed
            myembed = discord.Embed(
                title="Welcome to the server",
                description="| Check Out Other Channels to get started!! |\n <#1200803540273209374> \n <#1197830060896436265> \n <#1197828306565873760>",
                                                                         
                color=0x5900b3
            )
            myembed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            myembed.set_thumbnail(url=member.display_avatar.url)
            myembed.add_field(name="\u200b", value="❄ ENJOY YOUR STAY IN THE SERVER :DD ❄", inline=False)
            myembed.set_image(url=gif)
            
            # Send the embed
            await channel.send(embed=myembed)
        else:
            print(f"Channel with ID {channel_id} not found")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.get_channel(1271167183048933501)  # Corrected channel assignment
        if channel:
            await channel.send(f"Goodbye {member}!")
        else:
            print(f"Channel with ID 1271167183048933501 not found")

async def setup(client):
    await client.add_cog(Greetings(client))
