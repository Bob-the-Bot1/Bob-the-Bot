import discord
import os
import json
import datetime
import asyncio
from dotenv import load_dotenv
from colorama import init, Fore, Back, Style
import random
import requests
import bs4
import math

# colors of text in terminal: yellow=quote.

load_dotenv()
client = discord.Client()

quotes = [
    "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. As with all matters of the heart, you'll know when you find it. - Steve Jobs",
    "The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart. - Helen Keller",
    "We may encounter many defeats but we must not be defeated. - Maya Angelou",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
    "Hardships often prepare ordinary people for an extraordinary destiny. - C.S. Lewis",
    "A hacker is someone trying to figure out a way to make toast with a coffee maker. Wau Holland - Chaos Computer Club Founder",
    "You can't live someone else's expectations in life. It's a recipe for disaster. - Bear Grylls",
    "Improvise. Adapt. Overcome - Bear Grylls"
]

intents = discord.Intents.default()
intents = discord.Intents(members=True, presences=True)
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

    elif message.content.startswith('-hello'):
        print('')
        print(Fore.GREEN + '----------------------------------')
        print(Fore.GREEN + 'hello command used')
        await message.channel.send('Hello!')

    elif message.content.startswith('-help'):
        print('')
        print(Fore.GREEN + '--------------------------------------')
        print(Fore.GREEN + "help command used")
        await message.channel.send("List of Commands\n-help > Provides this message.\n-info > Provides a list of information.\n-hello > Replies with hello!\n-8ball > Plays a game of 8ball.\n-roll > Randomly rolls a number between 1 and 6.\n-search > [idk what command does].\n-math > Solves your math equation.")

        print('')
        print(Fore.RED + '------------------------------------------')
        print(Fore.RED + 'help command output completed')
    elif message.content.startswith('-roll'):
        print('')
        print(Fore.GREEN + '-----------------------------------')
        print(Fore.GREEN + "roll command was used")
        dice_roll = random.randint(1, 6)
        await message.channel.send(f"You rolled a {dice_roll}!")

    elif message.content.startswith('-info'):
        print('')
        print('-----------------------------------')
        print('info command used')
        await message.channel.send('I am a bot made and programmed by @ExplodeCode and I will only work when ExplodeCode turns me on')

    elif message.content.startswith('-calendar'):
        import calendar
        yy = 2023
        mm = 1
        print('')
        print(Fore.CYAN + '-----------------------------------')
        print(Fore.CYAN + 'calendar command used' + calendar.month(yy, mm))
        await message.channel.send(calendar.month(yy, mm))

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

    elif message.content.startswith("-math"):
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

    elif message.content.startswith("-echo"):
        print('')
        print('echo command used')
        # Get the message to echo from the command
        echo = message.content[6:]
        # Send the message to the channel
        await message.channel.send(echo)

    elif message.author not in users:
        users[message.author] = {"level": 1, "exp": 0}
    users[message.author]["exp"] += random.randint(5, 15)

    # Chec
    user = users[message.author]
    if user["exp"] >= 100:
        user["level"] += 1
        user["exp"] = 0
        await message.channel.send(f"{message.author.mention} has leveled up to level {user['level']}!")

    elif message.content == "-level":
        print('')
        print(Fore.MAGENTA + 'level command used')
        await message.channel.send(f"{message.author.mention} is level {user['level']} with {user['exp']} experience points. Well done :)")
    elif message.content == "-quote":
        print('')
        print('quote command used')
        # Select a random quote from the list
        quote = random.choice(quotes)
        # Send the quote to the channel
        await message.channel.send(quote)
        print(quote)

    elif message.content.startswith("-announce"):
        print('')
        print('announce command used')
        # Get the message to echo from the command
        echo = message.content[6:]
        # Send the message to the channel
        await message.channel.send(echo)

# birthday!


async def check_birthday():
    await client.wait_until_ready()

    while not client.is_closed():
        now = datetime.datetime.now()
        curmonth = int(now.strftime("%m"))
        curday = int(now.strftime("%d"))
        curhour = now.strftime("%H")
        curmin = now.strftime("%M")

        if int(curhour) == 20:
            print(
                f"Process 'check_birthday' ran command at {curhour}:{curmin}")
            with open("birthdays.json") as file:
                data = json.load(file)
                for servers, users in data.items():
                    print(servers)
                    for user in users:
                        print(user)
                        month = data[servers][user]['month']
                        day = data[servers][user]['day']
                        if month == curmonth and day == curday:
                            channel_id = data[servers]['announce']['id']
                            bb_channel = client.get_channel(channel_id)
                            await bb_channel.send(f"It's <@{user}>'s birthday today!")
            print('Birthday checked!')
            await asyncio.sleep(864390)  # task runs every day
        else:
            print(
                f"Process 'check_birthday' ran command at {curhour}:{curmin}")
            # wait for an hour before checking again 'if int(curhour)' again
            await asyncio.sleep(3600)


client.loop.create_task(check_birthday())
# await asyncio.sleep(86400) # task runs every day


