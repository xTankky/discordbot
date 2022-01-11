import sqlite3

tables = [
    "CREATE TABLE IF NOT EXISTS Guilds (id PRIMARY KEY, prefix, twitch_channel)",
    "CREATE TABLE IF NOT EXISTS TwitchStreamers (streamer PRIMARY KEY, online)",
    "CREATE TABLE IF NOT EXISTS TwitchGuilds (streamer, guild)",
]

def connect():
    """Connect to Database

    Returns:
        tuple: Connection and Cursor object
    """ 
    con = sqlite3.connect("bot.db")
    cur = con.cursor()
    return con, cur

def init():
    """Create tables in Database if they do not exists
    """
    con, cur = connect()

    for _query in tables:
        cur.execute(_query)
    
    con.commit()
    con.close()

def query(query, *args):
    """Execute and commit a query

    Args:
        query (str): SQL Query to execute
    """
    con, cur = connect()
    cur.execute(query, args)
    con.commit()

    if fetch:
        res = cur.fetchall()
        con.close()
        return res
    else :
        con.close()

def fetch(query, *args):
    """Execute, commit and fetch a query

    Args:
        query (str): SQL Query to execute
    Returns:
        tuple: Query data fetched
    """
    con, cur = connect()
    cur.execute(query, args)
    res = cur.fetchall()
    con.commit()
    con.close()

    return res

def get_prefix(client, message):
    """Get prefixes from Guilds""" 
    guild_id = message.guild.id
    prefix = fetch("SELECT prefix FROM Guilds WHERE id=?", guild_id)

    return "!!" if not prefix else prefix[0]

init()
