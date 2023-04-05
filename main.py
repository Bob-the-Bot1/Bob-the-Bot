import math
import discord
from discord.ext import commands
from discord import Embed
import datetime
import setting
import calendar
import asyncio
import colorama
import humanfriendly
import time
#import aiosqlite
import sqlite3
# import logging
from discord.ui import *
import colorsys
import setup_channels
import cases
import json
from time import mktime as mkt
from discord.ext import tasks
from itertools import cycle
import level_rewards
import requests
import configs
import random
import warningsget
from discord.ext import tasks

leveling_db = sqlite3.connect("expData.db")
leveling_cursor = leveling_db.cursor()






@tasks.loop(seconds=5.0)
async def updateit():
    await update_status()








#bot = discord.Bot(intents = discord.Intents.all())
bot = commands.Bot(command_prefix=commands.when_mentioned_or("b?"), intents=discord.Intents.all(), case_insensitive = True)

client = bot
level_multiplier = 5

@bot.event
async def on_guild_join(guild:discord.Guild):
    setup_channels.check_whether_if(guild.id)
    level_rewards.check_whether_if(guild.id)
    print(f"Joined {guild.name}, {guild.member_count} members")



@bot.event
async def on_ready():
  # await botdb()
  leveling_cursor.execute('''CREATE TABLE IF NOT EXISTS users
             (server_id INTEGER, user_id INTEGER, xp INTEGER, level INTEGER, PRIMARY KEY (server_id, user_id))''')
  leveling_db.commit()
  for guild in bot.guilds:
     setup_channels.check_whether_if(guild.id)
     level_rewards.check_whether_if(guild.id)
  updateit.start()
  print(colorama.Fore.BLUE+f"We have logged into {client.user}!")
  print(colorama.Fore.RED+'We have logged in as {0.user}'.format(bot))
  print(colorama.Fore.YELLOW)






async def update_status():
    servers = len(client.guilds)
    users = len(set(client.get_all_members()))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{servers} servers | {users} users"))




@bot.event
async def on_message(message:discord.Message):
    # await bot.process_application_commands(message)
    # await bot.process_commands(message)
    
    guild = message.guild
    if message.guild is not None:
        xd = level_rewards.get_enabled(guild.id)
        if xd is True:
          if not message.author.bot:
              # Get the user's data from the database or create a new row if the user is new
              leveling_cursor.execute('SELECT * FROM users WHERE server_id=? AND user_id=?', (message.guild.id, message.author.id))
              user_data = leveling_cursor.fetchone()
              if user_data is None:
                  user_data = (message.guild.id, message.author.id, 0, 0)
                  leveling_cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', user_data)
                  leveling_db.commit()

              # Calculate the XP to be earned for this message
              xp_earned = len(message.content) // 10 + 1
              channel_id = setup_channels.get_channel_id(message.guild, "levelup")
              channel_id = channel_id or message.channel.id
              channel = message.guild.get_channel(channel_id)
              # Update the user's data in the database with the earned XP and check for level up
              leveling_cursor.execute('UPDATE users SET xp=xp+? WHERE server_id=? AND user_id=?', (xp_earned, message.guild.id, message.author.id))
              leveling_db.commit()
              user_data = leveling_cursor.execute('SELECT * FROM users WHERE server_id=? AND user_id=?', (message.guild.id, message.author.id)).fetchone()
              xp, level = user_data[2], user_data[3]
              xp_needed = 5 * (level ** 2) + 50 * level + 100
              if xp >= xp_needed:
                  leveling_cursor.execute('UPDATE users SET level=level+1 WHERE server_id=? AND user_id=?', (message.guild.id, message.author.id))
                  leveling_db.commit()
                  await channel.send(f"{message.author.mention}", embed=configs.levelup(message.author, level+1))
                  xd = level_rewards.get_one_role(message.guild.id, int(level+1))
                  if xd is not None:
                     role = message.guild.get_role(xd)
                     await message.author.add_roles(role)
                  else:return

            	    
          else:
            return

        else:
           return
    else:
       return






@client.event
async def on_member_ban(gld:discord.Guild, usr:discord.User):
    await asyncio.sleep(0.5) # wait for audit log
    found_entry = None
    async for entry in gld.audit_logs(limit = 50, action = discord.AuditLogAction.ban, after = datetime.datetime.utcnow() - datetime.timedelta(seconds = 15), oldest_first = False):
        if entry.target.id == usr.id:
            found_entry = entry
            break
    if not found_entry:
        return
    await post_modlog(guild = gld, type = "BAN", user = found_entry.user, target = usr, reason = found_entry.reason)
@client.event
async def on_member_unban(gld, usr):
    await asyncio.sleep(0.5) # wait for audit log
    found_entry = None
    async for entry in gld.audit_logs(limit = 50, action = discord.AuditLogAction.unban, after = datetime.datetime.utcnow() - datetime.timedelta(seconds = 15), oldest_first = False):
        if entry.target.id == usr.id:
            found_entry = entry
            break
    if not found_entry:
        return
    await post_modlog(guild = gld, type = "UNBAN", user = found_entry.user, target = usr, reason = found_entry.reason)

@client.event
async def on_member_join(user:discord.User):
  date_format = "%d %b, %Y"
  type = "JOIN"
  mod_log_channel = user.guild.get_channel(setup_channels.get_channel_id(user.guild, "logging"))
  if setting.get_value(user.guild.id, "raid_mode") is True:
    await user.ban(reason = "Raid mode was active")
    e = discord.Embed(color = configs.MODLOG_COLORS[type], timestamp = datetime.datetime.utcnow())
    e.set_author(name = f"{type.capitalize()} | User {user.name}")
    e.add_field(name = "Registered on", value = f"{user.created_at.strftime(date_format)}", inline = True)
    e.add_field(name = "Joined", value = f"{user.joined_at.strftime(date_format)}", inline = True)
    ea = Embed(color=configs.MODLOG_COLORS["KICK"], title=f"{user} was banned", description="User was banned due to raid mode was active")
    await mod_log_channel.send(embeds = [e, ea])
  else:
    if not mod_log_channel:
      return
    e = discord.Embed(color = configs.MODLOG_COLORS[type], timestamp = datetime.datetime.utcnow())
    e.set_author(name = f"{type.capitalize()} | User {user.name}")
    e.add_field(name = "Registered on", value = f"{user.created_at.strftime(date_format)}", inline = True)
    e.add_field(name = "Joined", value = f"{user.joined_at.strftime(date_format)}", inline = True)
    await mod_log_channel.send(embed = e)
@client.event
async def on_member_remove(usr:discord.User):
    await asyncio.sleep(0.5) # wait for audit log
    found_entry = None
    async for entry in usr.guild.audit_logs(limit = 50, action = discord.AuditLogAction.kick, after = datetime.datetime.utcnow() - datetime.timedelta(seconds = 10), oldest_first = False): # 10 to prevent join-kick-join-leave false-positives
        if entry.target.id == usr.id:
            found_entry = entry
            break
        if not found_entry:
          return
    await post_modlog(guild = usr.guild, type = "KICK", user = found_entry.user, target = usr, reason = found_entry.reason)
