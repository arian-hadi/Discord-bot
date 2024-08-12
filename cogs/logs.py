import discord 
from discord.ext import commands
from apikey import channel_id, log_channel
from utils import timestamp,get_channel_id


#Loggin deleted message
class Logs(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = get_channel_id(self.client, log_channel)
        current_time = timestamp()
        embed = discord.Embed(
            title = f"Message was deleted in {message.channel.mention}",
            description = f"Deleted message = {message.content}",
            color = discord.Color.red()
        )
        embed.set_author(name = str(message.author), icon_url = message.author.display_avatar.url)
        embed.add_field(name = "User_id", value = message.author.mention, inline = False)
        embed.set_footer(text= current_time)
        await channel.send(embed=embed)


    #Loggin edited message
    @commands.Cog.listener()
    async def on_message_edit(self,before, after):
        if before.author == self.client.user or before.content == after.content:
            return
        current_time = timestamp()
        channel = get_channel_id(self.client, log_channel)
        embed = discord.Embed(
            title = f"{before.author} edited a message in {before.channel.mention}",
            description="",
            color = 0x1abc9c
        )
        embed.set_author(name = str(before.author), icon_url = before.author.display_avatar.url)
        embed.add_field(name="Before" ,value=before.content, inline=False)
        embed.add_field(name= "After" ,value=after.content, inline=False)
        embed.add_field(name = "User_id", value = before.author.mention, inline = False)
        embed.set_footer(text= current_time)

        await channel.send(embed = embed)

    #role_update and username update
    @commands.Cog.listener()
    async def on_member_update(self,before, after):
        if before.author == self.client.user:         
         return
        current_time = timestamp()
        channel = get_channel_id(self.client,log_channel)
        if len(before.roles) > len(after.roles):
            role = next(role for role in before.roles if role not in after.roles)
            embed = discord.Embed(
                title = "A member role was removed!",
                description=f"{role.name} was removed from {before.mention}",
                color=discord.Color.from_rgb(255, 255, 0)
            )
            embed.set_footer(text= current_time)
        elif len(after.roles) > len(before.roles):
            role = next(role for role in after.roles if role not in before.roles)
            embed = discord.Embed(
                title = "A member got a new role!",
                description=f"{role.name} role was added to  {after.mention}",
                color=discord.Color.from_rgb(0, 255, 0)
            )
            embed.set_footer(text= current_time)
        elif before.nick != after.nick:
            before_nick = before.nick if before.nick else before.display_name
            after_nick = after.nick if after.nick else after.display_name
            embed = discord.Embed(
                title = "User nickname changed",
                description=f"{before_nick} changed to {after_nick}",
                color=discord.Color.from_rgb(0, 128, 255)
            )
            embed.set_footer(text= current_time)
        else:
            return
        embed.set_author(name = after.name, icon_url = after.display_avatar.url)
        await channel.send(embed = embed)


async def setup(client):
    await client.add_cog(Logs(client))
