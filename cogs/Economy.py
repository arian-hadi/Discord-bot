import discord
from discord.ext import commands, tasks
import random
from discord import app_commands
import sqlite3
import json
from datetime import timedelta, datetime
import math
import re

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)

class InventoryView(discord.ui.View):
    def __init__(self, client, ctx, user_data, items_per_page=6):
        super().__init__(timeout=None)  # Keeps the view active indefinitely
        self.client = client
        self.ctx = ctx
        self.user_data = user_data
        self.items_per_page = items_per_page
        self.current_page = 1

        # Ensure inventory is a list of dictionaries
        inventory = user_data.get('inventory', [])
        if isinstance(inventory, str):
            try:
                self.inventory = json.loads(inventory)  # Convert if stored as a JSON string
            except json.JSONDecodeError:
                self.inventory = []  # Reset if parsing fails
        elif isinstance(inventory, list):
            self.inventory = inventory
        else:
            self.inventory = []  # Reset if it's not a list

        # Calculate the total number of pages
        self.total_pages = math.ceil(len(self.inventory) / self.items_per_page)

        # Disable "Previous" button initially if on the first page
        self.previous_button.disabled = True

        # Disable "Next" button initially if only one page exists
        if self.total_pages <= 1:
            self.next_button.disabled = True

    async def update_page(self, interaction: discord.Interaction):
        """Helper method to update the embed with the current page."""
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_embed(self):
     """Creates an embed for the current page of inventory."""
     start = (self.current_page - 1) * self.items_per_page
     end = start + self.items_per_page
     paginated_inventory = self.inventory[start:end]

     embed = discord.Embed(
        title="Your Inventory",
        description=f"Page {self.current_page}/{self.total_pages}",
        color=discord.Color.blue()
    )

     def get_item_details(name):
        for item_list in [self.client.all_shop_items, self.client.dig_items, self.client.fish_list]:
            for item in item_list:
                if item['name'].lower() == name.lower():  # Compare names in a case-insensitive manner
                    return item.get('description', 'No description available'), item.get('image_url')
        return 'No description available', None

     for item in paginated_inventory:
        if isinstance(item, dict):  # Handle dictionary format
            item_name = item.get('name', 'Unknown Item')
            quantity = item.get('quantity', 0)
        else:  # Handle string format
            item_name = item
            quantity = 1  # Default quantity for string items
        description, image_url = get_item_details(item_name)
        field_value = f"{description}\n**Quantity:** {quantity}"
        if image_url:
            embed.add_field(
                name=item_name,
                value=field_value,
                inline=False
            )
        else:
            embed.add_field(
                name=item_name,
                value=field_value,
                inline=False
            )

     return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handles the 'Previous' button click."""
        if self.current_page > 1:
            self.current_page -= 1
            self.next_button.disabled = False  # Re-enable "Next" button if not on the last page
            if self.current_page == 1:
                button.disabled = True  # Disable "Previous" button if on the first page
            await self.update_page(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handles the 'Next' button click."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.previous_button.disabled = False  # Re-enable "Previous" button if not on the first page
            if self.current_page == self.total_pages:
                button.disabled = True  # Disable "Next" button if on the last page
            await self.update_page(interaction)

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.owner_id = 1009902303542775931
        self.user_athenyx_shop = {}

        # Define shop items
        self.all_shop_items = [
            {"name": "Phone", "price": 100, "description": "Used to contact people.", "display_price": "<a:Coins:1289703818136916008>"},
            {"name": "Shovel", "price": 150, "description": "Used to dig up items","display_price": "<a:Coins:1289703818136916008>"},
            {"name": "Fishing rod", "price": 500, "description": "Used to fish.","display_price": "<a:Coins:1289703818136916008>"},
            {"name": "Beer", "price": 400, "description": "One could get drunk from too many.","display_price": "<a:Coins:1289703818136916008>"},
            {"name": "Gun", "price": 700, "description": "A weapon that can be used for self defense","display_price": "<a:Coins:1289703818136916008>"},
            {"name": "Backpack", "price": 550, "description": "Can be used to hold items","display_price": "<a:Coins:1289703818136916008>"},
            {"name": "Notes", "price": 450, "description": "Can be used to expand the amount your Bank can hold","display_price": "<a:Coins:1289703818136916008>"},
            {"name": "Tickets", "price": 350, "description": "Buy and have a chance to win the lottery!", "display_price": "<a:Coins:1289703818136916008>"}
        ]
        self.dig_items = [
            {"name": "Gold Nugget", "price": 200, "description": "A shiny gold nugget.", "rarity": 25,"display_price": "200<a:Coins:1289703818136916008>"},
            {"name": "Silver Coin", "price": 100, "description": "An ancient silver coin.", "rarity": 35,"display_price": "100<a:Coins:1289703818136916008>"},
            {"name": "Old Boot", "price": 20, "description": "An old, worn-out boot.", "rarity": 50,"display_price": "20<a:Coins:1289703818136916008>"},
            {"name": "Treasure Chest", "price": 350, "description": "A rare and valuable treasure chest.", "rarity": 10,"display_price": "350<a:Coins:1289703818136916008>"},
            {"name": "Old Book", "price": 100, "description": "An old book, maybe it contains forgotten knowledge.", "rarity": 45,"display_price": "100<a:Coins:1289703818136916008>"},
            {"name": "Prism shard", "price": 25000, "description": "A forgotten prism, highly valuable.", "rarity": 5,"display_price": "25000<a:Coins:1289703818136916008>"},
        ]
        self.fish_list = [
            {"name": "Goldfish", "price": 100, "description": "A shiny goldfish.", "rarity": 30,"display_price": "100<a:Coins:1289703818136916008>"},
            {"name": "Salmon", "price": 150, "description": "A tasty salmon.", "rarity": 20,"display_price": "150<a:Coins:1289703818136916008>"},
            {"name": "Tuna", "price": 200, "description": "A large tuna.", "rarity": 15,"display_price": "200<a:Coins:1289703818136916008>"},
            {"name": "Trout", "price": 170, "description": "A common trout.", "rarity": 35,"display_price": "170<a:Coins:1289703818136916008>"},
            {"name": "Shark", "price": 250, "description": "A rare and dangerous shark.", "rarity": 5,"display_price": "250<a:Coins:1289703818136916008>"}
        ]
        
        self.jobs = {
    'Discord Mod': {
        'earnings': 5000,   
        'shifts_required_per_day': 0, 
        'time_between_shifts': '40m', 
        'total_shifts_required_to_unlock': 0,
    },
    'Babysitter': {    
        'earnings': 5500,  
        'shifts_required_per_day': 0, 
        'time_between_shifts': '40m', 
        'total_shifts_required_to_unlock': 15  
    },
    'Youtuber': {
        'earnings': 100000,  
        'shifts_required_per_day': 0, 
        'time_between_shifts': '1h', 
        'total_shifts_required_to_unlock': 30  
    },
    'Software Developer': {
        'earnings': 200000,  
        'shifts_required_per_day': 0, 
        'time_between_shifts': '2h', 
        'total_shifts_required_to_unlock': 75  
    }
}
        self.current_shop_items = []
        

        # Initialize the database and ensure schema
        self.init_db()

        # Rotate shop items initially
        self.rotate_shop.start()

        # Dictionary to store the beg command cooldowns
        self.beg_cooldowns = {}

    def init_db(self):
        """Initialize the SQLite database and create tables."""
        conn = sqlite3.connect('economy.db')
        c = conn.cursor()
        # Ensure the schema includes last_daily_claim
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 100,
                inventory TEXT DEFAULT '[]',
                exp INTEGER DEFAULT 0,
                job TEXT DEFAULT NULL,
                bank INTEGER DEFAULT 0,
                has_used_athenyx BOOLEAN DEFAULT 0,
                athenyx_currency INTEGER DEFAULT 0,
                bank_cap INTEGER DEFAULT 15000,
                last_daily_claim TIMESTAMP DEFAULT NULL,
                completed_shifts INTEGER DEFAULT 0  
                
            )
        ''')
        conn.commit()
        conn.close()

    def db_query(self, query, params=()):
        """Execute a query with parameters and return the result."""
        conn = sqlite3.connect('economy.db')
        c = conn.cursor()
        c.execute(query, params)
        result = c.fetchall()
        conn.commit()
        conn.close()
        return result

    def db_execute(self, query, params=()):
        """Execute a query with parameters."""
        conn = sqlite3.connect('economy.db')
        c = conn.cursor()
        print(f"Executing query: {query} with params: {params}")
        c.execute(query, params)
        conn.commit()
        conn.close()
    def get_cooldown_minutes(self, time_string: str) -> int:
     """Convert time_between_shifts (e.g., '40m', '1h') into minutes."""
     if 'h' in time_string:
        return int(time_string.replace('h', '')) * 60
     elif 'm' in time_string:
        return int(time_string.replace('m', ''))
     return 0
    def ensure_user_data(self, user_id):
        """Ensure user data exists in the database."""
        user = self.db_query('SELECT * FROM users WHERE id = ?', (user_id,))
        if not user:
            self.db_execute('''
                INSERT INTO users (id, balance, inventory, exp, job, bank, has_used_athenyx, athenyx_currency, bank_cap, completed_shifts, last_daily_claim)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, 100, '[]', 0, None, 0, 0, 0, 15000, 0, None))
    def add_item_to_inventory(self, user_id, item_name):
     self.ensure_user_data(user_id)
     user_data = self.get_user_data(user_id)

    # Retrieve user inventory
     inventory = user_data.get('inventory', [])

    # Check if item already exists
     inventory_item = next((item for item in inventory if item['name'].lower() == item_name.lower()), None)

     if inventory_item:
        # Increase quantity if item already exists
        inventory_item['quantity'] += 1
     else:
        # Add new item with default quantity of 1
        item = {'name': item_name, 'quantity': 1}
        inventory.append(item)

    # Update user's inventory
     user_data['inventory'] = inventory
     self.set_user_data(user_id, user_data)

    def get_user_data(self, user_id):
     """Retrieve user data from the database."""
     user = self.db_query('SELECT * FROM users WHERE id = ?', (user_id,))
     if user:
        user = user[0]
        last_daily_claim = user[9]
        if last_daily_claim:
            try:
                last_daily_claim = datetime.strptime(last_daily_claim, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                last_daily_claim = None

        return {
            'balance': user[1],
            'inventory': json.loads(user[2]) if user[2] else [],
            'exp': user[3],
            'job': user[4],
            'bank': user[5],
            'has_used_athenyx': bool(user[6]),
            'athenyx_currency': user[7],
            'bank_cap': user[8],
            'last_daily_claim': last_daily_claim,
            'completed_shifts': user[10] if len(user) > 10 else 0
        }

    # Return default values if user not found
     return {
        'balance': 100,
        'inventory': [],
        'exp': 0,
        'job': None,
        'bank': 0,
        'has_used_athenyx': False,
        'athenyx_currency': 0,
        'bank_cap': 15000,
        'last_daily_claim': None,
        'completed_shifts': 0
    }
    def set_user_data(self, user_id, data):
        """Update user data in the database."""
        self.db_execute('''
            UPDATE users
            SET balance = ?,
                inventory = ?,
                exp = ?,
                job = ?,
                bank = ?,
                has_used_athenyx = ?,
                athenyx_currency = ?,
                bank_cap = ?,
                last_daily_claim = ?,
                completed_shifts = ?  -- Add completed_shifts here       
            WHERE id = ?
        ''', ((
        data['balance'],
        json.dumps(data['inventory']),
        data['exp'],
        data['job'],
        data['bank'],
        data['has_used_athenyx'],
        data['athenyx_currency'],
        data['bank_cap'],
        data['last_daily_claim'],
        data.get('completed_shifts', 0),  # Add this line
        user_id
    )))

    @tasks.loop(minutes=30)  # Refresh shop items every 30 mins
    async def rotate_shop(self):
        """Rotates the shop items every 30 minutes."""
        self.current_shop_items = random.sample(self.all_shop_items, 4)
        print("Shop items have been rotated.")
    @app_commands.command(name="sell", description="Sells any item in inventory")
    async def sell(self, interaction: discord.Interaction, item_name: str, quantity: int):
     """Sell a specified quantity of an item from your inventory."""
     item_name = item_name.lower().strip()  # Normalize item name
     await interaction.response.defer()
    # Ensure user data is initialized
     self.ensure_user_data(interaction.user.id)
     user_data = self.get_user_data(interaction.user.id)
    
    # Retrieve user inventory
     inventory = user_data.get('inventory', [])

    # Find the item in the user's inventory
     inventory_item = next((item for item in inventory if item['name'].lower() == item_name), None)

     if not inventory_item:
        await interaction.response.send_message(f"You do not have an item named '{item_name}' in your inventory.")
        return

     if quantity <= 0:
        await interaction.response.send_message("Quantity must be greater than zero.")
        return

     if quantity > inventory_item['quantity']:
        await interaction.response.send_message(f"You do not have enough of '{item_name}' to sell. You have {inventory_item['quantity']} available.")
        return

    # Find the item in all item lists to get its price
     item_price = 0
     for item_list in [self.all_shop_items, self.dig_items, self.fish_list]:
        item = next((i for i in item_list if i['name'].lower() == item_name), None)
        if item:
            item_price = item['price']  # This will be an integer
            break

     if item_price == 0:
        await interaction.response.send_message(f"Item '{item_name}' is not a valid item to sell.")
        return

    # Calculate total sale amount
     total_sale_amount = item_price * quantity

    # Update the user's balance
     print(f"Current balance before sale: {user_data['balance']}")
     user_data['balance'] += total_sale_amount
     print(f"New balance after sale: {user_data['balance']}")

    # Update inventory
     inventory_item['quantity'] -= quantity
     if inventory_item['quantity'] <= 0:
        inventory.remove(inventory_item)

    # Save updated inventory
     self.set_user_data(interaction.user.id, user_data)

    # Create an embed to confirm the sale
     display_price = f"{total_sale_amount} <a:Coins:1289703818136916008>"
     sale_embed = discord.Embed(
        title="Sale Confirmation",
        description=f"You have successfully sold {quantity} {item_name}(s).",
        color=discord.Color.green()
    )
     sale_embed.add_field(name="Total Sale Amount", value=display_price, inline=False)
     sale_embed.add_field(name="Remaining Inventory", value=f"{inventory_item['quantity']} {item_name}(s) left", inline=False)

     await interaction.followup.send(embed=sale_embed)


    @app_commands.command(name='daily', description = "Gives daily cash")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        self.ensure_user_data(user_id)
        # Get the user's data
        user_data = self.get_user_data(user_id)

        # Get the current time and last claim time
        current_time = datetime.now()
        last_claim_time = user_data['last_daily_claim']

        # Check if the user has claimed daily rewards before
        if last_claim_time:
            # Calculate the time difference in hours
            time_since_last_claim = (current_time - last_claim_time).total_seconds() / 3600

            if time_since_last_claim < 24:
                remaining_time = 24 - time_since_last_claim
                await interaction.response.send_message(f"You can claim your daily reward in {math.ceil(remaining_time)} hours.")
                return
        
        # Reward the user
        daily_reward = 100  # Example daily reward amount
        new_balance = user_data['balance'] + daily_reward

        # Update the user's balance in the database
        self.db_execute('UPDATE users SET balance = ?, last_daily_claim = ? WHERE id = ?', 
                        (new_balance, current_time, user_id))
        
        await interaction.followup.send(f"You have claimed your daily reward of {daily_reward}<a:Coins:1289703818136916008>! Your new balance is {new_balance}<a:Coins:1289703818136916008>.")


    @app_commands.command(name="balance", description="Check the balance of a user.")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user  # Use interaction.user instead of ctx.author
        await interaction.response.defer()
        # Ensure user data and get user data
        self.ensure_user_data(member.id)
        user_data = self.get_user_data(member.id)
        
        eco_embed = discord.Embed(title=f"{member.name}'s Current Balance", description='Current balance of this user.', color=discord.Color.green())
        eco_embed.add_field(name='Current Balance', value=f"{user_data['balance']}<a:Coins:1289703818136916008>")
        eco_embed.set_footer(text='Want to increase your balance? Try running some economy-based commands!', icon_url=None)
        
        await interaction.followup.send(embed=eco_embed)

    @app_commands.command(name='beg', description='Beg for some coins with a 10-minute cooldown and a 50% chance of success.')
    async def beg(self, interaction: discord.Interaction): 
        """Beg for some coins with a 10-minute cooldown and a 50% chance of success."""
        user_id = interaction.user.id
        current_time = datetime.now()

        # Check if the user is on cooldown
        if user_id in self.beg_cooldowns:
            last_beg_time = self.beg_cooldowns[user_id]
            if current_time - last_beg_time < timedelta(minutes=10):
                remaining_time = (timedelta(minutes=10) - (current_time - last_beg_time)).total_seconds()
                minutes, seconds = divmod(remaining_time, 60)
                embed = discord.Embed(
                    title="Beg Command Cooldown",
                    description=f"You need to wait {int(minutes)}m {int(seconds)}s before you can beg again.",
                    color=discord.Color.red()
                )
                embed.set_footer(text="Patience is a virtue!")
                await interaction.response.send_message(embed=embed)
                return
        await interaction.response.defer()
        # Determine if the user receives coins
        if random.random() < 0.5:  # 50% chance
            coins_earned = random.randint(250, 2500)
            self.ensure_user_data(user_id)
            user_data = self.get_user_data(user_id)
            user_data['balance'] += coins_earned
            self.set_user_data(user_id, user_data)

            # Update cooldown
            self.beg_cooldowns[user_id] = current_time

            embed = discord.Embed(
                title="Successful Begging!",
                description=f"{interaction.user.mention} has begged and received {coins_earned}<a:Coins:1289703818136916008>.",
                color=discord.Color.green()
            )
            embed.set_footer(text="Keep trying for more!")
        else:
            embed = discord.Embed(
                title="No Luck This Time",
                description=f"{interaction.user.mention} begged but didn't receive any coins. Better luck next time!",
                color=discord.Color.red()
            )
            embed.set_footer(text="Sometimes luck just isn't on your side.")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name='shop', description='View items available for purchase.')
    async def shop(self, interaction: discord.Interaction):
        self.ensure_user_data(interaction.user.id)
        user_data = self.get_user_data(interaction.user.id)
        await interaction.response.defer()
        if user_data.get('has_used_athenyx'):
            shop_items = self.athenyx_shop
            currency_name = self.new_currency_name
            currency_symbol = self.new_currency_symbol
        else:
            if not self.current_shop_items:
                self.rotate_shop()  # Ensure shop items are loaded
            shop_items = self.current_shop_items
            currency_name = "Coins"
            currency_symbol = "$"
            
        shop_embed = discord.Embed(
            title="Item Shop",
            description=f"Here are the items available for purchase ({currency_name}):",
            color=discord.Color.blue()
        )

        for item in shop_items:
            shop_embed.add_field(
                name=item['name'],
                value=f"**Price:** {currency_symbol}{item['price']}{item['display_price']}\n**Description:** {item['description']}",
                inline=False
            )
        shop_embed.set_footer(text='Shop rotates every 30 mins!')

        await interaction.followup.send(embed=shop_embed)

    @app_commands.command(name='inventory', description='Displays your inventory.')
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        """Command to display the user's inventory with pagination and descriptions."""
        user_id = interaction.user.id
        self.ensure_user_data(user_id)

        # Fetch the user's inventory from the database
        user_data = self.db_query('SELECT * FROM users WHERE id = ?', (user_id,))
        if not user_data:
            await interaction.followup.send("User data not found.")
            return

        user_data = user_data[0]  # Unpack the first (and only) result row

        # Assuming the inventory is stored in the third column (adjust the index if needed)
        inventory = user_data[2]  # Assuming the third column is the 'inventory' field

        # If inventory is stored as a string (JSON format), load it
        if isinstance(inventory, str):
            try:
                inventory = json.loads(inventory)  # Convert from JSON string
            except json.JSONDecodeError:
                inventory = []  # Reset if parsing fails

        # Ensure inventory items have a quantity field
        for item in inventory:
            if isinstance(item, dict):
                if 'quantity' not in item:
                    item['quantity'] = 1  # Default to 1 if 'quantity' is missing
            else:
                # If the item is a string, convert it to a dict with a default quantity
                inventory.remove(item)
                inventory.append({'name': item, 'quantity': 1})

        # Create the initial inventory embed and start the View
        view = InventoryView(self, interaction, {"inventory": inventory})  # Pass the inventory as a dictionary
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name='buy', description='Buy an item from the shop.')
    async def buy(self, interaction: discord.Interaction, item_name: str):
     
        await interaction.response.defer()
        item_name = item_name.lower().strip()  # Normalize item name

    # Ensure the shop is not empty and item name is provided
        if not item_name:
           await interaction.followup.send("Please specify an item to buy.")
           return

    # Retrieve user data
        self.ensure_user_data(interaction.user.id)
        user_data = self.get_user_data(interaction.user.id)

    # Ensure inventory is a list
        inventory = user_data.get('inventory', [])
        if isinstance(inventory, str):
           try:
            inventory = json.loads(inventory)  # Attempt to parse if it's a string
           except json.JSONDecodeError:
            inventory = []  # Reset if parsing fails
        elif not isinstance(inventory, list):
           inventory = []  # Reset if it's not a list

    # Find the item in the current shop
        item = next((i for i in self.current_shop_items if i['name'].lower() == item_name), None)

        if not item:
         await interaction.followup.send(f"Item '{item_name}' not found in the shop.")
         return

    # Get the item price and extract the numeric part (assuming the price may contain an emoji)
        item_price_str = item['price']
        item_price = int(re.search(r'\d+', str(item_price_str)).group())  # Extract the number from the string

    # Check if the user has enough balance
        if user_data['balance'] < item_price:
         await interaction.followup.send("You do not have enough balance to buy this item.")
         return

    # Deduct the item price from the user's balance
        user_data['balance'] -= item_price

    # Check if the item is already in the user's inventory
        inventory_item = next((inv_item for inv_item in inventory if inv_item['name'].lower() == item_name), None)

        if inventory_item:
        # Increment item quantity if it already exists
         inventory_item['quantity'] += 1
        else:
        # Add new item to inventory with quantity of 1
         inventory.append({'name': item_name, 'quantity': 1})

    # Update the user's data
        user_data['inventory'] = inventory
        self.set_user_data(interaction.user.id, user_data)
 
    # Confirm purchase to the user
        await interaction.followup.send(f"You have successfully bought **{item_name}** for {item_price} <a:Coins:1289703818136916008>.")

    
    @app_commands.command(name='work', description='Work at your job and earn money and shifts.')
    async def work(self, interaction: discord.Interaction):
     """Work at your job and earn money and shifts."""
     await interaction.response.defer()

     self.ensure_user_data(interaction.user.id)
     user_data = self.get_user_data(interaction.user.id)

     job = user_data['job']
     if not job:
        await interaction.followup.send("You do not have a job. Use the /job command to select one.")
        return

     if job not in self.jobs:
        await interaction.followup.send("Invalid job.")
        return

    # Calculate earnings and shifts
     job_info = self.jobs[job]
     earnings = job_info['earnings']
     completed_shifts = user_data.get('completed_shifts', 0) + 1  # Increment the completed shifts
     user_data['completed_shifts'] = completed_shifts  # Update user data

    # Update user balance
     user_data['balance'] += earnings
     self.set_user_data(interaction.user.id, user_data)

    # Create an embed message
     embed = discord.Embed(
        title="Work Results",
        description=f"You worked hard at your job as **{job}**!",
        color=discord.Color.green()
    )
     embed.add_field(name="Earnings", value=f"<a:Coins:1289703818136916008> {earnings:,}", inline=True)
     embed.add_field(name="Total Shifts Completed", value=f"{completed_shifts}", inline=True)
     embed.set_footer(text="Keep up the great work!")

     await interaction.followup.send(embed=embed)

    @app_commands.command(name='dig', description='Dig for items with a Shovel.')
    async def dig(self, interaction: discord.Interaction):
     await interaction.response.defer()
    # Debugging: Print the dig_items to ensure they are initialized
     print(f"Dig Items: {self.dig_items}")

    # Ensure the user data is present in the database
     self.ensure_user_data(interaction.user.id)

    # Fetch user data from the SQLite database
     user_data = self.get_user_data(interaction.user.id)

    # Check if the user has a Shovel in their inventory
     shovel_in_inventory = any(item['name'].lower() == 'shovel' for item in user_data['inventory'])
     if not shovel_in_inventory:
        await interaction.response.send_message("You need a Shovel to use this command. Purchase one from the shop using /buy Shovel.")
        return

    # Select a random item from the dig_items based on their rarity
     dig_item = random.choices(self.dig_items, weights=[item['rarity'] for item in self.dig_items])[0]
    
    # Check if the item already exists in the inventory
     item_in_inventory = next((item for item in user_data['inventory'] if item['name'] == dig_item['name']), None)
    
     if item_in_inventory:
        # Increment the quantity if the item already exists
        item_in_inventory['quantity'] += 1
     else:
        # Add the item to the inventory with quantity 1
        user_data['inventory'].append({'name': dig_item['name'], 'quantity': 1})

    # Check for Stone Of Athenyx usage
     if dig_item['name'] == 'Stone Of Athenyx':
        user_data['has_used_athenyx'] = True

        # Send embed for Stone Of Athenyx
        eco_embed = discord.Embed(
            title="Congratulations!",
            description="You have used the Stone Of Athenyx and unlocked a new dimension of shop and currency.",
            color=discord.Color.green()
        )
        eco_embed.add_field(name='Item Description', value=dig_item['description'], inline=False)
        eco_embed.set_footer(text='Explore the new shop with /shop!', icon_url=None)
        await interaction.followup.send(embed=eco_embed)
     else:
        # Send embed for other items found
        eco_embed = discord.Embed(
            title="Congratulations!",
            description=f"You found a {dig_item['name']}.",
            color=discord.Color.green()
        )
        eco_embed.add_field(name='Item Description', value=dig_item['description'], inline=False)
        eco_embed.add_field(name='Value', value=f"${dig_item['price']}.", inline=False)
        eco_embed.set_footer(text='You can sell items for cash or use them as you see fit!', icon_url=None)
        await interaction.followup.send(embed=eco_embed)

    # Update the user data in the SQLite database
     self.set_user_data(interaction.user.id, user_data)

    @app_commands.command(name='quit', description="Quit your current job.")
    async def quit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        """Quit the user's current job."""
        user_id = interaction.user.id
        self.ensure_user_data(user_id)
        user_data = self.get_user_data(user_id)

        if not user_data['job']:
            await interaction.followup.send("You are not currently employed in any job.")
            return

        user_data['job'] = None
        self.set_user_data(user_id, user_data)
        await interaction.followup.send("You have successfully quit your current job.")

    @app_commands.command(name='fish', description='Catch a fish from the pond.')
    async def fish(self, interaction: discord.Interaction):
     await interaction.response.defer()
     """Catch a fish from the pond."""
     self.ensure_user_data(interaction.user.id)
     user_data = self.get_user_data(interaction.user.id)

     fishing_rod_in_inventory = any(item['name'].lower() == 'fishing rod' for item in user_data['inventory'])
     if not fishing_rod_in_inventory:
        await interaction.followup.send("You need a Fishing Rod to use this command. Purchase one from the shop using /buy Fishing Rod.")
        return

     fish = random.choices(self.fish_list, weights=[fish['rarity'] for fish in self.fish_list])[0]
     fish_item = {
        'name': fish['name'],
        'quantity': 1
    }

    # Check if the fish is already in the user's inventory
     inventory_item = next((item for item in user_data['inventory'] if item['name'] == fish['name']), None)

     if inventory_item:
        inventory_item['quantity'] += 1
     else:
        user_data['inventory'].append(fish_item)

    # Update the user data in the database
     self.set_user_data(interaction.user.id, user_data)

    # Send a confirmation message
     embed = discord.Embed(
        title="Fishing Results",
        description=f"You caught a **{fish['name']}**.",
        color=0x00ff00
    )
     embed.add_field(name="Description", value=fish['description'], inline=False)
     embed.add_field(name="Value", value=f"${fish['price']}", inline=False)

     await interaction.followup.send(embed=embed)

    @app_commands.command(name='steal', description="Steal money from another user.")
    async def steal(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
        if interaction.user.id == member.id:
            await interaction.response.send_message("You can't steal from yourself!")
            return

        self.ensure_user_data(interaction.user.id)
        self.ensure_user_data(member.id)

        thief_data = self.get_user_data(interaction.user.id)
        victim_data = self.get_user_data(member.id)

        if random.random() < 0.5:  # 50% chance to steal successfully
            amount = random.randint(1, victim_data['balance'])
            victim_data['balance'] -= amount
            thief_data['balance'] += amount
            self.set_user_data(member.id, victim_data)
            self.set_user_data(interaction.user.id, thief_data)
            await interaction.followup.send(f"Successfully stole ${amount}<a:Coins:1289703818136916008> from {member.name}!")
        else:
            await interaction.followup.send("Stealing failed! Better luck next time.")

    @app_commands.command(name='give', description="Give money to another user.")
    async def give(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await interaction.response.defer()
        self.ensure_user_data(interaction.user.id)
        self.ensure_user_data(member.id)

        user_data = self.get_user_data(interaction.user.id)
        recipient_data = self.get_user_data(member.id)

        if user_data['balance'] < amount:
            await interaction.response.send_message("You do not have enough balance to give this amount.")
            return

        user_data['balance'] -= amount
        recipient_data['balance'] += amount
        self.set_user_data(interaction.user.id, user_data)
        self.set_user_data(member.id, recipient_data)
        await interaction.followup.send(f"You have successfully given ${amount}<a:Coins:1289703818136916008> to {member.name}!")

    @commands.command()
    async def selfgive(self, ctx, amount: int):
        if ctx.author.id != self.owner_id:
            await ctx.send("You do not have permission to use this command.")
            return
        
        self.ensure_user_data(ctx.author.id)
        user_data = self.get_user_data(ctx.author.id)
        user_data['balance'] = amount
        self.set_user_data(ctx.author.id, user_data)
        
        await ctx.send(f"Your balance has been set to ${amount}<a:Coins:1289703818136916008>.")

    @app_commands.command(name='job', description="Choose a job for yourself.")
    async def job(self, interaction: discord.Interaction, job_name: str):
     await interaction.response.defer()
     self.ensure_user_data(interaction.user.id)
     user_data = self.get_user_data(interaction.user.id)

    # Check if the job exists
     if job_name not in self.jobs:
        await interaction.followup.send("This job is not available. Please choose a valid job.")
        return

    # Check if the user has completed the required number of shifts
     job_info = self.jobs[job_name]
     completed_shifts = user_data['completed_shifts']  # Use total completed shifts
     required_shifts = job_info['total_shifts_required_to_unlock']

     if completed_shifts < required_shifts:
        await interaction.followup.send(
            f"You need to complete {required_shifts} shifts to unlock this job. "
            f"You have completed {completed_shifts} shifts so far."
        )
        return

    # Assign the job to the user
     user_data['job'] = job_name
     self.set_user_data(interaction.user.id, user_data)

     await interaction.followup.send(f"You have chosen the job: **{job_name}**.")
 
    @app_commands.command(name='jobs', description="List all available jobs.")
    async def jobs(self, interaction: discord.Interaction):
     await interaction.response.defer()
     self.ensure_user_data(interaction.user.id)
     user_data = self.get_user_data(interaction.user.id)

     job_list = ''
    
     for job, job_info in self.jobs.items():
        shifts_required = job_info['total_shifts_required_to_unlock']
        earnings = job_info['earnings']
        time_between_shifts = job_info['time_between_shifts']

        # Correctly get the completed shifts for the user
        completed_shifts = user_data['completed_shifts']  # Use total completed shifts
        status_icon = "✅" if completed_shifts >= shifts_required else "❌"

        job_list += (
            f"{status_icon} **{job}**\n"
            f"Shifts Required Per Day: {job_info['shifts_required_per_day']}\n"
            f"Time Between Shifts: {time_between_shifts}\n"
            f"Total Shifts Required To Unlock: {shifts_required}\n"
            f"Salary: <a:Coins:1289703818136916008> {earnings:,} per shift\n\n"
        )

     embed = discord.Embed(
        title="Available Jobs",
        description="Jobs with ❌ next to them are locked.",
        color=discord.Color.blue()
    )
     embed.add_field(name="Jobs", value=job_list, inline=False)
     embed.set_footer(text='Type /job <job_name> to choose a job.')

     await interaction.followup.send(embed=embed)
    @app_commands.command(name='bank', description="Check your bank balance and capacity.")
    async def bank(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_data = self.get_user_data(interaction.user.id)
        default_bank_cap = 15000
        current_bank_cap = user_data.get('bank_cap', default_bank_cap)
        increase_in_capacity = current_bank_cap - default_bank_cap

        embed = discord.Embed(title=f"{interaction.user.name}'s Bank", color=discord.Color.blue())
        embed.add_field(name="Bank Balance", value=user_data['bank'])
        embed.add_field(name="Bank Capacity", value=current_bank_cap)

        if increase_in_capacity > 0:
            embed.add_field(name="Increased Capacity", value=f"+{increase_in_capacity}", inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name='deposit', description="Deposit money into your bank.")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer()
        self.ensure_user_data(interaction.user.id)
        user_data = self.get_user_data(interaction.user.id)

        if amount <= 0:
            await interaction.followup.send("You need to deposit a positive amount of money.")
            return

        if user_data['balance'] < amount:
            await interaction.followup.send("You don't have enough money to deposit that amount.")
            return

        potential_new_balance = user_data['bank'] + amount
        if potential_new_balance > user_data['bank_cap']:
            allowed_deposit = user_data['bank_cap'] - user_data['bank']
            if allowed_deposit > 0:
                user_data['balance'] -= allowed_deposit
                user_data['bank'] += allowed_deposit
                await interaction.followup.send(f"Bank cap reached! Only {allowed_deposit} was deposited.")
            else:
                await interaction.followup.send("Your bank is already full. You can't deposit more money.")
        else:
            user_data['balance'] -= amount
            user_data['bank'] += amount
            await interaction.followup.send(f"{amount}<a:Coins:1289703818136916008> has been deposited into your bank.")

        self.set_user_data(interaction.user.id, user_data)

    @app_commands.command(name='withdraw', description="Withdraw money from your bank.")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer()
        self.ensure_user_data(interaction.user.id)
        user_data = self.get_user_data(interaction.user.id)

        if user_data['bank'] < amount:
            await interaction.followup.send("You do not have enough balance in the bank to withdraw this amount.")
            return

        user_data['bank'] -= amount
        user_data['balance'] += amount
        self.set_user_data(interaction.user.id, user_data)

        await interaction.followup.send(f"You have successfully withdrawn ${amount}<a:Coins:1289703818136916008> from your bank.")

    @app_commands.command(name='eco', description="Show information about the economy system.")
    async def eco(self, interaction: discord.Interaction):
        await interaction.response.defer()
        eco_info_embed = discord.Embed(
            title="Economy System Information",
            description="Everything you need to know about the economy system!",
            color=discord.Color.gold()
        )

        eco_info_embed.add_field(
            name="How to Earn Money",
            value=(
                "• **/work** - Work to earn a random amount of money.\n"
                "• **/beg** - Beg to get a small amount of money (or lose some if you're unlucky).\n"
                "• **/dig** - Dig to find random items that you can sell for money.\n"
                "• **/steal @member** - Attempt to steal money from another member (50% chance of success)."
            ),
            inline=False
        )

        eco_info_embed.add_field(
            name="How to Spend Money",
            value=(
                "• **/shop** - View available items in the shop.\n"
                "• **/buy <item_name>** - Buy an item from the shop using your balance.\n"
            ),
            inline=False
        )

        eco_info_embed.add_field(
            name="Account Management",
            value=(
                "• **/balance [@member]** - Check your current balance or the balance of another member.\n"
                "• **/inventory** - View the items you currently have in your inventory.\n"
                "• **/give @member <amount>** - Give money to another member.\n"
                "• **/bank** - Shows money in bank\n"
                "• **/deposit <amount>** - Deposit money into bank\n"
                "• **/withdraw <amount>** - Withdraw money from bank"
            ),
            inline=False
        )

        eco_info_embed.set_footer(
            text="Enjoy building your wealth!",
            icon_url=None
        )
        await interaction.followup.send(embed=eco_info_embed)

async def setup(client):
    print("Loading Economy cog...")
    await client.add_cog(Economy(client))
    print("Economy cog loaded.")
