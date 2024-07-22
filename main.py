from asyncio import tasks
import discord 
from  discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from apikey import *
import requests,json,asyncio
import json
import datetime, time
from googleapiclient.discovery import build

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = '!', intents=intents)


def timestamp():
    current_time = datetime.datetime.utcnow().strftime("Date = %Y-%m-%d || Time = %H:%M:%S UTC")
    return current_time

def get_api():
    response = requests.get(url)
    result = response.json()
    return result

def check_new_video():
    # Make a request to the YouTube API to check for a new video
    result = get_api()
    video_id = result['items'][0]['id']['videoId']
    channel_title = result['items'][0]['snippet']['channelTitle']
    title = result['items'][0]['snippet']['title']
    
    
    with open("data/YouTubedata.json","w") as f:
        json.dump(result, f)
    try:       
        with open("data/video_id.json", "r") as read_file:
            json_data = json.load(read_file)
        json_value = json_data["video_id"]
        print(f"json_value: {json_value}")
        print(f"Video_id : {video_id}")
        print(f"channel title: {channel_title}")
        print(f"description: {title}")

        if json_value == video_id:
            return None,None,channel_title,title
        
        with open("data/video_id.json", "w") as file:
            json.dump({"video_id": video_id}, file)
        return base_video_url + video_id, video_id, channel_title,title
    except Exception as e:
        print(f"An error occured, type error: {e}")


youtube = build("youtube", "v3", developerKey=API_KEY)
def get_pfp(youtube_id):
    request = youtube.channels().list(
        part = "snippet",
        id = youtube_id
    )
    response = request.execute()
    channel_pfp = response['items'][0]['snippet']['thumbnails']['default']['url']
    return channel_pfp


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


@tasks.loop(seconds=30.0)  # adjust this as needed
async def check_new_videos():
    channel = client.get_channel(channel_id)  # replace with your YouTube channel ID
    message, id_video,channel_title,caption = check_new_video()
    #hyperlink_format = f'<a href="{message}">{caption}</a>'
    #link_text = hyperlink_format.format
    print ("checking....")
    await asyncio.sleep(5)
    print(id_video)
    if message is None:
        return None
    result = get_api()
    channel_thumbnail = result['items'][0]['snippet']['thumbnails']['default']['url']
    channel_pfp = get_pfp(YOUTUBE_ID)
    embed = discord.Embed(
        title = f"[{caption}({message})]",
        description= f"{channel_title} published a video on YouTube!",
        color = discord.Color.red()
    )
    embed.set_author(name = channel_title, icon_url = channel_pfp)
    embed.set_thumbnail(url = channel_pfp)
    embed.set_image(url = channel_thumbnail)
    await channel.send(f"@everyone {channel_title} shared a new video: ' {caption}'\n <{message}>",)
    await channel.send(embed = embed)
#Loggin edited message
@client.event
async def on_message_edit(before, after):
    current_time = timestamp()
    channel = client.get_channel(log_channel)
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

#Loggin deleted message
@client.event
async def on_message_delete(message):
    channel = client.get_channel(1252240278257926207)
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


#role_update and username update
@client.event
async def on_member_update(before, after):
    current_time = timestamp()
    channel = client.get_channel(1252240278257926207)
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

#kick command
@client.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx, member:discord.Member,*,reason = None):
    channel = client.get_channel(1252240278257926207)
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
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have premission to kick members!")

#ban member
@client.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member:discord.Member,*,reason = None):
    channel = client.get_channel(1252240278257926207)
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
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have premission to ban members!")



@client.command(name="unban")
@commands.guild_only()
@commands.has_permissions(ban_members=True)
async def unban(ctx, userId: int):
    channel = client.get_channel(1252240278257926207)
    current_time = timestamp() 

    try:
        user = await client.fetch_user(userId)
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


                




#timeout member
@client.command()
@commands.has_role("Mod")
async def mute(ctx, member:discord.Member, duration : str = "0", unit: str = None):
    duration = int(duration)
    roleobject = discord.utils.get(ctx.message.guild.roles,id=1263512433885188186)
    await ctx.send(f":white_check_mark: Muted {member} for {duration}{unit}")
    await member.add_roles(roleobject)
    if unit == "s":
        wait = 1 * duration
        time.sleep(wait)
    elif unit == "m":
        wait = 60 * duration
        time.sleep(wait)
    await member.remove_roles(roleobject)
    await ctx.send(f":white_check_mark: {member} was unmuted")



# @client.command()
# @commands.has_permissions(moderate_members = True)
# async def timeout(ctx, member:discord.Member,duration: int ,*,reason = None):
#     await member.timeout(duration = duration, reason = reason)
#     channel = client.get_channel(1252240278257926207)
#     current_time = timestamp()
#     embed = discord.Embed(color = discord.Color.red(),title = "**timed out**", description= "")
#     embed.add_field(name = f"Moderator/Admin: ", value = f"{ctx.author.mention}", inline =False)
#     embed.add_field(name =f"", value =f"""The user **{member}** has been muted.\nReason = **{reason}**""", inline = True)
#     embed.set_author(name = str(member), icon_url = member.display_avatar.url)
#     embed.set_footer(text= current_time)
#     await channel.send(embed = embed)

#     await ctx.send(f"User {member.mention} is timed out for {duration} seconds.")

# @timeout.error
# async def ban_error(ctx, error):
#     if isinstance(error, commands.MissingPermissions):
#         await ctx.send("You don't have premission to ban members!")


@client.event
async def on_ready():
    channel = client.get_channel(channel_id)
    #check_new_videos.start()
    print ("The bot is now ready for use")
    print("------------------------------")
    await channel.send("Teletraan 1 online")

client.run(token)

 

