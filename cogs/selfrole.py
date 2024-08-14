import discord
from discord.ext import commands
from apikey import log_channel

roles_info = {
    "Capcut" : 1198715502118322287,
    "After Effect" : 1198716508239573012,
    "VSP" : 1198716806538477629,
    "Alight Motion" : 1198716676418584776
}

class RoleButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        for role_name, role_id in roles_info.items():
            button = discord.ui.Button(
                label = role_name,
                custom_id = f"Role_{role_id}" ,
                style = discord.ButtonStyle.secondary
                )
          
            
            button.callback = self.button_callback  # Assign the callback method to the button
            self.add_item(button)
  

    async def button_callback(self, interaction: discord.Interaction):
        role_id = int(interaction.data['custom_id'].split("_")[1])
        user = interaction.user
        role = user.guild.get_role(role_id)

        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"You have removed the {role.name} role!", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"You have added the {role.name} role!", ephemeral=True)


class Roles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def roles(self, ctx):
        embed = discord.Embed(title='Role selection form', description='Get your desired role! Press to add/remove role!')
        await ctx.send(embed=embed, view=RoleButtons())

async def setup(client):
    await client.add_cog(Roles(client))


# class RoleButtons(discord.ui.View):
#     @discord.ui.button(label='Videostar', custom_id='Role_1', style=discord.ButtonStyle.secondary)
#     async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
#         role_id = 1259205800874999950
#         user = interaction.user
#         role = user.guild.get_role(role_id)
#         if role in user.roles:
#             await user.remove_roles(role)
#             await interaction.response.send_message('You have removed the role!', ephemeral=True)
#         else:
#             await user.add_roles(role)
#             await interaction.response.send_message('You have added the role!', ephemeral=True)

#     @discord.ui.button(label='Aftereffects', custom_id='Role_2', style=discord.ButtonStyle.secondary)
#     async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
#         role_id = 1259205872173842545
#         user = interaction.user
#         role = user.guild.get_role(role_id)
#         if role in user.roles:
#             await user.remove_roles(role)
#             await interaction.response.send_message('You have removed the role!', ephemeral=True)
#         else:
#             await user.add_roles(role)
#             await interaction.response.send_message('You have added the role!', ephemeral=True)

#     @discord.ui.button(label='Capcut', custom_id='Role_3', style=discord.ButtonStyle.secondary)
#     async def button3(self, interaction: discord.Interaction, button: discord.ui.Button):
#         role_id = 1259205868000645201
#         user = interaction.user
#         role = user.guild.get_role(role_id)
#         if role in user.roles:
#             await user.remove_roles(role)
#             await interaction.response.send_message('You have removed the role!', ephemeral=True)
#         else:
#             await user.add_roles(role)
#             await interaction.response.send_message('You have added the role!', ephemeral=True)

#     @discord.ui.button(label='Alight motion', custom_id='Role_4', style=discord.ButtonStyle.secondary)
#     async def button4(self, interaction: discord.Interaction, button: discord.ui.Button):
#         role_id = 1259205864246738996
#         user = interaction.user
#         role = user.guild.get_role(role_id)
#         if role in user.roles:
#             await user.remove_roles(role)
#             await interaction.response.send_message('You have removed the role!', ephemeral=True)
#         else:
#             await user.add_roles(role)
#             await interaction.response.send_message('You have added the role!', ephemeral=True)


