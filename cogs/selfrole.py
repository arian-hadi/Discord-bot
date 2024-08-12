
import discord
from discord.ext import commands
from apikey import log_channel

intents = discord.Intents.all()

client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

class RoleButtons(discord.ui.View):
    @discord.ui.button(label='Videostar', custom_id='Role_1', style=discord.ButtonStyle.secondary)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1259205800874999950
        user = interaction.user
        role = user.guild.get_role(role_id)
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message('You have removed the role!', ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message('You have added the role!', ephemeral=True)

    @discord.ui.button(label='Aftereffects', custom_id='Role_2', style=discord.ButtonStyle.secondary)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1259205872173842545
        user = interaction.user
        role = user.guild.get_role(role_id)
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message('You have removed the role!', ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message('You have added the role!', ephemeral=True)

    @discord.ui.button(label='Capcut', custom_id='Role_3', style=discord.ButtonStyle.secondary)
    async def button3(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1259205868000645201
        user = interaction.user
        role = user.guild.get_role(role_id)
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message('You have removed the role!', ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message('You have added the role!', ephemeral=True)

    @discord.ui.button(label='Alight motion', custom_id='Role_4', style=discord.ButtonStyle.secondary)
    async def button4(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1259205864246738996
        user = interaction.user
        role = user.guild.get_role(role_id)
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message('You have removed the role!', ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message('You have added the role!', ephemeral=True)

class Roles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def roles(self, ctx):
        embed = discord.Embed(title='Role selection form', description='Get your desired role! Press to add/remove role!')
        await ctx.send(embed=embed, view=RoleButtons())

async def setup(client):
    await client.add_cog(Roles(client))

