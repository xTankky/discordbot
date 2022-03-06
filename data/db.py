import json
from discord.ext import tasks

files = ('guilds', 'streamers')
data = {}

# Get file data
for name in files:
    with open(f"data/{name}.json") as f:
        data[name] = json.loads(f.read())

# Save data into files every 30 seconds
@tasks.loop(seconds=10)
async def save_files():
    for name in files:
        with open(f"data/{name}.json", "w") as f:
            f.write(json.dumps(data[name], indent=4))

def get_prefix(client, message): 
    prefix = data["guilds"][str(message.guild.id)]["prefix"]
    return prefix if prefix is not None else "!"

def add_guild(guild_id):
    data["guilds"][str(guild_id)] = {
        "prefix": "!"
    }