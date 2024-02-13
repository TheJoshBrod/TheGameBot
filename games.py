import discord

async def codenames( channel):
    return

async def wordle(channel):
    embedVar = discord.Embed(title="Game", description="Wordle", color=0x5865F2)
    embedVar.add_field(name="Guess History", value="hi", inline=False)
    await channel.send(embed=embedVar)