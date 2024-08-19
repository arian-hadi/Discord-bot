import discord
from discord.ext import commands
import os
import asyncio
import sqlite3
import math

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)

class LevelSystem(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.save_interval = 5  
        self.fixed_exp_gain = 25  
        self.setup_database()  

    # SQLite database setup
    def setup_database(self):
        conn = sqlite3.connect('level_system.db')  # Connect to SQLite database
        c = conn.cursor()

        # Create a table with level and experience columns
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,   -- Discord user ID
            level INTEGER,            -- Level
            experience INTEGER        -- Experience points
        )
        ''')

        conn.commit()
        conn.close()

    # Function to retrieve or create a user's data
    def get_user_data(self, user_id):
        conn = sqlite3.connect('level_system.db')
        c = conn.cursor()

        # Fetch user data from the database
        c.execute('SELECT level, experience FROM users WHERE id = ?', (user_id,))
        result = c.fetchone()

        # If user doesn't exist, create a new entry with default level 1 and 0 experience
        if result is None:
            c.execute('INSERT INTO users (id, level, experience) VALUES (?, ?, ?)', (user_id, 1, 0))
            conn.commit()
            conn.close()
            return 1, 0  # Default level and experience
        else:
            conn.close()
            return result[0], result[1]  # Return level and experience

    # Function to update user's level and experience in the database
    def update_user_data(self, user_id, level, experience):
        conn = sqlite3.connect('level_system.db')
        c = conn.cursor()

        # Update the user's level and experience
        c.execute('UPDATE users SET level = ?, experience = ? WHERE id = ?', (level, experience, user_id))

        conn.commit()
        conn.close()

    def level_up(self, author_id):
        current_level, current_experience = self.get_user_data(author_id)
        
        # Uncomment one of the following methods:

        # Linear Increase
        base_xp = 100
        increment = 200
        required_experience = base_xp + increment * current_level

        # Exponential Increase (ignore)
        # base_xp = 1000
        # multiplier = 1.2
        # required_experience = base_xp * (multiplier ** current_level)
        
        if current_experience >= required_experience:
            new_level = current_level + 1
            new_experience = current_experience - required_experience
            self.update_user_data(author_id, new_level, new_experience)
            return True
        else:
            return False

    @commands.Cog.listener()
    async def on_ready(self):
        print('LevelSystem.py is ready.')
        self.client.loop.create_task(self.save())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.client.user.id or message.author.bot:
            return

        author_id = message.author.id
        current_level, current_experience = self.get_user_data(author_id)

        # Use fixed experience points per message
        new_experience = current_experience + self.fixed_exp_gain

        # Update the database with the new experience points
        self.update_user_data(author_id, current_level, new_experience)

        # Check if the user has leveled up
        if self.level_up(author_id):
            level_up_embed = discord.Embed(title='Level up!', color=discord.Color.green())
            level_up_embed.add_field(name='Congratulations', value=f"{message.author.mention} has leveled up to level {current_level + 1}")
            channel_id = 1274718493962539080  # Replace with your desired channel ID
            channel = self.client.get_channel(channel_id)

            if channel is not None:
                await channel.send(embed=level_up_embed)

    @commands.command(aliases=['rank', 'lvl', 'r'])
    async def level(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        level, experience = self.get_user_data(user.id)
        level_card = discord.Embed(title=f"{user.name}'s level and experience", color=discord.Color.random())
        level_card.add_field(name='Level', value=level)
        level_card.add_field(name='Experience', value=experience)
        level_card.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=level_card)

    @commands.Cog.listener()
    async def on_disconnect(self):
        self.save_data()

    @commands.Cog.listener()
    async def on_error(self, error):
        self.save_data()

    async def save(self):
        while not self.client.is_closed():
            # Save data periodically or on disconnect
            await asyncio.sleep(self.save_interval)

async def setup(client):
    await client.add_cog(LevelSystem(client))
