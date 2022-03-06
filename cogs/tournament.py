from discord.ext import commands
import notifications as nt
import discord
import data.db as db

class Tournament(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    async def tourn(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @tourn.command()
    async def single(self, ctx, teamSize=1):
        await self.msg_start(ctx, "Single Elimination")

    @tourn.command()
    async def double(self, ctx, teamSize=1):
        await self.msg_start(ctx, "Double Elimination")

    @tourn.command()
    async def rr(self, ctx, teamSize=1):
        await self.msg_start(ctx, "Round Robin")

    @commands.Cog.listener()
    async def on_reaction_add(reaction, user):
        pass

    async def msg_start(self, ctx, title):
        """Sends a starter message"""
        embed=discord.Embed(title=f"{title} Tournament")
        embed.add_field(name="✋", value="Add yourself")
        embed.add_field(name="🆗", value="Start tournament")
        msg = await ctx.send(embed=embed)

        await msg.add_reaction("✋")
        await msg.add_reaction("🆗")