# This project is made by ExplodeCode, OpenSourceSimon, Tim, Cattopy The Web

import discord
from discord.ext import commands
from discord import app_commands
from discord import Role
from colorama import init, Fore, Back, Style
import calendar
import datetime
import random
import requests
import bs4
import json
import math
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("TOKEN")
guildId = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)


# Define the amount of XP needed to level up
level_up_xp = 150

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guildId))
    print(Fore.CYAN + f"Successfully logged in as {client.user}")
    print("Packages and commands are loaded")
    print("User data loaded")
    print(Fore.GREEN + "-------------------")
    print(Fore.GREEN + f"Thanks for using Bob the Bot! {client.user} is now online")

# Function to add XP and level up the user
def add_xp(user, xp):
    f = open("user_data.json", "r")
    global user_data
    user_data = json.load(f)
    if user not in user_data:
        user_data[user] = {"xp": xp, "level": 1}
        with open("user_data.json", "w") as f:
            json.dump(user_data, f)
    user_data[user]["xp"] += xp
    # Update the json values
    with open("user_data.json", "w") as f:
        json.dump(user_data, f)
    if user_data[user]["xp"] >= level_up_xp:
        user_data[user]["level"] += 1
        user_data[user]["xp"] = 0
    f.close()


@tree.command(
    name="level",
    description="View your current level",
    guild=discord.Object(id=guildId),
)
async def level(interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user
    member = member.id
    f = open("user_data.json", "r")
    global user_data
    user_data = json.load(f)
    f.close()
    if str(member) in user_data:
        await interaction.response.send_message(
            f"<@{member}> is currently level {user_data[str(member)]['level']} with {user_data[str(member)]['xp']} XP."
        )
    else:
        await interaction.response.send_message(
            f"<@{member}> is not in the user data."
        )


@tree.command(
    name="givexp", description="Give XP to a user", guild=discord.Object(id=guildId)
)
async def givexp(interaction, member: discord.Member, xp: int):
    if member.id not in user_data:
        user_data[member.id] = {"xp": 0, "level": 1}
    user_data[member.id]["xp"] += xp
    user_data[member.id]["level"] = math.floor(
        0.1 * math.sqrt(user_data[member.id]["xp"])
    )
    await interaction.response.send_message(
        f"{member.mention} has been given {xp} XP. They now have {user_data[member.id]['xp']} XP and are level {user_data[member.id]['level']}."
    )
    print(Fore.GREEN + f"xp was given to {member.mention}")


@tree.command(
    name="leaderboard",
    description="View the leaderboard",
    guild=discord.Object(id=guildId),
) # TODO fix this
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
    await interaction.response.send_message(embed=embed)


# ping
@tree.command(
    name="ping", description="Check ping of the bot.", guild=discord.Object(id=guildId)
)
async def command(interaction):
    await interaction.response.send_message(f"Pong! Latency: {client.latency:.2f}s")


@tree.command(
    name="giverole",
    description="Assign a role to a user",
    guild=discord.Object(id=guildId),
)
@commands.has_permissions(manage_roles=True)
async def giverole(interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await interaction.response.send_message(
        f"{member.mention} has been given the {role.name} role."
    )


@tree.command(
    name="bored",
    description="Generates a random activity to do when feeling bored.",
    guild=discord.Object(id=guildId),
)
async def bored(interaction):
    response = requests.get("https://www.boredapi.com/api/activity")
    json_data = json.loads(response.text)
    activity = json_data["activity"]
    await interaction.response.send_message(f"Why not try to: {activity}")


@tree.command(
    name="announce",
    description="Make an announcement.",
    guild=discord.Object(id=guildId),
)
async def command(interaction, *, message: str):
    await interaction.response.send_message(message)


@tree.command(
    name="quote", description="Get a random quote.", guild=discord.Object(id=guildId)
)
async def command(interaction):
    response = requests.get("https://quotable.io/random")
    json_data = json.loads(response.text)
    content = json_data["content"]
    author = json_data["author"]
    embed = discord.Embed(title="Quote", description=content, color=0x00FF33)
    embed.set_footer(text=author)
    await interaction.response.send_message(embed=embed)


@tree.command(name="hello", description="Say hi!", guild=discord.Object(id=guildId))
async def command(interaction):
    greetings = ["Hello", "Hi", "Greetings", "Hola", "Bonjour", "Konnichiwa"]
    username = interaction.message.author.name
    await interaction.response.send_message(f"{random.choice(greetings)} {username}!")


# Info Command
@tree.command(
    name="info", description="Get info about the bot", guild=discord.Object(id=guildId)
)
async def command(interaction):
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
    await interaction.response.send_message(embed=embed)


# Calendar Command
@tree.command(
    name="calendar", description="View the calendar", guild=discord.Object(id=guildId)
)
async def command(interaction):
    yy = datetime.datetime.now().year
    mm = datetime.datetime.now().month
    await interaction.response.send_message(calendar.month(yy, mm))


# Search Command
@tree.command(
    name="search", description="Search the internet.", guild=discord.Object(id=guildId)
)
@app_commands.choices(
    engine=[
        app_commands.Choice(name="Google", value="google"),
        app_commands.Choice(name="Duck Duck Go", value="duckduckgo"),
        app_commands.Choice(name="Bing", value="bing"),
        app_commands.Choice(name="Let Me Google That", value="letmegoogle"),
    ]
)
async def command(interaction, query: str, engine: app_commands.Choice[str]):
    print(engine)  # Choice(name='Google', value='google')
    engine = engine.value
    query = query.rstrip().replace(" ", "+")
    if engine == "google":
        await interaction.response.send_message(f"https://google.com/search?q={query}")
    elif engine == "duckduckgo":
        await interaction.response.send_message(f"https://duckduckgo.com/?q={query}")
    elif engine == "bing":
        await interaction.response.send_message(f"https://bing.com/search?q={query}")
    elif engine == "letmegoogle":
        await interaction.response.send_message(
            f"https://letmegooglethat.com/?q={query}"
        )
    else:
        await interaction.response.send_message("Invalid engine.")


# 8ball command


@tree.command(
    name="8ball",
    description="Ask the magic 8-ball a question.",
    guild=discord.Object(id=guildId),
)
async def command(interaction, question: str):
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
    await interaction.response.send_message(f"Question: {question}\nAnswer: {response}")


# Math command
@tree.command(
    name="math", description="Solve a math problem", guild=discord.Object(id=guildId)
)
async def command(interaction, problem: app_commands.Range[str, 1]):
    # Split the message into a list of words
    words = problem.split()
    # Make sure we have enough arguments
    if len(words) != 3:
        await interaction.response.send_message(
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
            await interaction.response.send_message("Error: Cannot divide by zero.")
            return
        result = number1 / number2

    else:
        await interaction.response.send_message("Invalid operation. Use +, -, *, or /.")
        return
    # Send the result to the channel
    await interaction.response.send_message(f"Result: {result}")

# When a message is sent
@client.event
async def on_message(message):
    user = message.author.id
    return add_xp(user, random.randint(1, 5))



client.run(token)
