from discord.ext import commands
from dotenv import load_dotenv
import os
import db
import cogs

load_dotenv()

# Help command setup
Help_Setup = commands.DefaultHelpCommand(
    sort_commands=True,
    dm_help=True,
    width=255,
)

# Bot Setup
bot = commands.Bot(
    db.get_prefix,
    help_command=Help_Setup, 
    description="A multi tool bot",
)

# Add cogs to bot
bot.add_cog(cogs.Setup(bot))
bot.add_cog(cogs.TwitchBot(bot))

# Run bot
bot.run(os.getenv("DISCORD_TOKEN"))