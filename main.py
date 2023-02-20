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
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("TOKEN")
intents = discord.Intents.all()
intents.members = True
client = discord.Bot(intents=intents)


# colors of text in terminal: yellow=quote.

# Create an empty dictionary to store user data

# Create an empty dictionary to store user data
with open('levels.json', 'r') as file:
    user_data = json.loads(file.read())
with open('server_settings.json', 'r') as file:
    server_settings = json.loads(file.read())

# Define the amount of XP needed to level up
level_up_xp = 50

#error handling


@client.event
async def on_command_error(context, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await context.send("Oh no! Looks like you have missed out an argument for this command.")
  elif isinstance(error, commands.MissingPermissions):
    await context.send("Oh no! Looks like you Dont have the permissions for this command.")
  elif isinstance(error, commands.MissingRole):
    # bot errors
    await context.send("Oh no! Looks like you Dont have the roles for this command.")
  elif isinstance(error, commands.BotMissingPermissions):
    await context.send("Oh no! Looks like I Dont have the permissions for this command.")
  elif isinstance(error, commands.BotMissingRole):
    await context.send("Oh no! Looks like I Dont have the roles for this command.")
  elif isinstance(error, commands.CommandNotFound):
    await context.send(f" :warning: {error}.")
  elif isinstance(error, commands.MemberNotFound):
    await context.send("Please specify the member correctly!!!!!!")
  else:
    raise error


@client.event
async def on_message(msg: discord.Message):
    if not msg.author.bot:
        if str(msg.author.id) not in user_data:
            user_data[str(msg.author.id)] = {"xp": 0, "level": 1}
        user_data[str(msg.author.id)]["xp"] += 1
        if user_data[str(msg.author.id)]["xp"] >= level_up_xp:
            user_data[str(msg.author.id)]["level"] += 1
            if server_settings.get(str(msg.guild.id)) != None and server_settings[str(msg.guild.id)]['levelup_channel'] != None:
                await discord.utils.get(msg.guild.channels, id=server_settings[str(msg.guild.id)]['levelup_channel']).send(f'{msg.author.mention} just reached level {user_data[str(msg.author.id)]["level"]}!')
            user_data[str(msg.author.id)]["xp"] = 0

        with open('levels.json', 'w') as file:
            file.write(json.dumps(user_data, indent=4))


@client.slash_command()
@commands.has_permissions(administrator=True)
async def raid_mode(ctx):
    if server_settings.get(str(ctx.guild.id)) != None:
        if server_settings[str(ctx.guild.id)].get('raid_mode') != None:
            server_settings[str(ctx.guild.id)]['raid_mode'] = not server_settings[str(ctx.guild.id)]['raid_mode']
        else:
            server_settings[str(ctx.guild.id)]['raid_mode'] = True
    else:
        server_settings[str(ctx.guild.id)] = {}
        server_settings[str(ctx.guild.id)]['raid_mode'] = False
        server_settings[str(ctx.guild.id)]['levelup_channel'] = None
        server_settings[str(ctx.guild.id)]['welcome_channel'] = None
    with open('server_settings.json', 'w') as file:
        file.write(json.dumps(server_settings, indent=4))


@client.event
async def on_member_join(member):
    if server_settings.get(str(member.guild.id)) and server_settings[str(member.guild.id)].get('raid_mode', False):
        await member.ban('raid mode was activated when you joined')
        return

    if server_settings.get(str(member.guild.id)) != None and server_settings[str(member.guild.id)]['welcome_channel'] != None:
        await discord.utils.get(member.guild.channels, id=server_settings[str(member.guild.id)]['welcome_channel']).send(f'{member.mention} just joined the server!')


@client.slash_command()
async def set_levelup_channel(ctx, channel: discord.TextChannel):
    if server_settings.get(str(ctx.guild.id)) != None:
        server_settings[str(ctx.guild.id)]['levelup_channel'] = channel.id
    else:
        server_settings[str(ctx.guild.id)] = {}
        server_settings[str(ctx.guild.id)]['levelup_channel'] = channel.id
        server_settings[str(ctx.guild.id)]['welcome_channel'] = None
    with open('server_settings.json', 'w') as file:
        file.write(json.dumps(server_settings, indent=4))


@client.slash_command()
async def set_welcome_channel(ctx, channel: discord.TextChannel):
    if server_settings.get(str(ctx.guild.id)) != None:
        server_settings[str(ctx.guild.id)]['welcome_channel'] = channel.id
    else:
        server_settings[str(ctx.guild.id)] = {}
        server_settings[str(ctx.guild.id)]['welcome_channel'] = channel.id
        server_settings[str(ctx.guild.id)]['levelup_channel'] = None
    with open('server_settings.json', 'w') as file:
        file.write(json.dumps(server_settings, indent=4))


@client.slash_command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, _channel: discord.TextChannel = None):
    if _channel == None:
        channel = ctx.channel
    else:
        channel = _channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.respond(f'Channel locked by {ctx.author.mention}')


@client.slash_command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, limit: int):
    await ctx.channel.purge(limit=limit)
    await ctx.respond(f'{limit} message(s) were deleted by {ctx.author.mention}')


@client.slash_command()
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, msg):
	await ctx.send(msg)