@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
  if before.roles == after.roles:
    return
  mod_log_id = setup_channels.get_channel_id(before.guild, "logging")
  mod_log = before.guild.get_channel(mod_log_id)
  if before.roles != after.roles:
    embed = discord.Embed(title="ROLE(S) UPDATED", timestamp=datetime.datetime.utcnow())
    if len(before.roles) < len(after.roles):
      for updated_roles in after.roles:
        if updated_roles not in before.roles:
          rolementions = [updated_roles.mention]
          rolementions.reverse()
          role_string = ' '.join(rolementions)
      embed.add_field(name=f"These roles were added to {after}", value=role_string, inline=False)
      embed.color = configs.MODLOG_COLORS["MUTE"]
    if len(before.roles) > len(after.roles):
      for updated_roles in before.roles:
        if updated_roles not in after.roles:
          rolementions = [updated_roles.mention]
          rolementions.reverse()
          role_string = ' '.join(rolementions)
      embed.add_field(name=f"These roles were removed from {after}", value=role_string, inline=False)
      embed.color = configs.MODLOG_COLORS["UNMUTE"]
    await mod_log.send(embed=embed)
  if before.nick == after.nick:
    return
  if before.nick != after.nick:
    embed = Embed(title=f"Nickname changed! of {after.display_name}", timestamp=datetime.datetime.utcnow(), color=configs.MODLOG_COLORS["ROLES_CHANGED"])
    embed.add_field(name="BEFORE NAME", value=before.nick, inline=False)
    embed.add_field(name="AFTER NAME", value=after.nick, inline=False)
    await mod_log.send(embed=embed)

async def post_modlog(guild:discord.Guild, type, user:discord.User, target:discord.User, reason=None, duration=None, roles_given:commands.Greedy[discord.Role] = None):
    x = cases.add_case(target.id, type, reason, user.id, datetime.datetime.utcnow(), guild)
    await log_case2(guild, (x, target.id, type, reason, user.id, datetime.datetime.utcnow()))
  



    
