import discord 
from discord.ext import commands
from apikey import mod_log_channel,mod_log_channel
from utils import timestamp,get_channel_id
from discord import Member
import datetime
from datetime import timedelta
import re

class Moderation(commands.Cog):
    def __init__(self,client):
        self.client = client

    #kick command
    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self,ctx, member:discord.Member,*,reason = None):
        channel = get_channel_id(self.client, mod_log_channel)
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
        channel = get_channel_id(self.client, mod_log_channel)
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
        channel = get_channel_id(self.client, mod_log_channel)
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


    #timeout command
    @commands.command()
    @commands.has_permissions(moderate_members = True)
    async def timeout(self, ctx, member: discord.Member, duration, *, reason):
        # await member.timeout(datetime.timedelta(seconds=int(time)), reason=reason)
        # await ctx.send(f"{member} is muted for {time} seconds")
        # Regular expression to parse the duration
        channel = get_channel_id(self.client, mod_log_channel)
        current_time =  timestamp()
        try: 
            time_regex = re.match(r"(\d+)([smhd])$", duration)
            
            if time_regex:
                amount = int(time_regex.group(1))
                unit = time_regex.group(2)

                if unit == "s":
                    delta = datetime.timedelta(seconds=amount)
                    unit_name = "seconds"
                elif unit == "m":
                    delta = datetime.timedelta(minutes=amount)
                    unit_name = "minutes"
                elif unit == "h":
                    delta = datetime.timedelta(hours=amount)
                    unit_name = "hours"
                elif unit == "d":
                    delta = datetime.timedelta(days=amount)
                    unit_name = "days"
                else:
                    await ctx.send("Invalid time unit. Use 's' for seconds, 'm' for minutes, 'h' for hours, or 'd' for days.")
                    return

                embed = discord.Embed(
                    title = "Time out",
                    description = f"user {member.mention} has been timed out",
                    color = discord.Color.yellow()
                )       
                embed.add_field(name = "Admin", value = f"{ctx.author.mention}", inline = False)
                embed.add_field(name = "Duration", value = f"{amount} {unit_name}", inline = False) 
                embed.add_field(name = "Reason", value = f"{reason}")
                embed.set_footer(text = current_time)       
                await member.timeout(delta, reason=reason)
                await channel.send(embed = embed)
                await ctx.send(f"{member} is muted for {amount} {unit_name} ({delta}).")

            else:
                await ctx.send('Invalid duration format. (!timeount @user duration reason) Please use s,m,h,d after duration to represent second, minute,etc')
        except Exception as e:
            #  await ctx.send(f"An error occurred: {str(e)}")
            pass

    @timeout.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have premission to timeout members")



async def setup(client):
    await client.add_cog(Moderation(client))