@client.event
async def birthday_msg(msg):
    msgsender = msg.author.id
    server_id = msg.guild.id
    if msg.content.startswith('whenbd'):
        with open("birthdays.json") as file:
            data = json.load(file)
            try:
                sender = data[str(server_id)][str(msgsender)]
                month = sender['month']
                day = sender['day']
                await msg.channel.send(f"<@{msgsender}>'s birthday is on {month}/{day}")
            except KeyError:
                await msg.channel.send("ID doesn't exist")
            file.close()

        if msg.content.startswith('+whenbd'):
            # print(msg.author)
            liszt = msg.content.split()
            with open("birthdays.json") as file:
                try:
                    if liszt[1] is not None:
                        try:
                            msgsender = msg.mentions[0].id
                            try:
                                if msg.mentions[1] is not None:
                                    await msg.channel.send(f'<@{msg.author.id}>, you can only @ping 1 person at a time!')
                                    return
                            except IndexError:
                                pass
                        except IndexError:
                            await msg.channel.send('`Exception error occurred, Server member not found.`'
                                                   '\nPlease enter valid @username.')
                            return
                except IndexError:
                    msgsender = msg.author.id
                data = json.load(file)
                try:
                    sender = data[str(server_id)][str(msgsender)]
                    month = sender['month']
                    day = sender['day']
                    await msg.channel.send(f"<@{msgsender}>'s birthday is on {month}/{day}")
                except KeyError:
                    await msg.channel.send("Member doesn't exist in database. They haven't set their birthday yet.")
                file.close()

    if msg.content.startswith('+setbbchannel'):
        await msg.channel.send('`setting...`')
        channel_id = msg.channel.id

        with open("birthdays.json", "r+") as file:
            data = json.load(file)
            srvid = str(server_id)
            if srvid not in data:
                data[srvid] = {}
            data[srvid]['announce'] = {"id": channel_id, "month": 0, "day": 0}
            file.close()
            file = open("birthdays.json", "w")
            json.dump(data, file)
            await msg.channel.send(f'Successfully set **#{msg.channel.name}** as announcement channel.')

    if msg.content.startswith('+bbset'):
        await msg.channel.send('`setting...`')

        try:
            liszt = msg.content.split()
            date = liszt[1].split('/')
            month = int(date[0])
            day = int(date[1])

            if month > 13 or month < 1:
                await msg.channel.send(f"`Exception error occurred.`")
                await msg.channel.send('Correct usage is: bbset mm/dd {@another_person}')
                return
            else:
                pass
            if month in (1, 3, 5, 7, 8, 10, 12):
                if day > 31 or day < 1:
                    await msg.channel.send(f"`Exception error occurred.`")
                    await msg.channel.send('Correct usage is: bbset mm/dd {@another_person}')
                    return
                else:
                    pass
            elif month in (4, 6, 9, 11):
                if day > 30 or day < 1:
                    await msg.channel.send(f"`Exception error occurred.`")
                    await msg.channel.send('Correct usage is: bbset mm/dd {@another_person}')
                    return
                else:
                    pass
            elif month == 2:
                if day > 29 or day < 1:
                    await msg.channel.send(f"`Exception error occurred.`")
                    await msg.channel.send('Correct usage is: bbset mm/dd {@another_person}')
                    return
                else:
                    pass
            else:
                await msg.channel.send(f"`Exception error occurred.`")
                await msg.channel.send('Correct usage is: bbset mm/dd {@another_person}')
                return
        except:
            await msg.channel.send(f"`Exception error occurred.`")
            await msg.channel.send('Correct usage is: bbset mm/dd {@another_person}')
            return

        with open("birthdays.json", "r+") as file:
            data = json.load(file)
            srvid = str(server_id)
            if srvid not in data:
                data[srvid] = {}
            try:
                if liszt[2] is not None:
                    try:
                        msgsender = msg.mentions[0].id
                        try:
                            if msg.mentions[1] is not None:
                                await msg.channel.send(f'<@{msg.author.id}>, you can only @ping 1 person at a time!')
                                return
                        except IndexError:
                            pass
                    except IndexError:
                        await msg.channel.send('`Exception error occurred, Server member not found.`'
                                               '\nPlease enter valid @username.')
                        return
                    data[srvid][str(msgsender)] = {"month": month, "day": day}
            except IndexError:
                msgsender = msg.author.id
                data[srvid][str(msgsender)] = {"month": month, "day": day}
            file.close()
            file = open("birthdays.json", "w")
            json.dump(data, file)
            await msg.channel.send(f"`Success!`\nBirthday was set on **{month}/{day}** for <@{msgsender}>.")

            if msg.content.startswith('+help'):
                await msg.channel.send('`( {} = optional )`\n'
                                       '`+bbset mm/dd {@another_person}` - to set your birthday\n'
                                       '`+setbbchannel` - to set channel as birthday announcements channel\n'
                                       '`+whenbd {@another_person}` - to view your registered birth date\n')
client.run('ADD_YOUR_TOKEN_HERE')