@bot.event
async def on_command_error(context, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await context.send("Oh no! Looks like you have missed out an argument for this command.")
  elif isinstance(error, commands.MissingPermissions):
    await context.send("Oh no! Looks like you Dont have the permissions for this command.")
  elif isinstance(error, commands.MissingRole):
    await context.send("Oh no! Looks like you Dont have the roles for this command.") #bot errors
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


@bot.slash_command(name="raid_mode", description="Toggles raid mode on or off")
@commands.has_permissions(administrator=True)
async def raid_mode(ctx:discord.Interaction):
    value = setting.get_value(ctx.guild.id, "raid_mode")
    if value is None or False:
        setting.set_value(ctx.guild.id, "raid_mode", True)
        await ctx.response.send_message("Successfully set raid mode to True")
    else:
      setting.set_value(ctx.guild.id, "raid_mode", False)
      await ctx.response.send_message("Successfully set raid mode to False")

@bot.slash_command(name="set_logging_channel", description="Sets a logging channel")
@commands.has_permissions(administrator = True)
async def set_logging_channel(ctx:discord.Interaction, channel:discord.TextChannel):
  
  await ctx.response.send_message("Success", ephemeral=True)
  setup_channels.set_channel_id(ctx.guild.id, "logging", channel.id)

@bot.slash_command(name="set_welcome_channel", description="Sets a welcome channel")
@commands.has_permissions(administrator = True)
async def set_welcome_channel(ctx:discord.Interaction, channel:discord.TextChannel):
  
  await ctx.response.send_message("Success", ephemeral=True)
  setup_channels.set_channel_id(ctx.guild.id, "welcome", channel.id)

@bot.slash_command(name="set_levelup_channel", description="Sets a levelup channel")
@commands.has_permissions(administrator = True)
async def set_logging_channel(ctx:discord.Interaction, channel:discord.TextChannel):
  
  await ctx.response.send_message("Success", ephemeral=True)
  setup_channels.set_channel_id(ctx.guild.id, "levelup", channel.id)

@bot.slash_command(name="get_channels", description="Get all the channels set")
@commands.has_permissions(administrator = True)
async def get_channels(ctx:discord.Interaction):
  await ctx.response.defer(ephemeral=True)
  await asyncio.sleep(5)
  logging = setup_channels.get_channel_id(ctx.guild, "logging")
  welcome = setup_channels.get_channel_id(ctx.guild, "welcome")
  levelup = setup_channels.get_channel_id(ctx.guild, "levelup")
  embed = Embed(title="Channels of this server", color=0xfe156d)
  embed.add_field(name="Welcome channel", value=f"<#{welcome}>")
  embed.add_field(name="Levels channel", value=f"<#{levelup}>")
  embed.add_field(name="Logging channel", value=f"<#{logging}>")
  await ctx.followup.send(embed=embed, ephemeral=True)
  # await ctx.user.

@bot.slash_command(name='nick', description="Change any member's nickname")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(manage_nicknames = True)
async def nick(ctx : discord.Interaction, member: discord.Member = None, *, arg:str = None):
  # modlog = discord.utils.get(ctx.guild.text_channels, name=configs.MOD_LOG_CHANNEL_NAME)
  
#   x = case_id()
  if member is None:
    member = ctx.user
  await member.edit(nick=arg)
  e = discord.Embed(title=f"Successfully changed name",  color=configs.MODLOG_COLORS["BAN"])
  if arg is None:
    e.description=f"Successfully reset {member.mention}'s nickname for this server."
  else:
    e.description=f"Successfully changed {member.mention} nickname to ***{arg}***"
  await ctx.response.send_message(embed=e)
  await post_modlog(ctx.guild, "NICKNAME CHANGE", ctx.user, member, f"Nickname changed of {member.mention} to {arg}", None, None)
  # await modlog.send(embed = e)
      

@client.slash_command(
    name="math", description="Solve a math problem"
)
async def calc(interaction:discord.Interaction, problem: str):
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

@bot.slash_command(name='ping', with_app_command=True, description="Get the latency of the bot.")
async def ping(ctx : discord.Interaction):
    bot_latency = round(bot.latency * 1000)
    conf_embed = Embed(title='Pong!!', description=f"**Bot latency is** `{bot_latency}` ***ms*** *.*", color=0x9b59b6)
    await ctx.response.send_message(embed = conf_embed)

@bot.slash_command(name="kick", with_app_command=True, description="Kick any of your member!")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(kick_members = True)
async def kick(ctx : discord.Interaction, member: discord.Member, *, reason='No reason was provided'):
    if not member: 
        return await ctx.response.send_message(f'{ctx.user.mention}, !!!!! :warning: ***No user was specified to kick or you may have forgot to mention one, Please do it again.***')
    elif member is ctx.user:
      return await ctx.response.send_message(f'{ctx.user.mention}, :warning: ***You cannot kick yourself***')
    elif member.guild_permissions.administrator:
      await ctx.response.send_message(f'{ctx.user.mention}, :warning: ***You cannot kick an admin. It can only done by the owner.***')
      await ctx.response.send_message(':person_facepalming:')
    else:
      try:
        # x = case_id()
        conf_embed = Embed(color=configs.MODLOG_COLORS["KICK"], title="User was Kicked", description=f"{member.mention} was kicked for reason: {reason} by {ctx.user.mention}")
        conf_embed2 = Embed(color=configs.MODLOG_COLORS["KICK"], title=f"User was Kicked", description=f"{member.mention} was kicked for reason: {reason} by {ctx.user.mention}")
        user_embed = Embed(color=configs.MODLOG_COLORS["KICK"], title='You were kicked', description=f'You were kicked in **{ctx.guild.name}** by Moderator {ctx.user.mention} for reason: {reason}')
        await member.send(embed=user_embed)
        await member.kick(reason=reason)
        await ctx.response.send_message(embed=conf_embed)
        # await ctx.guild.get_channel(setup_channels.get_channel_id(ctx.guild, "logging")).send(embed=conf_embed2)
        case_id = cases.add_case(member.id, "kick", reason, ctx.user.id, datetime.datetime.utcnow(), ctx.guild.id)
        await log_case(ctx, (case_id, member.id, "kick", reason, ctx.user.id, datetime.datetime.utcnow()))
      except discord.Forbidden:
        pass
#   else:
#     await ctx.response.send_message(f"{ctx.user.mention} **Error: ** Bans/Kicks is disabled in this server. Please ask anyone who has admin permissions to do the action is case of emergency!")


@client.slash_command(
    name="8ball",
    description="Ask the magic 8-ball a question."
)
async def ball(interaction:discord.Interaction, query: str):
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
    await interaction.response.send_message(f"Question: {question}\nAnswer: {response}")

@bot.slash_command(name="warn", description = "Warns a user provided!")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(moderate_members=True)
async def warn(ctx:discord.Interaction, member:discord.Member,*, reason:str = "No reason was provided"):
  if member.id == ctx.user.id:
    await ctx.response.send_message(f"{ctx.user.mention} You cannot warn your self")
  elif member.guild_permissions.administrator:
    await ctx.response.send_message(f"{ctx.user.mention} You cannot warn an adminstrator!")
  else:
    warn_code = f'{ctx.guild.id}-{member.id}-{len(warningsget.get_warnings(ctx.guild.id, member.id)) + 1}'
    
    cur = sqlite3.connect('warnings.db')
    conn = cur.cursor()
    # Store the warning in the database
    conn.execute("INSERT INTO warnings (server_id, user_id, warn_code, moderator_id, reason) VALUES (?, ?, ?, ?, ?)", 
                 (ctx.guild.id, member.id, warn_code, ctx.user.id, reason))
    
    cur.commit()

    warnings = warningsget.get_warnings(ctx.guild.id, member.id)
    if len(warnings) <= 0:
       first_warning = True
    else:
       first_warning = False

    count = len(warnings)
    conf_embed = Embed(title='Warned a User', description=f"Gave `1` strike/warning to {member.mention}. They now have totally ***{count}*** {'warning' if first_warning else 'warnings'} for reason --> **{reason}**.", color=discord.Color.blue())
    user_embed = Embed(title='You were warned!', description=f"You were given a warning/strike in {ctx.guild.name} by {ctx.user.mention} for reason --> **{reason}**. You now totally have ***{count}*** {'warning' if first_warning else 'warnings'}.", color=discord.Color.blue())
    await ctx.response.send_message(embed=conf_embed)
    await member.send(embed=user_embed)
    # type = "WARN"
    # mod_log_channel = discord.utils.get(ctx.guild.text_channels, name = configs.MOD_LOG_CHANNEL_NAME)
    # if not mod_log_channel:
    #   return
    e = discord.Embed(color = 0xff0000, timestamp = datetime.datetime.utcnow())
    # x = case_id()
    e.set_author(name = f"WARN")
    e.add_field(name = "Target", value = f"<@{member.id}> ({member})", inline = True)
    e.add_field(name = "Moderator", value = f"<@{ctx.user.id}> ({ctx.user})", inline = True)
    e.add_field(name = "Reason", value = reason, inline = False)
    case_id = cases.add_case(member.id, "warn", reason, ctx.user.id, datetime.datetime.utcnow(), ctx.guild.id)
    await log_case(ctx, (case_id, member.id, "warn", reason, ctx.user.id, datetime.datetime.utcnow()))
    # await mod_log_channel.send(embed = e)
  
@bot.slash_command(name="warnings", description = "Get warns of user")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(kick_members=True)
async def warnings(ctx:discord.Interaction, member:discord.Member):
  warnings = warningsget.get_warnings(ctx.guild.id, member.id)
  embed = Embed(title=f"Warnings for {member}", timestamp=datetime.datetime.utcnow())
  embed.set_author(name=member, icon_url=member.avatar or ctx.guild.icon)
  if len(warnings) <= 0:
    await ctx.response.send_message(f"No warnings were found for {member.mention}.")
  else:
    for warning in warnings:
      embed.add_field(name=f"Case ID: {warning[2]}", value=f"Warning Given by: <@{warning[3]}> for reason: {warning[4]}", inline=False)
    await ctx.response.send_message(embed=embed)

@bot.slash_command(name="log_all", description = "Logs all cases in the log channel.")
@commands.has_permissions(administrator=True)
async def log_all(ctx:discord.Interaction):
    conn = sqlite3.connect('moderation_cases.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM moderation_cases WHERE guild = ?", (ctx.guild.id))
    data = cur.fetchall()
    channelid = setup_channels.get_channel_id(ctx.guild, "logging")
    channel = ctx.guild.get_channel(channelid)


@bot.slash_command(name="rmwarn", description = "Removes a warning of user with the code provided")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(administrator=True)
async def rmwarn(ctx : discord.Interaction ,*,id_of_warn):
  warning = warningsget.get_warning_by_code(ctx.guild.id, id_of_warn)
  db = sqlite3.connect("warnings.db")
  cur = db.cursor()
  cur.execute("DELETE FROM warnings WHERE server_id = ? AND warn_code = ?", (ctx.guild.id, id_of_warn))
  db.commit()
  user = ctx.guild.get_member(warning[1])
  embed = Embed(title=f"Warning deleted | Code: {id_of_warn} ", description=f"Warning given by <@{warning[3]}>, for Reason {warning[4]}. Warning was given to {user.mention}")
  mod = ctx.guild.get_member(warning[3])
  embed.set_author(name=user.display_name, icon_url=user.avatar or mod.avatar)
  embed.set_thumbnail(url=user.avatar)
  await ctx.response.send_message(embed=embed)
  await ctx.guild.get_channel(setup_channels.get_channel_id(ctx.guild, "logging")).send(embed=embed)

@bot.slash_command(name="time", description="Get your local time.")
# @app_commands.guilds(discord.Object(id=guild_id))
async def time(ctx : discord.Interaction):
  time_now = datetime.datetime.now()
  hours = time_now.hour
  year = time_now.year
  month = time_now.month
  minutes = time_now.minute
  days = time_now.day

  date_time = datetime.datetime(year, month, days)
  end_date = date_time + datetime.timedelta(hours=hours, minutes=minutes)
  date_tuple=(end_date.year, end_date.month, end_date.day, end_date.hour, end_date.minute, end_date.second)
  epochtime = mkt(datetime.datetime(*date_tuple).timetuple())
  stringtime = str(epochtime)
  timelst = []
  timelst.extend(stringtime)
  prepared = timelst[:10]
  strtime1 = ','.join(prepared)
  strtime2 = strtime1.replace(',',"")
  inttime = int(strtime2)
  await ctx.response.send_message(f"The current time is <t:{inttime}:F>")


@bot.slash_command(name="timeout", description="Timeout/Mute a member.")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(moderate_members=True)
async def timeout(ctx : discord.Interaction, user:discord.Member=None,*, time='2m',  reason="No reason was provided"):
  
  time2 = humanfriendly.parse_timespan(time)

  if user is None:
    await ctx.response.send_message(f'{ctx.user.mention}, !!!!! :warning: ***No user was specified to timeout or you may have forgot to mention one, Please do it again.***')
  elif user == ctx.user:
    await ctx.response.send_message(f'{ctx.user.mention}, :warning: ***You cannot timeout yourself***')
  elif user.guild_permissions.administrator:
    await ctx.response.send_message(f'{ctx.user.mention}, :warning: ***You cannot timeout an admin. It can only done by the owner.***')
    await ctx.response.send_message(':person_facepalming:')

  else:
    duration = discord.utils.utcnow() + datetime.timedelta(seconds=time2)
    await user.send(f'You were timed out in **{ctx.guild.name}** for reason:{reason} by mod: {ctx.user.mention}. Duration: {time}.')
    await user.timeout(duration, reason=reason)
    await ctx.response.send_message(f'**Timed out {user.mention} for {time} by mod: {ctx.user.mention} for reason:** \n*{reason}*.')
    # await post_modlog(guild=ctx.guild, type="TIMEOUT", user=ctx.user, target=user, reason=reason, duration=time)
    caseid = cases.add_case(user.id, "timeout", reason+"for"+time, ctx.user.id, datetime.datetime.utcnow(), ctx.guild.id)
    await log_case(ctx, (caseid, user.id, "timeout", reason+" ."+"Timed out "+"for "+time, ctx.user.id, datetime.datetime.utcnow()))

@bot.slash_command(name='purge', description='Clear no.of messages in a given channel')
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(manage_messages=True)
async def purge(ctx : discord.Interaction,amount : int = 2):
#   log_channel = discord.utils.get(ctx.guild.text_channels, name = configs.MOD_LOG_CHANNEL_NAME)
#   if not log_channel:
    # return
#   x = case_id()
  e = discord.Embed(title=f"Cleared messages", description=f"Cleared `{amount}` message(s) in <#{ctx.channel.id}> by Moderator {ctx.user.mention}")
  await ctx.channel.purge(limit=amount+1)
  await ctx.response.send_message(f"Deleted `{amount}` message(s) in channel <#{ctx.channel.id}> by  Moderator {ctx.user.mention}")
  #await log_channel.send(embed = e)
  log_Channel = ctx.guild.get_channel(setup_channels.get_channel_id(ctx.guild, "logging"))
  await log_Channel.send(embed=e)




@bot.slash_command(name='ban', description='Ban a member from the server')
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(ban_members=True)
async def ban( ctx : discord.Interaction, user:discord.Member=None, *, reason="No reason was provided"):
    if user is None:
      cmdusage = Embed(title='Ban', description='-> Command for Banning a User is `*ban`. \n -> Usage: `*ban @user [reason]`. \n **Note : ** ***You can user userIds, role IDs instead @ pinging.***')
      await ctx.response.send_message(embed=cmdusage)
      await ctx.response.send_message(f'{ctx.user.mention}, !!!!! :warning: ***No user was specified to ban or you may have forgot to mention one, Please do it again.***')
    elif user == ctx.message.author:
      await ctx.response.send_message(f'{ctx.user.mention}, :warning: ***You cannot ban yourself***')
    elif user.guild_permissions.administrator:
      await ctx.response.send_message(f'{ctx.user.mention}, :warning: ***You cannot ban an admin. It can only done by the owner.***')
      await ctx.response.send_message(':person_facepalming:')
    else:
      conf_embed = Embed(color=0xff0000, title="User was banned", description=f"{user.mention} was banned for reason: {reason} by {ctx.user.mention}")
      user_embed = Embed(color=0xff0000, title='You were banned', description=f'You were banned in **{ctx.guild.name}** by Moderator {ctx.user.mention} for reason: {reason}')
      await ctx.response.send_message(embed=conf_embed)
      if user.bot:
        return
      else:
        await user.send(embed=user_embed)
      await user.ban(reason=reason)
      # await post_modlog(guild = ctx.guild, type = "BAN", user = ctx.user, target = user, reason = reason)
      case_id = cases.add_case(user.id, "ban", reason, ctx.user.id, datetime.datetime.utcnow(), ctx.guild.id)
      await log_case(ctx, (case_id, user.id, "ban", reason, ctx.user.id, datetime.datetime.utcnow()))

  
@bot.slash_command(name="unban", description='UNban a user from the server.')
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(ban_members=True)
#@commands.guild_only()
async def unban(ctx:discord.Interaction, member: discord.User, *, reason="No reason was provided"):
  await ctx.guild.unban(member, reason=reason)
  await ctx.response.send_message(f'**{member.mention}** has been unbanned from the server by {ctx.user.mention} for reason: {reason}.')
  await post_modlog(guild = ctx.guild, type = "UNBAN", user = ctx.user, target = member, reason = reason)
  case_id = cases.add_case(member.id, "unban", reason, ctx.user.id, datetime.datetime.utcnow(), ctx.guild.id)
  await log_case(ctx, (case_id, member.id, "unban", reason, ctx.user.id, datetime.datetime.utcnow()))


@bot.slash_command(name='tempban', description = "Banning a member for a given period of time.")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(ban_members=True)
async def tempban(ctx:discord.Interaction, member: discord.User, duration: str = None, *, reason="No reason was provided"):
  time2 = humanfriendly.parse_timespan(duration)

  if duration is None:
    await ctx.response.send_message('What!, Tempban means banning someone for a period of time')
  else:
    time3 = datetime.datetime.utcnow() + datetime.timedelta(seconds=time2)
    await ctx.guild.ban(member)
    await ctx.response.send_message(f'{member} has been banned for {duration} for reason: {reason} by moderator: {ctx.user.mention}')
    # await post_modlog(guild = ctx.guild, type = "TEMPBAN", user = ctx.user, target = member, reason = reason, duration=duration)
    caseid = cases.add_case(member.id, "tempban", reason+" ."+"Timed out "+"for "+time, ctx.user.id, datetime.datetime.utcnow(), ctx.guild.id)
    await log_case(ctx, (caseid, member.id, "tempban", reason+" ."+"Timed out "+"for "+time, ctx.user.id, datetime.datetime.utcnow()))
    await asyncio.sleep(time3)
    await ctx.guild.unban(member)




@bot.slash_command(name='untimeout',description="remove timeout from a member")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx:discord.Interaction, member: discord.Member, *, reason="No reason was provided."):
  if member.is_timed_out():
    await member.timeout(datetime.timedelta(seconds=1))
    await ctx.response.send_message(f"Successfully removed {member.mention} 's timeout.")

  else:
    await ctx.response.send_message(f" {member.mention} isn't timed out.")

@client.slash_command(name="giverole", description="Gives a role to a member")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(manage_roles=True)
async def giverole(ctx:discord.Interaction, member: discord.Member, *, role: discord.Role):
  if role.position > ctx.user.top_role.position: #if the role is above users top role it sends error
    if member.id == ctx.user.id:
      name = "yourself"
    else:
      name = member.mention
    embed = Embed(title=f"Error", description=f":person_facepalming: That role which you wanna give to {name} is above your reach!! Please ask a higher moderator whose role is above than {role.mention} to do this action. Thank you :)")
    await ctx.reply(embed=embed)
  else:
    # case = case_id()
    conf_embed = Embed(title=f'Assigned a Role to a Member.', description=f'Assigned {role.mention} role to {member.mention}.', color=discord.Color.magenta())
    conf_embed.add_field(name="Moderator: ", value=f"{ctx.user.mention}", inline=False)
    conf_embed.add_field(name="Subject: ", value=f"{member.mention}", inline=False)
    conf_embed.set_author(name=f"{member.name}", icon_url=member.avatar)
    conf_embed.set_thumbnail(url=member.avatar)
    await member.add_roles(role, reason="No reason")
    await ctx.response.send_message(embed=conf_embed)
    modlog = ctx.guild.get_channel(setup_channels.get_channel_id(ctx.guild, "logging"))
    modlog = modlog or ctx.channel
    await modlog.send(embed=conf_embed)

@client.slash_command(name="removerole", description="Removes a role from a user")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(manage_roles=True)
async def removerole(ctx:discord.Interaction, member: discord.Member, *, role: discord.Role):
  if role.position > ctx.user.top_role.position: #if the role is above users top role it sends error
    if member.id == ctx.user.id:
      name = "yourself"
    else:
      name = member.mention
    embed = Embed(title=f"Error", description=f":person_facepalming: That role which you wanna remove from {name} is above your reach!! Please ask a higher moderator whose role is above than {role.mention} to do this action. Thank you :)")
    await ctx.reply(embed=embed)
  else:
    # case = case_id()
    conf_embed = Embed(title=f'Removed a Role from a Member.', description=f'Removed {role.mention} role from {member.mention}.', color=discord.Color.magenta())
    conf_embed.add_field(name="Moderator: ", value=f"{ctx.user.mention}", inline=False)
    conf_embed.add_field(name="Subject: ", value=f"{member.mention}", inline=False)
    conf_embed.set_author(name=f"{member.name}", icon_url=member.avatar)
    conf_embed.set_thumbnail(url=member.avatar)
    await ctx.response.send_message(f'Removing **{role}** role from {member.mention}')
    await member.remove_roles(role)
    await ctx.followup.send(embed=conf_embed)
    modlog = ctx.guild.get_channel(setup_channels.get_channel_id(ctx.guild, "logging"))
    modlog = modlog or ctx.channel
    await modlog.send(embed=conf_embed)



@bot.slash_command(name = "test", description = "Testing")
# @app_commands.guilds(discord.Object(id = guild_id))
@commands.has_permissions(administrator = True)
async def test(ctx: discord.Interaction):
    await ctx.response.send_message("hi", ephemeral=True)



@bot.slash_command(name='info',description="Gives the information about bot.")
# @app_commands.guilds(discord.Object(id=guild_id))
async def info(ctx:discord.Interaction):
  e = Embed(title="Information About me.", timestamp=datetime.datetime.utcnow(), color=0xffffff)
  e.add_field(name="Creators: ", value="Coder_DO_As_Impossible#1237 -> <@774332691008061502> \n csdaniel#9326 -> <@1075087931980652544> \n ExplodeCode#2008 -> <@896814282317131848> \n Kyro#2945 -> <@811771148613189652>", inline=False)
  date_format = "%d %b, %Y"
  e.add_field(name="Created at: ", value=f"{bot.user.created_at.strftime(date_format)}", inline=False)
  
  e.set_author(name=str(bot.user.name), icon_url=bot.user.avatar)
  e.set_thumbnail(url=bot.user.avatar)
  await ctx.response.send_message(embed=e)


@client.slash_command(
    name="calendar", description="View the calendar"
)
async def cal(interaction:discord.Interaction):
    yy = datetime.datetime.now().year
    mm = datetime.datetime.now().month
    await interaction.respond(calendar.month(yy, mm))

@bot.slash_command(name="lock", with_app_command=True, description="Locks a channel")
# @app_commands.guilds(discord.Object(id=guild_id))
@commands.has_permissions(manage_channels=True)
async def lock(ctx,time:str=None, role:discord.Role=None, channel: discord.TextChannel=None):
  modlog = ctx.guild.get_channel(setup_channels.get_channel_id(ctx.guild, "logging"))
  role = role or ctx.guild.default_role
  channel = channel or ctx.channel
  # count = case_id()
  embed=discord.Embed(title=f"Locked a channel", timestamp=datetime.datetime.utcnow(), color=configs.MODLOG_COLORS["KICK"])
  timetext = f"for time {time}"
  embed.add_field(name=f"Locked channel {channel.name} for {role.name} ",value=f"Locked channel <#{channel.id}> for {role.name}", inline=False)
  await ctx.response.send_message("Done!!")
  if time:
    time2 = humanfriendly.parse_timespan(time)
    time3 = datetime.datetime.utcnow() + datetime.timedelta(seconds=time2)
    embed.add_field(name="For time", value=f"{timetext}")
    await channel.send(embed=embed)
    modlog = modlog or ctx.channel
    await modlog.send(embed=embed)
    overwrite = channel.overwrites_for(role)
    overwrite.send_messages = False
    asyncio.sleep(time3)
    overwrite = channel.overwrites_for(role)
    overwrite.send_messages = True
    await channel.set_permissions(role, overwrite=overwrite)
    # x = case_id()
    unlock_embed = discord.Embed(title= (f"UNLOCKED"),description= (f"**{channel.mention}** HAS BEEN UNLOCKED FOR **{role}**"),colour=0x00FFF5,)        
    unlock_embed.set_footer(text=ctx.user.name, icon_url=ctx.user.avatar)
    unlock_embed.set_author(name=client.user.name, icon_url=client.user.avatar)
    unlock_embed.set_thumbnail(url=ctx.guild.icon)
    await ctx.response.send_message(embed=unlock_embed, delete_after = 60) 
    modlog = modlog or ctx.channel
    await modlog.send(embed=unlock_embed) 
  else:
    pass
  await channel.send(embed=embed)
  modlog = modlog or ctx.channel
  await modlog.send(embed=embed)
  overwrite = channel.overwrites_for(role)
  overwrite.send_messages = False
  await channel.set_permissions(role, overwrite=overwrite)




@bot.slash_command(name="rank", description="Gives user rank")
async def rank(ctx:discord.Interaction, member: discord.Member=None):
    # await ctx.response.send_message("Done", ephemeral=True)
    member = member or ctx.user
    await ctx.response.defer()
    # get user exp
    leveling_cursor.execute('SELECT * FROM users WHERE server_id=? ORDER BY xp DESC', (ctx.guild.id,))
    user_data = leveling_cursor.fetchall()
    if len(user_data) == 0:
        await ctx.followup.send(f'No one on this server has earned any XP yet!')
    else:
        level_variables = {"xp": 0, "level": 0}
        rank = 1
        for data in user_data:
            if data[1] == member.id:
                level_variables["xp"] = data[2]
                level_variables["level"] = data[3]
                break
            rank += 1
        xp_needed = 5 * (level_variables["level"] ** 2) + 50 * level_variables["level"] + 100
        xp_needed_next_level = 5 * ((level_variables["level"]+1) ** 2) + 50 * (level_variables["level"]+1) + 100
        xp_needed_current_level = xp_needed_next_level - xp_needed
        xp_percentage = round(((xp_needed - level_variables["xp"]) / xp_needed_current_level)*100)
        xp = level_variables["xp"]
        embed = discord.Embed(title=f"Stats for {member.name}", colour=discord.Colour.gold())
        embed.add_field(name="Level", value=str(level_variables["level"]))
        embed.add_field(name="Exp", value=f"{xp}/{xp_needed}")
        embed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}")
        # embed.add_field(name="Level Progress", value=f"{xp_percentage}%")

        # await ctx.send(embed=embed)
        embed.set_author(name=member, icon_url=member.avatar)
        embed.set_thumbnail(url=member.avatar)

        await ctx.followup.send(embed=embed)






