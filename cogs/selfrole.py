import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

roles_info = {
    "🎨 Artist":  1198717378083700877,
    "👨‍💻 Programmer": 1198921926219923498,
    "🖋️ Writer": 1198921997078495353,
    "🎮 Gamer": 1198921592688877668,
    "📓 After Effect": 1198716508239573012,
    "📘 VSP": 1198716806538477629,
    "🎥 Capcut": 1198715502118322287,
    "📷 Alight Motion": 1198716676418584776
}

class RoleReact(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def roles(self, ctx):
        # Embed for skills
        embed = discord.Embed()
        embed.add_field(
            name="What are your skills?", 
            value=f"<@&{roles_info['🎨 Artist']}> \n"
                  f"<@&{roles_info['👨‍💻 Programmer']}> \n"
                  f"<@&{roles_info['🖋️ Writer']}> \n"
                  f"<@&{roles_info['🎮 Gamer']}> \n", 
            inline=False
        )
        skills_message = await ctx.send(embed=embed)

        # Add reactions for skills roles
        skill_reactions = ["🎨", "👨‍💻", "🖋️", "🎮"]
        for reaction in skill_reactions:
            await skills_message.add_reaction(reaction)

        # Embed for editing software

        embed = discord.Embed()
        embed.add_field(
            name="Which software do you use?", 
            value=f"<@&{roles_info['📓 After Effect']}>\n"
                  f"<@&{roles_info['📘 VSP']}>\n"
                  f"<@&{roles_info['🎥 Capcut']}>\n"
                  f"<@&{roles_info['📷 Alight Motion']}>\n", 
            inline=False
        )
        software_message = await ctx.send(embed=embed)

        # Add reactions for editing software roles
        software_reactions = ["📓", "📘", "🎥", "📷"]
        for reaction in software_reactions:
            await software_message.add_reaction(reaction)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        guild = self.client.get_guild(payload.guild_id)
        if guild is None:
            return

        user = guild.get_member(payload.user_id)
        if user is None:
            return

        emoji = str(payload.emoji)
        role_id = None

        # Assign role based on emoji reaction
        if emoji == "🎨":
            role_id = roles_info["🎨 Artist"]
        elif emoji == "👨‍💻":
            role_id = roles_info["👨‍💻 Programmer"]
        elif emoji == "🖋️":
            role_id = roles_info["🖋️ Writer"]
        elif emoji == "🎮":
            role_id = roles_info["🎮 Gamer"]
        elif emoji == "📓":
            role_id = roles_info["📓 After Effect"]
        elif emoji == "📘":
            role_id = roles_info["📘 VSP"]
        elif emoji == "🎥":
            role_id = roles_info["🎥 Capcut"]
        elif emoji == "📷":
            role_id = roles_info["📷 Alight Motion"]

        if role_id:
            role = guild.get_role(role_id)
            if role:
                await user.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.client.get_guild(payload.guild_id)
        if guild is None:
            return

        user = guild.get_member(payload.user_id)
        if user is None:
            return

        emoji = str(payload.emoji)
        role_id = None

        # Remove role based on emoji reaction
        if emoji == "🎨":
            role_id = roles_info["🎨 Artist"]
        elif emoji == "👨‍💻":
            role_id = roles_info["👨‍💻 Programmer"]
        elif emoji == "🖋️":
            role_id = roles_info["🖋️ Writer"]
        elif emoji == "🎮":
            role_id = roles_info["🎮 Gamer"]
        elif emoji == "📓":
            role_id = roles_info["📓 After Effect"]
        elif emoji == "📘":
            role_id = roles_info["📘 VSP"]
        elif emoji == "🎥":
            role_id = roles_info["🎥 Capcut"]
        elif emoji == "📷":
            role_id = roles_info["📷 Alight Motion"]

        if role_id:
            role = guild.get_role(role_id)
            if role:
                await user.remove_roles(role)


async def setup(client):
    await client.add_cog(RoleReact(client))
