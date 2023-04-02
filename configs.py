import discord

TOKEN = "Insert Your Token Here"

MODLOG_COLORS = {"BAN": 0xeb4034, "MUTE": 0xeda239, "UNMUTE": 0x56c470, "UNBAN": 0x4fb09e, "KICK": 0x559ced, "JOIN":0xd117b2, "WARN":0xff0000, "TIMEOUT": 0x00ffdf, "ROLES_CHANGED": 0x00ff00}
MOD_LOG_CHANNEL_NAME = "bob-bot-logging"

WATCHING_UP = "BOB THE BOT"

STRFTIME_FOR_CASES = "%d %B, %Y"

def levelup(user, level):
    LEVELEMBED = discord.Embed(title="Level Up!", description=f"{user.mention} leveled up to {level}!. GG, Congratulations {user.mention}.", color=0xf45987)
    LEVELEMBED.set_author(name=user, icon_url=user.avatar)
    LEVELEMBED.set_thumbnail(url=user.avatar)
    return LEVELEMBED

TRANCS = "Support Tickets"