@bot.slash_command(
    name="bored",
    description="Generates a random activity to do when feeling bored.",
)
async def bored(interaction:discord.Interaction):
    response = requests.get("https://www.boredapi.com/api/activity")
    json_data = json.loads(response.text)
    activity = json_data["activity"]
    await interaction.response.send_message(f"Why not try to: {activity}")


client.slash_command(
    name="announce",
    description="Make an announcement."
)
async def announce(interaction:discord.Interaction, *, message: str):
    await interaction.response.send_message(message)


@client.slash_command(
    name="quote", description="Get a random quote."
)
async def quote(interaction:discord.Interaction):
    response = requests.get("https://quotable.io/random")
    json_data = json.loads(response.text)
    content = json_data["content"]
    author = json_data["author"]
    embed = discord.Embed(title="Quote", description=content, color=0x00FF33)
    embed.set_footer(text=author)
    await interaction.response.send_message(embed=embed)


@client.slash_command(name="hello", description="Say hi!")
async def hello(interaction:discord.Interaction):
    greetings = ["Hello", "Hi", "Greetings", "Hola", "Bonjour", "Konnichiwa", "Namaste", "Aaram Ri"]
    username = interaction.user.name
    await interaction.response.send_message(f"{random.choice(greetings)} {username}!")




@client.slash_command(
    name="search", description="Search the internet."
)
async def search(interaction:discord.Interaction, query: str, engine: str):
    engine.lower()
    print(engine)  # Choice(name='Google', value='google')
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
    elif engine == "youtube":
      await interaction.response.send_message(f"https://www.youtube.com/results?search_query={query}")
    else:
        await interaction.response.send_message("Invalid engine.")







