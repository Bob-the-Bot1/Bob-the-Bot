import discord
from discord import app_commands
from colorama import init, Fore, Back, Style
import random
import requests
import bs4
import json
import math

guildId = 12345  # Replace with Guild Id

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)
# colors of text in terminal: yellow=quote.


users = {}


@client.event
async def on_message(message):
    if message.author == client.user:
        return

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
        await message.channel.send(
            f"{message.author.mention} is level {user['level']} with {user['exp']} experience points. Well done :)")

# Ping Command
@tree.command(name="ping", description="Check the bot's ping.", guild=discord.Object(id=guildId))
async def command(interaction):
    await interaction.response.send_message("Pong")


@tree.command(name="quote", description="Get a random quote.", guild=discord.Object(id=guildId))
async def command(interaction):
    # Fetch a random quote from a website
    res = requests.get("https://www.goodreads.com/quotes")
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    quote_tags = soup.select('.quoteText')
    author_tags = soup.select('.authorOrTitle')
    quote = quote_tags[random.randint(0, len(quote_tags) - 1)].getText().strip()
    author = author_tags[random.randint(0, len(author_tags) - 1)].getText().strip()

    # Create an embed with the quote and its author
    embed = discord.Embed(title="Quote of the day", description=quote, color=0x00ff33)
    embed.set_author(name='quote')
    await interaction.response.send_message(embed=embed)


# Hello command

@tree.command(name="hello", description="Say hi!", guild=discord.Object(id=guildId))
async def command(interaction):
    await interaction.response.send_message("Howdy!")


# Info Command
@tree.command(name="info", description="Get info about the bot", guild=discord.Object(id=guildId))
async def command(interaction):
    embed = discord.Embed(title="Info",
                          description="I am a bot made and programmed by @ExplodeCode and I will only work when ExplodeCode turns me on",
                          color=0x00ff33)
    embed.set_author(name="Bob the Bot")
    embed.add_field(name="Develpers", value="ExplodeCode \n OpenSourceSimon \n Tim \n Cattopy The Web", inline=False)
    await interaction.response.send_message(embed=embed)


# Calendar Command
@tree.command(name="calendar", description="View the calendar", guild=discord.Object(id=guildId))
async def command(interaction):
    import calendar
    yy = 2023
    mm = 1
    await interaction.response.send_message(calendar.month(yy, mm))


# Search Command
@tree.command(name="search", description="Search the internet.", guild=discord.Object(id=guildId))
async def command(interaction, query: app_commands.Range[str, 1]):
    # Perform the search
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(f"https://google.com/search?q={query}", headers=headers)
    res.raise_for_status()
    # Parse the search results
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    links = soup.select('.r a')

    # Send the results to the channel
    embed = discord.Embed(title="Search", description=f"Search results for '{query}'", color=0x00ff33)

    await interaction.response.send_message(embed=embed)


# Math command
@tree.command(name="math", description="Solve a math problem", guild=discord.Object(id=guildId))
async def command(interaction, problem: app_commands.Range[str, 1]):
    # Split the message into a list of words
    words = problem.split()
    # Make sure we have enough arguments
    if len(words) != 3:
        await interaction.response.send_message("Invalid number of arguments. Use -math [number] [operation] [number]")
        return
    # Get the first number and operation from the message
    number1 = float(words[0])
    operation = words[1]
    # Get the second number from the message
    number2 = float(words[2])
    # Perform the requested operation
    if operation == "+":
        result = number1 + number2
    elif operation == "-":
        result = number1 - number2
    elif operation == "*":
        result = number1 * number2
    elif operation == "/":
        if number2 == 0:
            await interaction.response.send_message("Error: Cannot divide by zero.")
            return
        result = number1 / number2

    else:
        await interaction.response.send_message("Invalid operation. Use +, -, *, or /.")
        return
    # Send the result to the channel
    await interaction.response.send_message(f"Result: {result}")


# When Bot is ready.
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guildId))
    print(Fore.CYAN + f'Successfully logged in as {client.user}!')
    print('-------------------')
    print('This is for testing only')

client.run('ADD_YOU_BOT_TOKEN_HERE')
