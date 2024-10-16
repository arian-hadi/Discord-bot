import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import asyncio
import math

class LevelSystem(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.save_interval = 5  
        self.fixed_exp_gain = 50
        self.level_roles = {  # Define roles to assign for specific levels
            5: 1294730090994995210,
            10: 1294730081138245632,
            20: 1294729566291759114,
            30: 1294731048667709552,
            40: 1294731299889741905,
            50: 1294731300351119370,
            60: 1294731650584018974,
            70: 1294733680513777735,
            80: 1294733689653035130
        }
        asyncio.create_task(self.setup_database())  # Set up database asynchronously
  
    # SQLite database setup
    async def setup_database(self):
        async with aiosqlite.connect('level_system.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,   -- Discord user ID
                    level INTEGER,            -- Level
                    experience INTEGER        -- Experience points
                )
            ''')
            await db.commit()

    # Function to retrieve or create a user's data
    async def get_user_data(self, user_id):
        async with aiosqlite.connect('level_system.db') as db:
            async with db.execute('SELECT level, experience FROM users WHERE id = ?', (user_id,)) as cursor:
                result = await cursor.fetchone()

            # If user doesn't exist, create a new entry with default level 1 and 0 experience
            if result is None:
                await db.execute('INSERT INTO users (id, level, experience) VALUES (?, ?, ?)', (user_id, 1, 0))
                await db.commit()
                return 1, 0  # Default level and experience
            else:
                return result[0], result[1]  # Return level and experience

    # Function to update user's level and experience in the database
    async def update_user_data(self, user_id, level, experience):
        async with aiosqlite.connect('level_system.db') as db:
            await db.execute('UPDATE users SET level = ?, experience = ? WHERE id = ?', (level, experience, user_id))
            await db.commit()

    async def assign_role(self, user, level):
        role_id = self.level_roles.get(level)
        if role_id:
            role = discord.utils.get(user.guild.roles, id=role_id)
            if role:
                await user.add_roles(role)

    async def level_up(self, author_id):
        current_level, current_experience = await self.get_user_data(author_id)
    
        level_cap = 80

        # If the user is already at the level cap, don't allow further level-ups
        if current_level >= level_cap:
            return False  # No level-up since they are at the cap

        base_xp = 100
        increment = 200
        required_experience = base_xp + increment * current_level

        if current_experience >= required_experience:
            new_level = current_level + 1
            if new_level > level_cap:
                new_level = level_cap
            new_experience = current_experience - required_experience
            await self.update_user_data(author_id, new_level, new_experience)

            return new_level  # Return the new level instead of True
        return False  # Return False if no level-up occurred


    @commands.Cog.listener()
    async def on_ready(self):
        print('LevelSystem.py is ready.')
        asyncio.create_task(self.save())
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.client.user.id or message.author.bot:
            return

        author_id = message.author.id
        author = message.author
        current_level, current_experience = await self.get_user_data(author_id)

        # Add experience points
        new_experience = current_experience + self.fixed_exp_gain
        await self.update_user_data(author_id, current_level, new_experience)

        # Check if the user leveled up
        new_level = await self.level_up(author_id)
        if new_level:  # Proceed if the user leveled up
            channel_id = 1198713461841072209  # Replace with your desired channel ID
            channel = self.client.get_channel(channel_id)

            if channel is not None:
                # Send a simple text message instead of an embed
                await channel.send(f"{message.author.mention} has leveled up to level {new_level}, Congrats!")
            # Assign the role without showing it in logs
            await self.assign_role(author, new_level)

    @app_commands.command(name="level")
    async def level(self, interaction: discord.Interaction, user: discord.User = None):
        """Check your or another user's level."""
        # Defer the interaction early to avoid the 3-second limit
        await interaction.response.defer()

        if user is None:
            user = interaction.user

        # Fetch level and experience data from the database
        try:
            level, experience = await self.get_user_data(user.id)
        except Exception as e:
            await interaction.followup.send(f"Failed to retrieve level data: {str(e)}")
            return

        # Create an embed with the user's level and experience
        level_card = discord.Embed(title=f"{user.name}'s level and experience", color=discord.Color.random())
        level_card.add_field(name='Level', value=level)
        level_card.add_field(name='Experience', value=experience)
        level_card.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar.url)

        await interaction.followup.send(embed=level_card)

    @app_commands.command(name="leaderboard", description="Show the leaderboard of top users by level.")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Fetch top 7 users from the database
        async with aiosqlite.connect('level_system.db') as db:
            cursor = await db.execute('''
                SELECT id, level, experience FROM users
                ORDER BY level DESC, experience DESC
                LIMIT 7
            ''')
            top_users = await cursor.fetchall()

        if not top_users:
            await interaction.followup.send("No users found in the leaderboard.")
            return

        # Create a visually appealing leaderboard embed
        leaderboard_embed = discord.Embed(
            title="🏆 **Top 7 Users by Level**",
            description="Here are the top users with the highest levels!",
            color=discord.Color.gold()
        )

        rank_emojis = ['🥇', '🥈', '🥉'] + ['#️⃣'] * 7  # Emojis for ranks (1st, 2nd, 3rd, etc.)
        for i, (user_id, level, experience) in enumerate(top_users, start=1):
            user = self.client.get_user(user_id)
            username = user.name if user else f"Unknown User ({user_id})"
            emoji = rank_emojis[i - 1] if i <= 3 else f"**#{i}**"  # Gold, Silver, Bronze for top 3

            leaderboard_embed.add_field(
                name=f"{emoji} {username}",
                value=f"**Level**: {level}\n**Experience**: {experience:,}",
                inline=False
            )

        leaderboard_embed.set_footer(text="Leaderboard updated regularly.")
        
        await interaction.followup.send(embed=leaderboard_embed)

    @commands.Cog.listener()
    async def on_disconnect(self):
        await self.save_data()

    @commands.Cog.listener()
    async def on_error(self, error):
        await self.save_data()

    async def save(self):
        while not self.client.is_closed():
            await asyncio.sleep(self.save_interval)

async def setup(client):
    await client.add_cog(LevelSystem(client))