@client.slash_command(name="wouldyourather", description="Generate a Would You Rather question.")
async def wouldyourather(interaction:discord.Interaction):
    questions = ["Would you rather live without internet for a week or without phone?",
                 "Would you rather have the power to be invisible or to read minds?",
                 "Would you rather have a pet dragon or a pet unicorn?",
                 "Would you rather travel to the past or the future?",
                 "Would you rather be a famous athlete or a famous musician?",
                 "Would you rather have the power of flight or the power of telekinesis?",
                 "Would you rather knowing how to code anything or know how to design anything?",
                 "Would you rather having an AI crush or being an AI?",
                 "Would you rather drinking your favourite food as a liquid or eating your favourite drink as a food?",
                 "Would you rather being lonely or being over popular?",
                 "Would you rather being a famous TikToker or famous YouTuber?",
                 "Would you rather eat a bug or a fly?",
                 "Would you rather lick the floor or a broom?",
                 "Would you rather eat ice cream or cake?",
                 "Would you rather clean a toliet or a babys diaper",
                 "Would you rather lick your keyboard or mouse?",
                 "Would you rather wash your hair with mash potatoes or cranberry sauce?",
                 "Would you rather team up with Wonder Woman or Captain Marvel?",
                 "Would you rather want to find true love or win lottery next month?",
                 "Would you rather be forced to sing along or dance to every song you hear?",
                 " Would you rather have everyone you know be able to read your thoughts or for everyone you know to have access to your Internet history?",
                 "Would you rather be chronically under-dressed or overdressed?",
                 "Would you rather lose your sight or your memories?",
                 "Would you rather have universal respect or unlimited power?",
                 "Would you rather give up air conditioning and heating for the rest of your life or give up the Internet for the rest of your life?",
                 "Would you rather swim in a pool full of Nutella or a pool full of maple syrup?","Would you rather labor under a hot sun or extreme cold?",
                 "Would you rather stay in during a snow day or build a fort?","Would you rather buy 10 things you don’t need every time you go shopping or always forget the one thing that you need when you go to the store?",
                 "Would you rather never be able to go out during the day or never be able to go out at night?",
                 "Would you rather have a personal maid or a personal chef?",
                 "Would you rather have beyoncé’s talent or Jay-Z‘s business acumen?",
                 "Would you rather be an extra in an Oscar-winning movie or the lead in a box office bomb?",
                 "Would you rather vomit on your hero or have your hero vomit on you?",
                 "Would you rather communicate only in emoji or never be able to text at all ever again?",
                 "Would you rather be royalty 1,000 years ago or an average person today?",
                 "Would you rather lounge by the pool or on the beach?",
                 "Would you rather wear the same socks for a month or the same underwear for a week?",
                 "Would you rather work an overtime shift with your annoying boss or spend full day with your mother-in-law?",
                 "Would you rather cuddle a koala or pal around with a panda?",
                 "Would you rather have a sing-off with Ariana Grande or a dance-off with Rihanna?",
                 "Would you rather watch nothing but Hallmark Christmas movies or nothing but horror movies?",
                 "Would you rather always be 10 minutes late or always be 20 minutes early?",
                 "Would you rather have a pause or a rewind button in your life?",
                 "Would you rather lose all your teeth or lose a day of your life every time you kissed someone?",
                 "Would you rather drink from a toilet or pee in a litter box?",
                 "Would you rather be forced to live the same day over and over again for a full year, or take 3 years off the end of your life?",
                 "Would you rather never eat watermelon ever again or be forced to eat watermelon with every meal?",
                 "Would you rather go to Harvard but graduate and be jobless, or graduate from another college and work for Harvard",
                 "Would you rather the aliens that make first contact be robotic or organic?",
                 "Would you rather lose the ability to read or lose the ability to speak?",
                 "Would you rather have a golden voice or a silver tongue?",
                 "Would you rather be covered in fur or covered in scales?",
                 "Would you rather be in jail for a year or lose a year off your life?",
                 "Would you rather have one real get out of jail free card or a key that opens any door?",
                 "Would you rather know the history of every object you touched or be able to talk to animals?",
                 "Would you rather be married to a 10 with a bad personality or a 6 with an amazing personality?",
                 "Would you rather be able to talk to land animals, animals that fly, or animals that live under the water?",
                 "Would you rather have all traffic lights you approach be green or never have to stand in line again?",
                 "Would you rather spend the rest of your life with a sailboat as your home or an RV as your home?",
                 "Would you rather marry someone pretty but stupid or clever but ugly?",
                 "Would you rather give up all drinks except for water or give up eating anything that was cooked in an oven?",
                 "Would you rather be able to see 10 minutes into your own future or 10 minutes into the future of anyone but yourself?",
                 "Would you rather have to fart loudly every time you have a serious conversation or have to burp after every kiss?",
                 "Would you rather become twice as strong when both of your fingers are stuck in your ears or crawl twice as fast as you can run?",
                 "Would you rather have everything you draw become real but be permanently terrible at drawing or be able to fly but only as fast as you can walk?",
                 "Would you rather thirty butterflies instantly appear from nowhere every time you sneeze or one very angry squirrel appear from nowhere every time you cough?",
                 "Would you rather vomit uncontrollably for one minute every time you hear the happy birthday song or get a headache that lasts for the rest of the day every time you see a bird (including in pictures or a video)?",
                 "Would you rather eat a sandwich made from 4 ingredients in your fridge chosen at random or eat a sandwich made by a group of your friends from 4 ingredients in your fridge?",
                 "Would you rather everyone be required to wear identical silver jumpsuits or any time two people meet and are wearing an identical article of clothing they must fight to the death?",
                 "Would you rather have to read aloud every word you read or sing everything you say out loud?",
                 "Would you rather wear a wedding dress/tuxedo every single day or wear a bathing suit every single day?",
                 "Would you rather be unable to move your body every time it rains or not be able to stop moving while the sun is out?",
                 "Would you rather have all dogs try to attack you when they see you or all birds try to attack you when they see you?",
                 "Would you rather be compelled to high five everyone you meet or be compelled to give wedgies to anyone in a green shirt?",
                 "Would you rather have skin that changes color based on your emotions or tattoos appear all over your body depicting what you did yesterday?",
                 "Would you rather randomly time travel +/- 20 years every time you fart or teleport to a different place on earth (on land, not water) every time you sneeze?",
                 "Would you rather there be a perpetual water balloon war going on in your city/town or a perpetual food fight?","Would you rather have a dog with a cat’s personality or a cat with a dog’s personality?","If you were reborn in a new life, would you rather be alive in the past or future?",
                 "Would you rather eat no candy at Halloween or no turkey at Thanksgiving?",
                 "Would you rather date someone you love or date someone who loves you?",
                 "Would you rather lose the ability to lie or believe everything you’re told?",
                 "Would you rather be free or be totally safe?",
                 "Would you rather eat poop that tasted like chocolate, or eat chocolate that tasted like crap?",
                 "Would you rather Look 10 years older from the neck up, or the neck down?",
                 "Would you rather be extremely underweight or extremely overweight?",
                 "Would you rather Experience the beginning of planet earth or the end of planet earth?",
                 "Would you rather have three kids and no money, or no kids with three million dollars?",
                 "Would you rather be the funniest person in the room or the most intelligent?",
                 "Would you rather have a Lamborghini in your garage or a bookcase with 9000 books and infinite knowledge?",
                 "Would you rather Reverse one decision you make every day or be able to stop time for 10 seconds every day?",
                 "Would you rather win $50,000 or let your best friend win $500,000?",
                 "Would you rather Run at 100 mph or fly at ten mph?",
                 "Would you rather Continue with your life or restart it?",
                 "Would you rather be able to talk your way out of any situation, or punch your way out of any situation?",
                 "Would you rather have free Wi-Fi wherever you go or have free coffee where/whenever you want?",
                 "Would you rather have seven fingers on each hand or have seven toes on each foot?",
                 "Would you rather live low life with your loved one or rich life all alone?",
                 "Would you rather have no one to show up for your wedding or your funeral?",
                 "Would you rather Rule the world or live in a world with absolutely no problems at all?",
                 "Would you rather go back to the past and meet your loved ones who passed away or go to the future to meet your children or grandchildren to be?",
                 "Would you rather Speak your mind or never speak again?",
                 "Would you rather live the life of a king with no family or friends or live like a vagabond with your friends or family?",
                 "Would you rather know how you will die or when you will die?",
                 "Would you rather Speak all languages or be able to speak to all animals?",
                 "Would you rather get away with lying every time or always know that someone is lying?",
                 "Would you rather Eat your dead friend or kill your dog and eat it when you are marooned on a lonely island?",
                 "Would you rather have a billion dollars to your name or spend $1000 for each hungry and homeless person?",
                 "Would you rather end death due to car accidents or end terrorism?",
                 "Would you rather end the life a single human being or 100 cute baby animals?",
                 "Would you rather end hunger or end your hunger?",
                 "Would you rather give up your love life or work life?",
                 "Would you rather live in an amusement park or a zoo?",
                 "Would you rather be a millionaire by winning the lottery or by working 100 hours a week?",
                 "Would you rather read minds or accurately predict future?",
                 "Would you rather eat only pizza for 1 year or eat no pizza for 1 year?",
                 "Would you rather visit 100 years in the past or 100 years in the future?",
                 "Would you rather be invisible or be fast?",
                 "Would you rather Look like a fish or smell like a fish?",
                 "Would you rather Play on Minecraft or play FIFA?",
                 "Would you rather Fight 100 duck-sized horses or 1 horse-sized duck?",
                 "Would you rather have a grapefruit-sized head or a head the size of a watermelon?",
                 "Would you rather be a tree or have to live in a tree for the rest of your life?",
                 "Would you rather live in space or under the sea?",
                 "Would you rather lose your sense of touch or your sense of smell?",
                 "Would you rather be Donald Trump or George Bush?",
                 "Would you rather have no hair or be completely hairy?",
                 "Would you rather wake up in the morning looking like a giraffe or a kangaroo?",
                 "Would you rather have a booger hanging from your nose for the rest of your life or earwax planted on your earlobes?",
                 "Would you rather have a sumo wrestler on top of you or yourself on top of him?"]
    username = interaction.user.mention
    await interaction.response.send_message(f"{username}! {random.choice(questions)}")


