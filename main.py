import discord
from colorama import init, Fore, Back, Style
import random
import requests
import bs4
import math

#colors of text in terminal: yellow=quote.

quotes = [
    "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. As with all matters of the heart, you'll know when you find it. - Steve Jobs",
    "The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart. - Helen Keller",
    "We may encounter many defeats but we must not be defeated. - Maya Angelou",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
    "Hardships often prepare ordinary people for an extraordinary destiny. - C.S. Lewis"
]


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
users = {}
@client.event
async def on_ready():
    print(Fore.CYAN + f'Successfully logged in as {client.user}!')
    print('-------------------')
    print('This is for testing only')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('-hello'):
        print('')
        print(Fore.GREEN + '----------------------------------')
        print(Fore.GREEN + 'hello command used')
        await message.channel.send('Hello!')

    if message.content.startswith('-help'):
        print('')
        print(Fore.GREEN + '--------------------------------------')
        print(Fore.GREEN + "help command used")
        await message.channel.send("List of Commands\n-help > Provides this message.\n-info > Provides a list of information.\n-hello > Replies with hello!\n-8ball > Plays a game of 8ball.\n-roll > Randomly rolls a number between 1 and 6.\n-search > [idk what command does].\n-math > Solves your math equation.")

        print('')
        print(Fore.RED + '------------------------------------------')
        print(Fore.RED + 'help command output completed')
    if message.content.startswith('-roll'):
        print('')
        print(Fore.GREEN + '-----------------------------------')
        print(Fore.GREEN + "roll command was used")
        dice_roll = random.randint(1, 6)
        await message.channel.send(f"You rolled a {dice_roll}!")

    if message.content.startswith('-info'):
        print('')
        print('-----------------------------------')
        print('info command used')
        await message.channel.send('I am a bot made and programmed by @ExplodeCode and I will only work when ExplodeCode turns me on')

    if message.content.startswith('-calendar'):
        import calendar
        yy = 2023
        mm = 1
        print('')
        print(Fore.CYAN + '-----------------------------------')
        print(Fore.CYAN + 'calendar command used' + calendar.month(yy, mm))
        await message.channel.send(calendar.month(yy,mm))

    if message.content.startswith('-8ball'):
        # Get the question from the message
        print('')
        print(Fore.LIGHTBLUE_EX + '8ball command used')
        question = message.content[7:]

        # Check if the question is empty
        if len(question) == 0:
            await message.channel.send("You didn't ask a question!")
            return

        # Select a random response
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
        response = random.choice(responses)

        # Send the response
        await message.channel.send(f"Question: {question}\nAnswer: {response}")

    if message.content.startswith('-search'):
        print(Fore.BLUE + 'search command used')
        # Get the search query
        query = message.content[8:]

        # Check if the query is empty
        if len(query) == 0:
            await message.channel.send("You didn't enter a search query!")
            return
        else:
            print(Fore.BLUE + 'performing search')
            # Perform the search
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(f"https://google.com/search?q={query}", headers=headers)
            res.raise_for_status()
            # Parse the search results
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            links = soup.select('.r a')
            # Send the results to the channel
            result_str = f"Search results for '{query}':\n"
            for i, link in enumerate(links):
                result_str += f"{i + 1}. {link.text}\n{link.get('href')}\n"
                await message.channel.send(result_str)
                print(result_str)

    if message.content.startswith("-math"):
        print(Fore.BLUE + 'math command used')
        # Split the message into a list of words
        words = message.content.split()
        # Make sure we have enough arguments
        if len(words) != 4:
            await message.channel.send("Invalid number of arguments. Use -math [number] [operation] [number]")
            return
        # Get the first number and operation from the message
        number1 = float(words[1])
        operation = words[2]
        # Get the second number from the message
        number2 = float(words[3])
        # Perform the requested operation
        if operation == "+":
            result = number1 + number2
        elif operation == "-":
            result = number1 - number2
        elif operation == "*":
            result = number1 * number2
        elif operation == "/":
            if number2 == 0:
                await message.channel.send("Error: Cannot divide by zero.")
                return
            result = number1 / number2

        else:
            await message.channel.send("Invalid operation. Use +, -, *, or /.")
            return
        # Send the result to the channel
        await message.channel.send(f"Result: {result}")

    if message.content.startswith("-echo"):
        print('')
        print('echo command used')
        # Get the message to echo from the command
        echo = message.content[6:]
        # Send the message to the channel
        await message.channel.send(echo)

    if message.author not in users:
        users[message.author] = {"level": 1, "exp": 0}
    users[message.author]["exp"] += random.randint(5, 15)

    # Chec
    user = users[message.author]
    if user["exp"] >= 100:
        user["level"] += 1
        user["exp"] = 0
        await message.channel.send(f"{message.author.mention} has leveled up to level {user['level']}!")

    if message.content == "-level":
        print('')
        print(Fore.MAGENTA + 'level command used')
        await message.channel.send(f"{message.author.mention} is level {user['level']} with {user['exp']} experience points. Well done :)")
    if message.content == "-quote":
        print('')
        print('quote command used')
        # Select a random quote from the list
        quote = random.choice(quotes)
        # Send the quote to the channel
        await message.channel.send(quote)
        print(quote)
    
    if message.content.startswith("-announce"):
        print('')
        print('announce command used')
        # Get the message to echo from the command
        echo = message.content[6:]
        # Send the message to the channel
        await message.channel.send(echo)

client.run('ADD_YOUR_TOKEN')
