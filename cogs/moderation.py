import discord 
from discord.ext import commands
from apikey import channel_id
from utils import timestamp,get_channel_id

class Moderation(commands.Cog):
    def __init__(self,client):
        self.client = client

    #kick command
    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self,ctx, member:discord.Member,*,reason = None):
        channel = get_channel_id(self.client, 1252240278257926207)
        current_time = timestamp()
        await member.kick(reason = reason)
        embed = discord.Embed(color = discord.Color.red(),title = "**kicked**", description= "")
        embed.add_field(name = f"Moderator/Admin: ", value = f"{ctx.author.mention}", inline =False)
        embed.add_field(name =f"", value =f"""The user **{member}** has been kicked.\nReason = **{reason}**""", inline = True)
        embed.set_author(name = str(member), icon_url = member.display_avatar.url)
        embed.set_footer(text= current_time)
        await channel.send(embed = embed)
        await ctx.send(f"user {member} is kicked")

    @kick.error
    async def kick_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have premission to kick members!")

    #ban member
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self,ctx, member:discord.Member,*,reason = None):
        channel = get_channel_id(self.client, 1252240278257926207)
        current_time = timestamp()
        await member.ban(reason = reason)
        embed = discord.Embed(color = discord.Color.red(),title = "**banned**", description= "")
        embed.add_field(name = f"Admin: ", value = f"{ctx.author.mention}", inline =False)
        embed.add_field(name = f"Banned user ID: ", value = f"{member.id}", inline =False)
        embed.add_field(name =f"", value =f"""The user **{member}** has been banned.\nReason = **{reason}**""", inline = True)
        embed.set_author(name = str(member), icon_url = member.display_avatar.url)
        embed.set_footer(text= current_time)
        await channel.send(embed = embed)
        await ctx.send(f"user {member} is banned")    

    @ban.error
    async def ban_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have premission to ban members!")    

    
    #unban command
    @commands.command(name="unban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self,ctx, userId: int):
        channel = get_channel_id(self.client, 1252240278257926207)
        current_time = timestamp() 

        try:
            user = await self.client.fetch_user(userId)
            await ctx.guild.unban(user)
            embed = discord.Embed(
                title="Unbanned",
                description=f"User {user.mention} has been unbanned",
                color=discord.Color.green()
            )
            embed.add_field(name = f"Admin: ", value = f"{ctx.author.mention}", inline =False)
            embed.set_footer(text=current_time)
            await channel.send(embed=embed)
            await ctx.send(f"User {user.mention} has been unbanned")
        except discord.NotFound:
            await ctx.send(f"User with ID {userId} not found.")
        except discord.HTTPException:
            await ctx.send(f"Failed to unban user with ID {userId}.")

async def setup(client):
    await client.add_cog(Moderation(client))