from discord.ext import commands
import db

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot Ready")

        #! Database tests
        for guild in self.bot.guilds:
            await self.on_guild_join(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        db.query("INSERT INTO Guilds VALUES (?, ?, ?)", guild.id, "!!",  guild.channels[0].id)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        db.query("DELETE FROM Guilds WHERE id=?", guild.id)

    @commands.command()
    async def prefix(self, ctx, prefix: str):
        db.query("UPDATE Guilds SET prefix=? WHERE id=?", prefix, ctx.guild.id)

    @commands.command()
    async def test(self, ctx):
        print("test")