async def log_case(ctx, case):
    gild = ctx.guild
    channel = None
    x = setup_channels.get_channel_id(gild.id, 'logging')
    if isinstance(x, str):
      channel = ctx.channel.id
    if isinstance(x, int):
      channel = x
    await cases.log_case(ctx.guild, case, channel)
  

async def log_case2(guild, case):
    # gild = ctx.guild
    channel = None
    x = setup_channels.get_channel_id(guild.id, 'logging')
    if isinstance(x, int):
      channel = x
    await cases.log_case(guild, case, channel)











@bot.slash_command(name="get_role_list", description="Get all the reward role list")
async def get_role_list(ctx:discord.Interaction):
    xd = level_rewards.get_all_rewards(ctx.guild.id)
    if xd is not None:
        e = Embed(title="Reward role list", color=0x57f287)
        for roles in xd:
            level, roleid = roles
            role = ctx.guild.get_role(roleid)
            e.add_field(name=f"Level {level}", value=f"{role.mention}", inline=False)
        await ctx.response.send_message(embed=e)


@bot.slash_command(name="set_reward_role", description = "Sets reward role")
@commands.has_permissions(administrator = True)
async def set_reward_role(ctx:discord.Interaction, level:int,role:discord.Role):
    xd = level_rewards.add_role(ctx.guild.id, level, role.id)
    if xd is True:
       await ctx.response.send_message("Success", ephemeral=True)
    else:
       await ctx.response.send_message("Some error occured", ephemeral=True)


