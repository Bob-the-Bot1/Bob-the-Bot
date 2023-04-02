import sqlite3
import datetime
import discord
import setup_channels



# create table for storing mod actions
conn = sqlite3.connect('moderation_cases.db')
c = conn.cursor()

# Create the moderation cases table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS moderation_cases (
        case_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        guild INTEGER,
        action TEXT,
        reason TEXT,
        moderator_id INTEGER,
        timestamp TEXT
    )
''')


# function to add a new mod action to the database
def add_case(user_id, action, reason, moderator_id, timestamp, guild:int):
    c.execute('INSERT INTO moderation_cases (user_id, guild, action, reason, moderator_id, timestamp) VALUES (?, ?, ?, ?, ?, ?)', (user_id, guild,action, reason, moderator_id, timestamp))
    conn.commit()
    return c.lastrowid

# function to get all mod actions for a given server
# def get_mod_actions(server_id):
#     c.execute("SELECT * FROM mod_actions WHERE server_id=?", (server_id,))
#     return c.fetchall()

# # function to delete a mod action by case ID
# def delete_mod_action(case_id):
#     c.execute("DELETE FROM mod_actions WHERE case_id=?", (case_id,))
#     conn.commit()


# Create the cases table

# Define functions for adding cases
# def add_kick_case(user_id, reason, moderator_id, timestamp):
#     cursor.execute("INSERT INTO mod_actions VALUES (?, ?, ?, ?, ?)", (user_id, "kick", reason, moderator_id, timestamp))
#     db.commit()

# def add_ban_case(user_id, reason, moderator_id, timestamp):
#     cursor.execute("INSERT INTO cases VALUES (?, ?, ?, ?, ?)", (user_id, "ban", reason, moderator_id, timestamp))
#     db.commit()

# def add_warn_case(user_id, reason, moderator_id, timestamp):
#     cursor.execute("INSERT INTO cases VALUES (?, ?, ?, ?, ?)", (user_id, "warn", reason, moderator_id, timestamp))
#     db.commit()

# Define function for logging cases
async def log_case(guild, case_info, channelid):
    case_id = case_info[0]
    user_id = case_info[1]
    action = case_info[2]
    reason = case_info[3]
    moderator_id = case_info[4]
    timestamp = case_info[5]
    case_count = c.execute('SELECT COUNT(*) FROM moderation_cases WHERE user_id = ?', (user_id,)).fetchone()[0]
    embed = discord.Embed(
        title=f"Case {case_id} | {action} | {user_id}",
        color=0xFF5733
    )
    embed.add_field(name="guild", value=f"{guild.id}", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Moderator", value=f"<@{moderator_id}>", inline=False)
    embed.add_field(name="Timestamp", value=timestamp, inline=False)
    embed.set_footer(text=f"Case #{case_count}")
    # channelid = setup_channels.get_channel_id(guild.id, "logging")
    channel = guild.get_channel(channelid)
    await channel.send(embed=embed)