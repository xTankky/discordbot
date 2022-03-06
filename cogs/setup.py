from discord.ext import commands
import notifications as nt
import data.db as db

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot Ready")
        db.save_files.start()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        db.add_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        db.data["guilds"].pop(str(guild.id), None)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix: str):
        db.data["guilds"][str(ctx.guild.id)]["prefix"] = prefix

    @commands.command()
    async def test(self, ctx):
        await nt.Success(ctx, "Test")

    @commands.command()
    async def source(self, ctx):
        channel = ctx.author.dm_channel
        if not channel:
            channel = await ctx.author.create_dm()
        await channel.send(content="https://github.com/xTankky/discordbot")