@client.slash_command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason='he/she was bad'):
    if ctx.author.top_role.position > member.top_role.position:
        await member.ban()
        await ctx.respond(str(member)+' was banned by '+str(ctx.author)+', because '+reason)
    else:
        await ctx.respond('You need to be above a member to ban!')


@client.slash_command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, member: discord.Member):
    await member.unban()
    await ctx.respond(str(member)+'was unbanned by '+str(ctx.author))


@client.slash_command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason='he/she was bad'):
    if ctx.author.top_role.position > member.top_role.position:
        await member.kick(reason=reason)
        await ctx.respond(str(member)+' was kicked by '+str(ctx.author)+',because '+reason)
    else:
        await ctx.respond('You need to be above a member to kick!')


def add_xp(user, xp):
    if user not in user_data:
        user_data[user] = {"xp": 0, "level": 1}
    user_data[user]["xp"] += xp
    if user_data[user]["xp"] >= level_up_xp:
        user_data[user]["level"] += 1

        user_data[user]["xp"] = 0
    with open('levels.json', 'w') as file:
        file.write(json.dumps(user_data, indent=4))


@client.slash_command(
    name="rank",
    description="View your current level",

)
async def rank(interaction, member: discord.Member):
    if member is None:
        member = interaction.message.author
    if str(member.id) in user_data:
        await interaction.response.send_message(
            f"{member.mention} is currently level {user_data[str(member.id)]['level']} with {user_data[str(member.id)]['xp']} XP."
        )
    else:
        await interaction.respond(
            f"{member.mention} is not in the user data."
        )


@client.slash_command(
    name="givexp", description="Give XP to a user"
)
async def givexp(interaction: discord.Interaction, member: discord.Member, xp: int):
    if str(member.id) not in user_data:
        user_data[str(member.id)] = {"xp": 0, "level": 1}
    user_data[str(member.id)]["xp"] += xp
    while user_data[str(member.id)]["xp"] >= level_up_xp:
        user_data[str(member.id)]["xp"] -= level_up_xp
        user_data[str(member.id)]["level"] += 1
        if server_settings.get(str(interaction.guild.id)) != None and server_settings[str(interaction.guild.id)].get("levelup_channel") != None:
            level = user_data[str(member.id)]["level"]
            await discord.utils.get(interaction.guild.channels,id=server_settings[str(interaction.guild.id)]['levelup_channel']).send(f'{member.mention} just reached level {level}!')
    await interaction.respond(
        f"{member.mention} has been given {xp} XP. They now have {user_data[str(member.id)]['xp']} XP and are level {level}."
    )
    with open('levels.json', 'w') as file:
        file.write(json.dumps(user_data, indent=4))
    print(Fore.GREEN + f"xp was given to {member.mention}")


client.slash_command(
    name="leaderboard",
    description="View the leaderboard"

)


async def leaderboard(interaction):
    leaderboard = sorted(
        user_data.items(), key=lambda x: x[1]["level"], reverse=True)
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

    if member.top_role.position > role.position:
        await member.add_roles(role)
        await interaction.respond(
            f"{member.mention} has been given the {role.name} role.")
    else:
        await interaction.respond(f"{member.mention} You cant give a role to yourself thats higher than your top role!")


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
    username = interaction.author.name
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
        value="ExplodeCode \n OpenSourceSimon \n Tim \n Cattopy The Web \n csdaniel\(revamper,hoster\)",
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
    query = query.rstrip().replace(" ", "+")
    if engine == "google":
        await interaction.respond(f"https://google.com/search?q={query}")
    elif engine == "duckduckgo":
        await interaction.respond(f"https://duckduckgo.com/?q={query}")
    elif engine == "bing":
        await interaction.respond(f"https://bing.com/search?q={query}")
    elif engine == "baidu":
        await interaction.respond(f"https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd={query}")
    elif engine == "aol":
        await interaction.respond(f"https://search.aol.co.uk/aol/search?q={query}")
    elif engine == "ask":
        await interaction.respond(f"https://www.ask.com/web?q={query}")
    elif engine == "excite":
        await interaction.respond(f"https://results.excite.com/serp?q={query}")
    elif engine == "wolfram":
        await interaction.respond(f"https://www.wolframalpha.com/input?i={query}")
    elif engine == "yandex":
        await interaction.respond(f"https://yandex.com/search/?text={query}")
    elif engine == "lycos":
        await interaction.respond(f"https://search13.lycos.com/web/?q={query}")
    elif engine == "yahoo":
        await interaction.respond(f"https://search.yahoo.com/search;_ylt=Awr.Qpo5sPJj0CwvOY1LBQx.;_ylc=X1MDMjExNDcxNzAwMwRfcgMyBGZyA3NmcARmcjIDc2ItdG9wBGdwcmlkA2RYZWc2R3JVUkxTT19rcF9qdDY1ZkEEbl9yc2x0AzAEbl9zdWdnAzEwBG9yaWdpbgN1ay5zZWFyY2gueWFob28uY29tBHBvcwMwBHBxc3RyAwRwcXN0cmwDMARxc3RybAMxMARxdWVyeQNXaW5kb3dzJTIwMTEEdF9zdG1wAzE2NzY4NDkyMTg-?p={query}&fr2=sb-top&fr=sfp")
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
    print(Fore.GREEN +
          f"Thanks for using Bob the Bot! {client.user} is now online")


client.run(token)
