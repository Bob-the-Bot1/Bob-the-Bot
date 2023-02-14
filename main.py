# This project is made by ExplodeCode, OpenSourceSimon, Tim, Cattopy The Web

import discord
from discord.ext import commands

from discord import Role
from colorama import init, Fore, Back, Style
import calendar
import datetime
import random
import requests
import bs4
import json
import math

import os




guildId = 123456789
intents = discord.Intents.default()
intents.message_content = True
client = discord.Bot(intents=intents)


# colors of text in terminal: yellow=quote.

# Create an empty dictionary to store user data

# Create an empty dictionary to store user data

user_data = {}

# Define the amount of XP needed to level up
level_up_xp = 150


# Function to add XP and level up the user
def add_xp(user, xp):
    if user not in user_data:
        user_data[user] = {"xp": 0, "level": 1}
    user_data[user]["xp"] += xp
    if user_data[user]["xp"] >= level_up_xp:
        user_data[user]["level"] += 1
        user_data[user]["xp"] = 0


@client.slash_command(
    name="level",
    description="View your current level",

)
async def level(interaction, member: discord.Member):
    if member is None:
        member = interaction.message.author
    if member in user_data:
        await interaction.response.send_message(
            f"{member.mention} is currently level {user_data[member]['level']} with {user_data[member]['xp']} XP."
        )
    else:
        await interaction.respond(
            f"{member.mention} is not in the user data."
        )


@client.slash_command(
    name="givexp", description="Give XP to a user"
)
async def givexp(interaction, member: discord.Member, xp: int):
    if member.id not in user_data:
        user_data[member.id] = {"xp": 0, "level": 1}
    user_data[member.id]["xp"] += xp
    user_data[member.id]["level"] = math.floor(
        0.1 * math.sqrt(user_data[member.id]["xp"])
    )
    await interaction.respond(
        f"{member.mention} has been given {xp} XP. They now have {user_data[member.id]['xp']} XP and are level {user_data[member.id]['level']}."
    )
    print(Fore.GREEN + f"xp was given to {member.mention}")


client.slash_command(
    name="leaderboard",
    description="View the leaderboard"

)
async def leaderboard(interaction):
    leaderboard = sorted(user_data.items(), key=lambda x: x[1]["level"], reverse=True)
    embed = discord.Embed(title="Leaderboard", color=0x00FF33)
    for i, user in enumerate(leaderboard):
        member = interaction.message.guild.get_member(int(user[0]))
        if member:
            embed.add_field(
                name=f"{i + 1}. {member.name}",
                value=f"Level: {user[1]['level']} XP: {user[1]['xp']}",
                inline=False,
            )
    await interaction.respond(embed=embed)


# ping
@client.slash_command(
    name="ping", description="Check ping of the bot."
)
async def ping(interaction):
    await interaction.respond(f"Pong! Latency: {client.latency:.2f}s")


@client.slash_command(
    name="giverole",
    description="Assign a role to a user",

)
@commands.has_permissions(manage_roles=True)
async def giverole(interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await interaction.respond(
        f"{member.mention} has been given the {role.name} role."
    )

@client.slash_command(
    name="remrole",
    description="Removes a role from a user"
    
)
@commands.has_permissions(manage_roles=True)
async def remrole(interaction, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await interaction.respond(
        f"{member.mention} has been removed from the {role.name} role."
    )

@client.slash_command(
    name="bored",
    description="Generates a random activity to do when feeling bored.",

)
async def bored(interaction):
    response = requests.get("https://www.boredapi.com/api/activity")
    json_data = json.loads(response.text)
    activity = json_data["activity"]
    await interaction.respond(f"Why not try to: {activity}")


@client.slash_command(
    name="announce",
    description="Make an announcement."

)
async def announce(interaction, *, message: str):
    await interaction.respond(message)


@client.slash_command(
    name="quote", description="Get a random quote."
)
async def quote(interaction):
    response = requests.get("https://quotable.io/random")
    json_data = json.loads(response.text)
    content = json_data["content"]
    author = json_data["author"]
    embed = discord.Embed(title="Quote", description=content, color=0x00FF33)
    embed.set_footer(text=author)
    await interaction.respond(embed=embed)


@client.slash_command(name="hello", description="Say hi!")
async def hello(interaction):
    greetings = ["Hello", "Hi", "Greetings", "Hola", "Bonjour", "Konnichiwa"]
    username = interaction.message.author.name
    await interaction.respond(f"{random.choice(greetings)} {username}!")


# Info Command
@client.slash_command(
    name="info", description="Get info about the bot"
)
async def info(interaction):
    embed = discord.Embed(
        title="Info",
        description="I am a Top G bot made in python, I am an open source project and anyone can contribute!",
        color=0x00FF33,
    )
    embed.set_author(name="Bob the Bot")
    embed.add_field(
        name="Developers",
        value="ExplodeCode \n OpenSourceSimon \n Tim \n Cattopy The Web",
        inline=False,
    )
    await interaction.respond(embed=embed)


# Calendar Command
@client.slash_command(
    name="calendar", description="View the calendar"
)
async def cal(interaction):
    yy = datetime.datetime.now().year
    mm = datetime.datetime.now().month
    await interaction.respond(calendar.month(yy, mm))


# Search Command
@client.slash_command(
    name="search", description="Search the internet."
)









async def search(interaction, query: str, engine: str):
    print(engine)  # Choice(name='Google', value='google')
    engine = engine.value
    query = query.rstrip().replace(" ", "+")
    if engine == "google":
        await interaction.respond(f"https://google.com/search?q={query}")
    elif engine == "duckduckgo":
        await interaction.respond(f"https://duckduckgo.com/?q={query}")
    elif engine == "bing":
        await interaction.respond(f"https://bing.com/search?q={query}")
    elif engine == "letmegoogle":
        await interaction.respond(
            f"https://letmegooglethat.com/?q={query}"
        )
    else:
        await interaction.respond("Invalid engine.")


# 8ball command


@client.slash_command(
    name="8ball",
    description="Ask the magic 8-ball a question."

)
async def ball(interaction, query: str):
    # Get the question from the message
    question = query

    # Check if the question is empty
    if len(question) == 0:
        await interaction.respond("You didn't ask a question!")
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
        "Very doubtful.",
    ]
    response = random.choice(responses)

    # Send the response
    await interaction.respond(f"Question: {question}\nAnswer: {response}")


# Math command
@client.slash_command(
    name="math", description="Solve a math problem"
)
async def calc(interaction, problem: str):
    # Split the message into a list of words
    words = problem.split()
    # Make sure we have enough arguments
    if len(words) != 3:
        await interaction.respond(
            "Invalid number of arguments. Use -math [number] [operation] [number]"
        )
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
            await interaction.respond("Error: Cannot divide by zero.")
            return
        result = number1 / number2

    else:
        await interaction.respond("Invalid operation. Use +, -, *, or /.")
        return
    # Send the result to the channel
    await interaction.respond(f"Result: {result}")


# When Bot is ready.
@client.event
async def on_ready():
    print(Fore.CYAN + f"Successfully logged in as {client.user}")
    print("Packages and commands are loaded")
    print(Fore.GREEN + "-------------------")
    print(Fore.GREEN + f"Thanks for using Bob the Bot! {client.user} is now online")


client.run('TOKEN') 
