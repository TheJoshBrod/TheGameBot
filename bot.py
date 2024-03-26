# bot.py
import os
import sqlite3
import discord
from datetime import datetime, timedelta
from discord.ext import commands
from dotenv import load_dotenv
from games import wordle

# Private Key
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create the bot client
intents = discord.Intents().all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load info of games
games = {"Wordle": wordle}
game_req = datetime.utcnow() - timedelta(seconds=10)

active_games = {}

def get_sender_name(message):
    """Returns string of user's nickname or global name."""
    try:
        return message.author.nick
    except:
        return message.author.global_name

def register_server(connection, message):
    """Registers Server into DB."""
    current_datetime = datetime.utcnow()
    unix_time = int(current_datetime.timestamp())

    if message.guild:
        # Message is from a guild (server)
        guild_id = message.guild.id
        guild_name = message.guild.name
        channel_id = message.channel.id
        channel_name = message.channel.name
        channel_type = True
    else:
        # Message is from a DM (Direct Message)
        guild_id = None
        guild_name = None
        channel_id = message.channel.id
        channel_name = None
        channel_type = False
        
    # Insert into the servers table
    cur = connection.execute('''
    INSERT INTO servers (GuildID, GuildName, ChannelID, ChannelName, ChannelType, LastMessageTime, Status, LastMessageSent)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (guild_id, guild_name, channel_id, channel_name, channel_type, unix_time, -1, None))
    
    if message.guild:
        cur = connection.execute('''
            SELECT ConversationID
            FROM servers
            WHERE GuildID = ? AND ChannelID = ?
        ''', (guild_id, channel_id))
    else:
        cur = connection.execute('''
            SELECT ConversationID
            FROM servers
            WHERE GuildID IS NULL AND ChannelID = ?
        ''', (channel_id,))

    connection.commit()
    result = cur.fetchone()
    
    connection.commit()
    return result

def register_message(connection, message):
    """Updates db by time of last message sent and registers servers."""
    guild_id = message.guild.id if message.guild is not None else None
    channel_id = message.channel.id if message.channel.id is not None else None

    if guild_id is not None:
        cur = connection.execute('''
            SELECT ConversationID, Status
            FROM servers
            WHERE GuildID = ? AND ChannelID = ?
        ''', (guild_id, channel_id))
    else:
        cur = connection.execute('''
            SELECT ConversationID, Status
            FROM servers
            WHERE GuildID IS NULL AND ChannelID = ?
        ''', (channel_id,))

    output = cur.fetchone()
    if output is None:
        conversation_id = register_server(connection, message)[0]
        status = -1
    else:
        conversation_id, status = output
        
    timestamp = int(datetime.utcnow().timestamp())
    cur = connection.execute('''
        UPDATE servers
        SET LastMessageTime = ?
        WHERE ConversationID = ?
    ''', (timestamp, conversation_id))
    
    connection.commit()
    return conversation_id, status
   
async def start_game(connection, message, convo_id, game_id):
    """Runs the game chosen by the player."""

    cur = connection.execute("UPDATE servers SET Status = ? WHERE ConversationID = ?", (game_id, convo_id,))
    connection.commit()
    active_games[convo_id] = games[sorted(games.keys())[game_id - 1]](message, convo_id)
    if game_id - 1 == 0:
        """Wordle."""
        embedVar = discord.Embed(title="Wordle:", description=f"Guesses Remaining: 6\n", color=0x5865F2)
        await message.channel.send(embed=embedVar)

async def menu(connection, message, convo_id):
    """Offers the user to begin a game."""
    cur = connection.execute('''
            SELECT LastMessageSent
            FROM servers
            WHERE ConversationID = ?''',(convo_id,))   
    LastMessageID = cur.fetchone()[0]

    if LastMessageID is not None:
        last_bot_message = None
        async for msg in message.channel.history(limit=100, before=message):
            if msg.embeds and msg.author == bot.user:
                last_bot_message = msg
                break
        if last_bot_message is not None:
            await last_bot_message.delete()
    
    out_msg = f'Hello {get_sender_name(message)}, what game do you want to play today?\n'
    out_msg += f'Respond in 10 seconds with one of the following number(s):\n'
    
    embed = discord.Embed(
    title="Game Menu 🕹️",
    description=out_msg,
    color=discord.Color.blue()  # You can set a color for the embed
    )
   
    for id, game in enumerate(sorted(games.keys())):
        embed.add_field(name=f"Option {id+1}", value=f"{game}", inline=False)
    
    await message.channel.send(embed=embed)
    
    cur = connection.execute('''
    UPDATE servers
    SET status = 0
    WHERE ConversationID = ?
    ''', (convo_id,))

    connection.commit()

async def message_handler(connection, message, convo_id, status):
    """Handles types of user input (Menu, Begining Games, Continuing Games)."""

    if message.content == f"<@{bot.user.id}>" and status == -1:
        await menu(connection, message, convo_id)
        
    elif status == 0 and message.content.isdigit():
        if int(message.content) <= len(games) and int(message.content) > 0:
            await start_game(connection, message, convo_id, int(message.content))
        else:
            error_msg = f"Please give a number between 1 - {len(games)}"
            embedVar = discord.Embed(title="❌Error Not Valid Game❌", description=error_msg, color=0xFF1010)
            await message.channel.send(embed=embedVar)
    elif status > 0:
        try:
            await active_games[convo_id].play_round(message)
            if active_games[convo_id].completed:
                active_games.pop(convo_id)
                cursor = connection.cursor()
                cursor.execute("""DELETE FROM servers WHERE ConversationID = ? """, (convo_id,))
                connection.commit()
        except KeyError:
            embedVar = discord.Embed(title="❌Error Please Try Again❌", color=0xFF1010)
            await message.channel.send(embed=embedVar)
            cursor = connection.cursor()
            cursor.execute("""DELETE FROM servers WHERE ConversationID = ? """, (convo_id,))
            connection.commit()

@bot.event 
async def on_ready(): 
    """Controls functionality after running."""
    print("Logged in as a bot {0.user}".format(bot))

@bot.event 
async def on_message(message): 
    """Responds to messages."""

    # Ignore messages from itself
    if message.author == bot.user: 
        return
    
    connection = sqlite3.connect('db/discord_bot.sqlite3')

    convo_id, status = register_message(connection, message)

    await message_handler(connection, message, convo_id, status)

# Boots up the Bot
bot.run(TOKEN)