# bot.py
import os
import discord
from datetime import datetime, timedelta
from discord.ext import commands
from dotenv import load_dotenv
from games import codenames, wordle
from message_obj import message_obj

# Private Key
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create the bot client
intents = discord.Intents().all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load info of games
games = {"CodeNames": codenames, "Wordle": wordle}
game_req = datetime.utcnow() - timedelta(seconds=10)
user_req = ""

# Load history of bot
channel_mode = {}

async def start_game(message, msg, game_id):
    """Runs the game chosen by the player."""
    if game_id.isdigit() == True and int(game_id) <= len(games) and int(game_id) > 0:
        game_id = int(game_id)
        channel_mode[msg.guild][msg.channel] = games[sorted(games.keys())[game_id - 1]] 
        await games[sorted(games.keys())[game_id - 1]](message.channel)
    else:
        out_msg = f"Error Not Valid Game:\nPlease give a number in the range of 1 to {len(games)}"
        await message.channel.send(out_msg)
        return

async def game_select(message, msg):
    # Handles responses to game chosen
    if (datetime.utcnow() - game_req) <= timedelta(seconds=10) and user_req == msg.username and msg.content.isdigit():
        await start_game(message.channel, message.guild, int(msg.content))


async def menu(message,msg):
    # Handles being summoned (@ed)
    global game_req
    global user_req
    if "<@1204239173742108682>" in msg.content.lower():
        out_msg = f'Hello {msg.username}, what game do you want to play today?\n'
        out_msg += f'Respond in 10 seconds with one of the following number(s):\n'
        for id, game in enumerate(sorted(games.keys())):
            out_msg += "- " + game + ": " + str(id + 1) + "\n"
        await message.channel.send(out_msg)
        game_req = datetime.utcnow()
        user_req = msg.username

        channel_mode[msg.guild][msg.channel] = "game_select" 
        return


@bot.event
async def on_reaction_add(reaction, user):
    """TODO: Check if the reaction is added to a specific message"""
    print(f'Reaction {reaction.emoji} added by {user.name}')
    print(reaction.message.id)

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
    
    msg = message_obj(message)

    # Registers Guild/Channel    
    if channel_mode.get(msg.guild, None) is None:
        print(f"Joined new Guild: {msg.channel} of {msg.guild}")
        channel_mode[msg.guild] = {}
        channel_mode[msg.guild][msg.channel] = "idle"
    elif channel_mode[msg.guild].get(msg.channel, None) is None:
        channel_mode[msg.guild][msg.channel] = "idle"
    

    # Checks if Bot was mentioned less than 10 seconds ago
    if channel_mode[msg.guild][msg.channel] == "game_select" and datetime.utcnow() - game_req >= timedelta(seconds=10):
        channel_mode[msg.guild][msg.channel] = "idle"

    # Debugging
    print(f"From {msg.username} to {msg.channel} in {msg.guild}: {msg.content}\n\t- Status: {channel_mode[msg.guild][msg.channel]}")

    # Handles Game type
    if channel_mode[msg.guild][msg.channel] == "idle":
        await menu(message, msg)
    elif channel_mode[msg.guild][msg.channel] == "game_select":
        await start_game(message, msg, message.content)
    elif channel_mode[msg.guild][msg.channel] == wordle:
        await wordle(message.channel)

# Boots up the Bot
bot.run(TOKEN)