from discord.ext import commands, tasks
from twitchAPI.twitch import Twitch
from dotenv import load_dotenv
import notifications as nt
import discord
import data.db as db
import os

class TwitchBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        load_dotenv()
        client = os.getenv("TWITCH_CLIENT")
        secret = os.getenv("TWITCH_SECRET")
        self.twitch_api = Twitch(client, secret)

        self.update_streamers.start()

    @commands.group()
    async def twitch(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @twitch.command()
    async def add(self, ctx, streamer):
        try:
            res = self.twitch_api.get_users(logins=streamer)
            data = res["data"]

            # Streamer does not exist
            if len(data) == 0:
                raise Exception("Streamer not found")

            streamerID = data[0]["id"]
            db.data["streamers"][str(streamerID)] = {
                "online": False,
                "guilds": {
                    f"{ctx.guild.id}" : ctx.channel.id
                }
            }

            await nt.Success(ctx, "Streamer added")
        except Exception as err:
            await nt.Fail(ctx, str(err))
            return

    @twitch.command()
    async def remove(self, ctx, streamer):
        try :
            data = self.twitch_api.get_users(logins=streamer)["data"]

            # Streamer does not exist
            if len(data) == 0:
                raise Exception("Streamer not found")

            streamerID = data[0]["id"]
            db.data["streamers"][str(streamerID)]["guilds"].pop(str(ctx.guild.id), None)

            # Remove Streamer from Streamers table if he is not in any more guild
            count = len(db.data["streamers"][str(streamerID)]["guilds"])
            if count == 0:
                db.data["streamers"].pop(str(streamerID))

            await nt.Success(ctx, "Streamer removed")
        except Exception as err:
            await nt.Fail(ctx, str(err))

    @twitch.command()
    async def channel(self, ctx, channel):
        try :
            _channel = await commands.TextChannelConverter().convert(ctx, channel)

            for streamer in db.data["streamers"].values():
                print(streamer)
                if str(ctx.guild.id) in streamer["guilds"]:
                    streamer["guilds"][str(ctx.guild.id)] = _channel.id

            await nt.Success(ctx, f"Channel set to {_channel.name}")
        except Exception as err:
            await nt.Fail(ctx, str(err))

    @tasks.loop(seconds=30.0)
    async def update_streamers(self):
        """Updates the state of all streamers
        """
        for streamerID, data in db.data["streamers"].items():
            APIdata = self.twitch_api.get_streams(user_id=streamerID)["data"] # Data length is 0 when streamer is offline
            online = True if len(APIdata) > 0 else False
            wasOnline = data["online"]  # Streamer previous online state

            # Streamer went online
            if online and not wasOnline: 
                data["online"] = True
                profile_pic = self.twitch_api.get_users(user_ids=streamerID)["data"][0]["profile_image_url"]
                await self.send_notification(APIdata[0], data["guilds"], profile_pic)
            # Streamer went offline
            elif not online and wasOnline: 
                data["online"] = False

    #   Wait for bot to be ready before starting loop
    @update_streamers.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()

    async def send_notification(self, stream_data, guilds, profile_pic):
        # Embed data to pass
        thumbnail_url   = stream_data["thumbnail_url"].replace("-{width}x{height}", "")
        user            = stream_data["user_login"]
        username        = stream_data["user_name"]
        game            = stream_data["game_name"]
        title           = stream_data["title"]
        stream_url      = f"https://www.twitch.tv/{user}"
        twitch_icon     = "https://static.twitchcdn.net/assets/favicon-32-e29e246c157142c94346.png"

        # Embed setup
        embed = discord.Embed(title=title, url=stream_url, color=0xa970ff)
        embed.set_thumbnail(url=profile_pic)
        embed.set_author(name=username, icon_url=twitch_icon)
        embed.set_image(url=thumbnail_url)
        embed.add_field(name="Game", value=game, inline=False)

        # Send embed message in every guild
        for channelID in guilds.values():
            channel = self.bot.get_channel(channelID)
            
            await channel.send(
                content=f"@everyone {username} is now online at {stream_url} !",
                embed=embed
            )