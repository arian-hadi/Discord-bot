import discord
from discord import app_commands
from discord.ext import commands
from apikey import log_channel
from utils import timestamp, get_channel_id
from datetime import timedelta
import datetime
from datetime import datetime
import re
import discord.ui
import sqlite3

class WarningSystem(commands.Cog):
    def __init__(self, client):
        self.client = client
        # Connect to SQLite database (create if it doesn't exist)
        self.conn = sqlite3.connect('warnings.db')
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Create a table to store warnings if it doesn't already exist
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            warn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            reason TEXT,
            warned_by TEXT,
            timestamp TEXT
        )
        """)
        self.conn.commit()
    # Command to show all warnings in the database
    # Command to show all warnings in the database
    @app_commands.command(name="warns", description="Shows all warnings.")
    @commands.has_permissions(manage_messages=True)
    async def warns(self, interaction: discord.Interaction, page: int = 1):
        await interaction.response.defer()
    
    # Fetch all warnings from the database
        self.c.execute("SELECT warn_id, username, reason, warned_by, timestamp FROM warnings")
        warnings = self.c.fetchall()

        if len(warnings) == 0:
         await interaction.followup.send("There are no warnings in the database.", ephemeral=True)
         return

    # Paginate the warnings
        items_per_page = 5
        total_pages = (len(warnings) + items_per_page - 1) // items_per_page  # Calculate total pages
        page = max(1, min(page, total_pages))  # Clamp the page number

        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        warnings_to_display = warnings[start_index:end_index]

    # Create an embed to display the warnings
        embed = discord.Embed(title=f"All Warnings - Page {page}/{total_pages}", color=discord.Color.orange())
        for warn in warnings_to_display:
         warn_id, username, reason, warned_by, timestamp = warn
         embed.add_field(
            name=f"Warn ID: {warn_id} - User: {username}",
            value=f"**Warned by**: {warned_by}\n**Date**: {timestamp}\n**Reason**: {reason}",
            inline=False
        )

    # Add pagination controls
        if total_pages > 1:
         embed.set_footer(text=f"Page {page}/{total_pages} | Use /all_warnings [page number] to navigate.")

        await interaction.followup.send(embed=embed)


    @app_commands.command(name="warn", description="Warns a user.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
     await interaction.response.defer()
    # Check if the reason is provided
     if not reason:
        await interaction.followup.send("Please provide a reason for the warning.", ephemeral=True)
        return

     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

     if member == interaction.user:
        await interaction.followup.send("You cannot warn yourself!", ephemeral=True)
        return

    # Insert the new warning into the database
     with sqlite3.connect('warnings.db') as conn:
         cursor = conn.cursor()

        # Insert the new warning
         cursor.execute("""
            INSERT INTO warnings (user_id, username, reason, warned_by, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (member.id, str(member), reason, str(interaction.user), current_time))
         conn.commit()

        # Get the dynamically generated warn_id (the ID of the last inserted row)
         warning_id = cursor.lastrowid

        # Count the total warnings for this user
         cursor.execute("SELECT COUNT(*) FROM warnings WHERE user_id = ?", (member.id,))
         warning_count = cursor.fetchone()[0]

    # Create the embed message for the warning
     embed = discord.Embed(title="Warning Issued", color=discord.Color.red())
     embed.add_field(name="**⚠️ Warnings**", value=f"{warning_count} Warning(s)", inline=False)
     embed.add_field(name="**⏰ Time**", value=current_time, inline=False)
     embed.add_field(name="Warn ID", value=f"ID: {warning_id} - By {interaction.user.mention}", inline=False)
     embed.add_field(name="Reason", value=reason, inline=False)

    # Send the embed message
     await interaction.followup.send(embed=embed)


    @app_commands.command(name="warnings", description="Shows user's amount of warns")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member, page: int = 1):
        await interaction.response.defer()
        # Fetch all warnings for the user from the database
        self.c.execute("SELECT warn_id, reason, warned_by, timestamp FROM warnings WHERE user_id = ?", (member.id,))
        warnings = self.c.fetchall()

        if len(warnings) == 0:
            await interaction.followup.send(f"{member.mention} has no warnings.", ephemeral=True)
            return

        # Paginate the warnings
        items_per_page = 5
        total_pages = (len(warnings) + items_per_page - 1) // items_per_page  # Calculate total pages
        page = max(1, min(page, total_pages))  # Clamp the page number

        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        warnings_to_display = warnings[start_index:end_index]

        # Create an embed to display the warnings
        embed = discord.Embed(title=f"{member}'s Warnings - Page {page}/{total_pages}", color=discord.Color.orange())
        for warn in warnings_to_display:
            warn_id, reason, warned_by, timestamp = warn
            embed.add_field(
                name=f"Warn ID: {warn_id}",
                value=f"**Warned by**: {warned_by}\n**Date**: {timestamp}\n**Reason**: {reason}",
                inline=False
            )

        # Add pagination controls
        if total_pages > 1:
            embed.set_footer(text=f"Page {page}/{total_pages} | Use /warnings {member.mention} [page number] to navigate.")

        await interaction.followup.send(embed=embed)
    # Command to remove a warning
    @app_commands.command(name="delete_warn", description="Removes a warn from user.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delwarn(self, interaction: discord.Interaction, warn_id: int):
        await interaction.response.defer()
        # Check if the warning exists
        self.c.execute("SELECT * FROM warnings WHERE warn_id = ?", (warn_id,))
        warning = self.c.fetchone()

        if warning:
            self.c.execute("DELETE FROM warnings WHERE warn_id = ?", (warn_id,))
            self.conn.commit()
            await interaction.followup.send(f"Warning with ID {warn_id} has been removed.")
        else:
            await interaction.followup.send(f"No warning found with ID {warn_id}.")

    # Closing connection when bot stops
    def cog_unload(self):
        self.conn.close()


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Kick command
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await interaction.response.defer()
        channel = get_channel_id(self.client, log_channel)
        current_time = timestamp()
        await member.kick(reason=reason)
        embed = discord.Embed(color=discord.Color.red(), title="**Kicked**", description="")
        embed.add_field(name="Moderator/Admin: ", value=f"{interaction.user.mention}", inline=False)
        embed.add_field(name="", value=f"The user **{member}** has been kicked.\nReason = **{reason}**", inline=True)
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.set_footer(text=current_time)
        await channel.send(embed=embed)
        await interaction.followup.send(f"User {member} has been kicked", ephemeral=True)

    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.followup.send("You don't have permission to kick members!", ephemeral=True)
    # Ban command
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await interaction.response.defer()
        channel = get_channel_id(self.client, log_channel)
        current_time = timestamp()
        await member.ban(reason=reason)
        embed = discord.Embed(color=discord.Color.red(), title="**Banned**", description="")
        embed.add_field(name="Admin: ", value=f"{interaction.user.mention}", inline=False)
        embed.add_field(name="Banned user ID: ", value=f"{member.id}", inline=False)
        embed.add_field(name="", value=f"The user **{member}** has been banned.\nReason = **{reason}**", inline=True)
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.set_footer(text=current_time)
        await channel.send(embed=embed)
        await interaction.followup.send(f"User {member} has been banned", ephemeral=True)

    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.followup.send("You don't have permission to ban members!", ephemeral=True)

    # Unban command
    @app_commands.command(name="unban", description="Unban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: int):
        await interaction.response.defer()
        channel = get_channel_id(self.client, log_channel)
        current_time = timestamp()

        try:
            user = await self.client.fetch_user(user_id)
            await interaction.guild.unban(user)
            embed = discord.Embed(
                title="Unbanned",
                description=f"User {user.mention} has been unbanned",
                color=discord.Color.green()
            )
            embed.add_field(name="Admin: ", value=f"{interaction.user.mention}", inline=False)
            embed.set_footer(text=current_time)
            await channel.send(embed=embed)
            await interaction.followup.send(f"User {user.mention} has been unbanned", ephemeral=True)
        except discord.NotFound:
            await interaction.followup.send(f"User with ID {user_id} not found.", ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send(f"Failed to unban user with ID {user_id}.", ephemeral=True)

    # Timeout command
    @app_commands.command(name="timeout", description="Timeout a member for a specified duration")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        await interaction.response.defer()
        channel = get_channel_id(self.client, log_channel)
        current_time = timestamp()

        try:
            # Regular expression to parse the duration
            time_regex = re.match(r"(\d+)([smhd])$", duration)

            if time_regex:
                amount = int(time_regex.group(1))
                unit = time_regex.group(2)

                # Determine the duration of the timeout
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
                    await interaction.followup.send("Invalid time unit. Use 's' for seconds, 'm' for minutes, 'h' for hours, or 'd' for days.", ephemeral=True)
                    return

                embed = discord.Embed(
                    title="Timeout",
                    description=f"User {member.mention} has been timed out",
                    color=discord.Color.yellow()
                )
                embed.add_field(name="Admin", value=interaction.user.mention, inline=False)
                embed.add_field(name="Duration", value=f"{amount} {unit_name}", inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.set_footer(text=current_time)

                # Apply the timeout to the member
                await member.timeout(delta, reason=reason)
                await channel.send(embed=embed)
                await interaction.followup.send(f"{member} has been muted for {amount} {unit_name}.", ephemeral=True)

            else:
                await interaction.followup.send("Invalid duration format. Use 's', 'm', 'h', or 'd' to represent seconds, minutes, hours, or days.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    @commands.command()
    async def rules(self, ctx):
        embed = discord.Embed(
            title="Server Rules",
            
            description=(
                "**1) No spamming.**\n"
                "This includes begging, copy pastas, and text walls.\n\n"
                
                "**2) No inappropriate content.**\n"
                "This includes NSFW material of any kind, excessive profanity, racial slurs, flashing images, "
                "and gifs that crash Discord clients.\n\n"

                "**3) Unjust Harassment.**\n"
                "Examples: Bigotry, racism, transphobia, sexism, hate towards groups, hate speech, etc. "
                "(including slurs or variations of slurs, abusing the spoiler system to joke about these slurs is also not tolerated).\n\n"

                "**4) No advertising.**\n"
                "This includes DM'ing random people in the server with advertisements/invites to other servers.\n\n"

                "**5) No doxxing.**\n"
                "Do not reveal other people's real-life info/photos without permission.\n\n"

                "**6) No spamming messages/bot commands.**\n"
                "This means no spamming messages in channels.\n\n"

                "**7) Do not ping owners.**\n"
                "Pinging admins and mods is allowed, but have a legitimate reason and do not ping all of them. "
                "No pinging owner or Management Team; only ping admins and mods!\n\n"

                "**8) Do not fight, debate, harass, or start drama with other users.**\n"
                "Keep it in DMs.\n\n"

                "**9) Do not bait members into breaking the rules.**\n"
                "Making other people break rules will result in serious consequences.\n\n"

                "**10) When DM’ing mods/admins for help, make your message exactly what you need help with.**\n"
                "Don’t send a message saying 'hi' and expect a response.\n\n"

                "**11) Unbanning or ban appeal will only be heard by Owner or Management Team.**\n"
                "If you are appealing for a ban, a direct conversation with the Owner or Management Team is necessary.\n\n"

                "`**Strike System:**\n"
                "• 1 Warn  -  Nothing\n"
                "• 2 Warnings - 1 Hour Mute\n"
                "• 3 Warnings - 4 Hour Mute\n"
                "• 4 Warnings - 8 Hour Mute\n"
                "• 5 Warnings - 1 Day Mute\n"
                "• 6 Warnings - 30 Days temp ban (logged) -> Perm Ban After`"
            ),
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @timeout.error
    async def timeout_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You don't have permission to timeout members.", ephemeral=True)

# Ensure to add the cog to your bot
async def setup(client):

    await client.add_cog(WarningSystem(client))
    await client.add_cog(Moderation(client))

