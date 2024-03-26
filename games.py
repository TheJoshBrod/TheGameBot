import discord
from random import randint

class wordle:
    def __init__(self, message, ConversationID):
        self.converationID = ConversationID
        self.channel = message.channel
        self.guild = message.guild

        self.guesses_remaining = 6
        word_num = randint(1,968)
        self.word = "" 

        self.completed = False

        with open("assets/answers_wordle.txt") as file:
            self.word = file.readlines()[word_num][:5]


    def valid_guess(self, guess):
        if len(guess) != 5:
            return False
        
        with open("assets/complete_wordle_dict.txt") as file:
            words = file.readlines()
            for word in words:
                if guess == word[:5].upper():
                    return True
        return False

    async def play_round(self, message):
        """User Submited Guess"""
        guess = message.content.upper()
        valid = self.valid_guess(guess)
        if not valid:
            embedVar = discord.Embed(title="Wordle:", description=f"Error", color=0x202020)
            embedVar.add_field(name="Your Guess:", value=guess, inline=True)
            embedVar.add_field(name="Error:", value="Invalid Guess", inline=False)
            await message.channel.send(embed=embedVar)
            return
        
        if guess == self.word:
            embedVar = discord.Embed(title="Wordle:", description=f"You Win!", color=0x58FF58)
            embedVar.add_field(name="Your Guess:", value=guess, inline=True)
            embedVar.add_field(name="Result:", value=":green_square::green_square::green_square::green_square::green_square:", inline=False)
            await message.channel.send(embed=embedVar)
            self.completed = True
            return

        self.guesses_remaining -= 1

        result = "" 
        temp_answer = self.word
        for pos, letter in enumerate(guess):
            if letter == self.word[pos]:
                result += ":green_square:"
            elif letter in temp_answer:
                skip = False
                for p, l in enumerate(guess):
                    if l == letter and self.word[p] == l:
                        result += ":black_large_square:"
                        skip = True
                        break
                if skip:
                    continue
                temp_answer = temp_answer.replace(letter, '', 1)
                result += ":yellow_square:"
            else:
                result += ":black_large_square:"

        embedVar = discord.Embed(title="Wordle:", description=f"Guesses Remaining: {self.guesses_remaining}\n", color=0x5865F2)
        embedVar.add_field(name="Your Guess:", value=guess, inline=True)
        embedVar.add_field(name="Result:", value=result, inline=False)
        await message.channel.send(embed=embedVar)

        if self.guesses_remaining == 0:
            embedVar = discord.Embed(title="Wordle:", description=f"Out of Guesses\n", color=0xFF2020)
            embedVar.add_field(name="The Correct Answer Was:", value=self.word, inline=True)
            await message.channel.send(embed=embedVar)
            self.completed = True