@bot.slash_command(name="enable_levels", description="Command used to enable leveling sytem in the server")
@commands.has_permissions(administrator = True)
async def enable_levels(ctx:discord.Interaction):
    xd = level_rewards.enable(ctx.guild.id)
    if xd is True:
       await ctx.response.send_message("Success", ephemeral=True)
       await ctx.user.send(f"Successfully set leveling system to True")
       modlog = ctx.guild.get_channel(setup_channels.get_channel_id(ctx.guild, "logging"))
       embed = Embed(title="Leveling was enabled", description=f"Leveling system was enabled in {ctx.guild} by {ctx.user.mention}")
       modlog = modlog or ctx.channel
       await modlog.send(embed=embed)
    else:
       await ctx.response.send_message("Some error occured!")


@bot.slash_command(name="disable_levels", description="Command used to enable leveling sytem in the server")
@commands.has_permissions(administrator = True)
async def disable_levels(ctx:discord.Interaction):
    xd = level_rewards.disable(ctx.guild.id)
    if xd is True:
       await ctx.response.send_message("Success", ephemeral=True)
       modlog = ctx.guild.get_channel(setup_channels.get_channel_id(ctx.guild, "logging"))
       await ctx.user.send(f"Successfully set leveling system to False")
       embed = Embed(title="Leveling was disabled", description=f"Leveling system was disabled in {ctx.guild} by {ctx.user.mention}")
       modlog = modlog or ctx.channel
       await modlog.send(embed=embed)
    else:
       await ctx.response.send_message("Some error occured!")



