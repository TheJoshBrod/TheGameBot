# bot.py
import os
import discord
from datetime import datetime, timedelta
from discord.ext import commands
from dotenv import load_dotenv
from games import codenames

# Private Key
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create the bot client
intents = discord.Intents().all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load info of games
games = {"CodeNames": codenames}
game_req = datetime.utcnow() - timedelta(seconds=10)
user_req = ""


async def start_game(channel, game_id):
    """Runs the game chosen by the player."""
    if game_id > len(games) or game_id <= 0:
        out_msg = f"Error Not Valid Game:\nPlease give a number in the range of 1 to {len(games)}"
        await channel.send(out_msg)
        return
    await games[sorted(games.keys())[game_id - 1]]()

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
    global game_req
    global user_req
    try:
        username = message.author.nick
    except:
        username = str(message.author).split("#")[0]
    try:
        channel = str(message.channel.name) 
    except:
        channel = f"private_message_with_{username}"
    user_message = str(message.content) 
  
    # Ignore messages from itself
    if message.author == bot.user: 
        return
    
    # For debugging purposes
    print(f'Message {user_message} by {username} on {channel}') 

    # Handles responses to game chosen
    if (datetime.utcnow() - game_req) <= timedelta(seconds=10) and user_req == username and user_message.isdigit():
        await start_game(message.channel, int(user_message))

    # Handles being summoned (@ed)
    if "<@1204239173742108682>" in user_message.lower():
        out_msg = f'Hello {username}, what game do you want to play today?\n'
        out_msg += f'Respond in 10 seconds with one of the following number(s):\n'
        for id, game in enumerate(sorted(games.keys())):
            out_msg += "- " + game + ": " + str(id + 1) + "\n"
        await message.channel.send(out_msg)
        game_req = datetime.utcnow()
        user_req = username
        return

bot.run(TOKEN)