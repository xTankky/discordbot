from discord.ext import commands, tasks
from twitchAPI.twitch import Twitch
from dotenv import load_dotenv
import notifications as nt
import discord
import db
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
        """Adds a streamer to be notified when he lives

        Args:
            streamer (str): Streamer username
        """
        try:
            res = self.twitch_api.get_users(logins=streamer)
            data = res["data"]

            # Streamer does not exist
            if len(data) == 0:
                raise Exception("Streamer not found")

            id = data[0]["id"]
            db.query("INSERT INTO TwitchStreamers VALUES (?, ?)", id, False)
            db.query("INSERT INTO TwitchGuilds VALUES (?, ?)", id, ctx.guild.id)

            await nt.Success(ctx, "Streamer added")
        except Exception as err:
            await nt.Fail(ctx, str(err))
            return

    @twitch.command()
    async def remove(self, ctx, streamer):
        """Removes a streamer

        Args:
            streamer (str): Streamer username
        """
        try :
            data = self.twitch_api.get_users(logins=streamer)["data"]

            # Streamer does not exist
            if len(data) == 0:
                raise Exception("Streamer not found")

            id = data[0]["id"]
            db.query("DELETE FROM TwitchGuilds WHERE streamer=? AND guild=?", id, ctx.guild.id)

            # Remove Streamer from Streamers table if he is not in any more guild
            count = db.fetch("SELECT COUNT(streamer) FROM TwitchGuilds WHERE streamer=?", id)[0][0] # List into tuple, yikes
            if count == 0:
                db.query("DELETE FROM TwitchStreamers WHERE streamer=?", id)

            await nt.Success(ctx, "Streamer removed")
        except Exception as err:
            await nt.Fail(ctx, str(err))

    @twitch.command()
    async def channel(self, ctx, channel):
        """Set the channel where notfications will be displayed

        Args:
            channel (mention): Channel mention
        """
        try :
            _channel = await commands.TextChannelConverter().convert(ctx, channel)
            db.query("UPDATE Guilds SET twitch_channel=? WHERE id=?", _channel.id, ctx.guild.id)
            await nt.Success(ctx, f"Channel set to {_channel.name}")
        except Exception as err:
            await nt.Fail(ctx, str(err))

    @tasks.loop(seconds=30.0)
    async def update_streamers(self):
        """Updates the state of all streamers
        """
        streamers = db.fetch("SELECT * FROM TwitchStreamers")

        for streamer in streamers:
            id = streamer[0]
            online = streamer[1]
            data = self.twitch_api.get_streams(user_id=id)["data"] 
            # Data length is 0 when the streamer is offline

            if len(data) > 0 and not online: # Streamer went online
                db.query("UPDATE TwitchStreamers SET online=? WHERE streamer=?", True, id)
                guilds = db.fetch("SELECT guild FROM TwitchGuilds WHERE streamer=?", id)
                profile_pic = self.twitch_api.get_users(user_ids=id)["data"][0]["profile_image_url"]
                await self.send_notification(data[0], guilds, profile_pic)
            elif len(data) == 0 and online: # Streamer went offline
                db.query("UPDATE TwitchStreamers SET online=? WHERE streamer=?", False, id)

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
        for guild in guilds :
            _channel = db.fetch("SELECT twitch_channel FROM Guilds WHERE id=?", guild[0])[0][0]
            channel = self.bot.get_channel(int(_channel))
            
            await channel.send(
                content=f"@everyone {username} is now online at {stream_url} !",
                embed=embed
            )