@bot.slash_command(name="givexp", description="Give some XP to a user")
@commands.has_permissions(administrator=True)
@commands.has_permissions(manage_guild=True)
async def givexp(ctx:discord.Interaction, member:discord.Member, xp:int):
    ifenable = level_rewards.get_enabled(ctx.guild.id)
    if ifenable is True:
        await ctx.response.defer()
        user_data = leveling_cursor.execute('SELECT * FROM users WHERE server_id=? AND user_id=?', (ctx.guild.id, ctx.user.id)).fetchone()
        xp_current, level = user_data[2], user_data[3]
        xp_needed = 5 * (level ** 2) + 50 * level + 100
        new_xp = xp_current + xp
        if new_xp >= xp_needed:
            level_new = level + 1
        else:
            level_new = level
        leveling_cursor.execute(f"UPDATE users SET xp = ?, level = ? WHERE server_id = ? AND user_id = ?", (new_xp, level_new, ctx.guild.id, ctx.user.id))
        leveling_db.commit()
        leveling_cursor.execute("SELECT xp, level FROM users WHERE server_id = ? AND user_id = ?", (ctx.guild.id, ctx.user.id))
        leveling_db.commit()
        data = leveling_cursor.fetchone()
        xp_for, level_for = data
        if level_for != level:
            xd = level_rewards.get_one_role(ctx.guild.id, int(level_for))
            await ctx.followup.send(f"{member.mention}",embed=configs.levelup(member, int(level_for)))
            if xd is None:
              pass
            else:
              role = ctx.guild.get_role(xd)
              await ctx.user.add_roles(role)
    else:
        await ctx.response.send_message("**Error!** Leveling System disabled in this server!")

@bot.slash_command(name="resetxp", description="Resets all levels and xp for a server")
@commands.has_permissions(administrator=True)
async def resetxp(ctx:discord.Interaction):
    if level_rewards.get_enabled(ctx.guild.id) is True:
      leveling_cursor.execute("UPDATE users SET xp = 0, level = 0 WHERE server_id = ?", (0, ctx.guild.id))
      leveling_db.commit()
      await ctx.response.send_message("Done", ephemeral=True)
    else:
       await ctx.response.send_message("**Error!** Leveling System disabled in this server!")







@bot.slash_command(name="user_xp_reset", description = "Resets a defined users xp")
@commands.has_permissions(administrator=True)
async def user_xp_reset(ctx:discord.Interaction, user:discord.User):
    if level_rewards.get_enabled(ctx.guild.id) is True:
      leveling_cursor.execute("UPDATE users SET xp = 0, level = 0 WHERE server_id = ? AND user_id = ?", (ctx.guild.id, user.id))
      leveling_db.commit()
      await ctx.response.send_message(f"Successfully reset {user.mention}'s XP", ephemeral=True)
    else:
        await ctx.response.send_message("**Error!** Leveling System disabled in this server!")


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.page_size = 10 # number of entries per page
        self.conn = sqlite3.connect("expData.db")
        self.cursor = self.conn.cursor()

    @discord.slash_command(name="leaderboard", description="Shows the leaderboard of the server!")
    async def leaderboard(self, ctx:discord.Interaction):
        xd = level_rewards.get_enabled(ctx.guild.id)
        if xd is True:
            self.cursor.execute("SELECT user_id, xp, level FROM users WHERE server_id = ? ORDER BY level DESC, xp DESC", (ctx.guild.id,))
            entries = self.cursor.fetchall()
            num_pages = (len(entries) + self.page_size - 1) // self.page_size

            current_page = 1
            start_idx = (current_page - 1) * self.page_size
            end_idx = start_idx + self.page_size
            page_entries = entries[start_idx:end_idx]
            leaderboard_embed = discord.Embed(title="Leaderboard")
            leaderboard_embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            leaderboard_embed.set_thumbnail(url=bot.user.avatar)
            leaderboard_embed.set_footer(text=f"Page {current_page}/{num_pages}")

            for i, entry in enumerate(page_entries):
                member_id, xp, level = entry
                member = ctx.guild.get_member(member_id)
                leaderboard_embed.add_field(name=f"{i+1}. {member.name}#{member.discriminator}", value=f"Level: {level}, XP: {xp}", inline=False)

            message = await ctx.response.send_message(embed=leaderboard_embed)

            if num_pages > 1:
                # create buttons for pagination
                previous_button = discord.ui.Button(label='⬅️', style=discord.ButtonStyle.grey, disabled=True)
                next_button = discord.ui.Button(label='➡️', style=discord.ButtonStyle.grey)
                buttons_row = discord.ui.View()
                buttons_row.add_item(previous_button)
                buttons_row.add_item(next_button)

                def update_leaderboard():
                    start_idx = (current_page - 1) * self.page_size
                    end_idx = start_idx + self.page_size
                    page_entries = entries[start_idx:end_idx]

                    leaderboard_embed.clear_fields()

                    for i, entry in enumerate(page_entries):
                        leaderboard_embed.add_field(name=f"{i+1}. {entry[0]}", value=f"Level: {entry[1]}, XP: {entry[2]}", inline=False)

                    leaderboard_embed.set_footer(text=f"Page {current_page}/{num_pages}")
                    return leaderboard_embed

                # update message with current page
                await message.edit_original_response(embed=update_leaderboard(), view=buttons_row)

                def check_pagination(interaction):
                    return interaction.user == ctx.user and interaction.message.id == message.id

                while True:
                    try:
                        interaction = await self.bot.wait_for('button_click', timeout=60.0, check=check_pagination)
                    except asyncio.TimeoutError:
                        # disable buttons if no response after 60 seconds
                        previous_button.disabled = True
                        next_button.disabled = True
                        await message.edit_original_response(view=buttons_row)
                        break
                    else:
                        if interaction.component.label == '⬅️' and current_page > 1:
                            current_page -= 1
                            next_button.disabled = False
                        elif interaction.component.label == '➡️' and current_page < num_pages:
                            current_page += 1
                            previous_button.disabled = False
                        else:
                            continue

                        # update message with new page and button states
                        leaderboard_embed = update_leaderboard()
                        previous_button.disabled = current_page == 1
                        next_button.disabled = current_page == num_pages
                        await interaction.response.send_message(embed=leaderboard_embed, view=buttons_row)
        else:
            await ctx.response.send_message(f"{ctx.author.mention}, **Error!** Leveling system disabled in the server!.")

@bot.command()
async def fakban(ctx:commands.Context):
    for member in ctx.guild.members:
        if member.bot:
            return
        conf_embed = Embed(color=0xff0000, title="User was banned", description=f"{user.mention} was banned for reason: {reason} by {ctx.user.mention}")
        user_embed = Embed(color=0xff0000, title='You were banned', description=f'You were banned in **{ctx.guild.name}** by Moderator {ctx.user.mention} for reason: {reason}')
        await ctx.response.send_message(embed=conf_embed)
        if member.bot:
            return
        else:
            await member.send(embed=user_embed)

bot.add_cog(Leaderboard(bot))

bot.run(configs.TOKEN)
# asyncio.run(bot.db.close())
