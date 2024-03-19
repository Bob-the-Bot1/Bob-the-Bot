import sqlite3


connect = sqlite3.connect('level_and_guild_settings.db')
c = connect.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS guild_settings (
             guild_id INTEGER PRIMARY KEY,
             leveling_enabled INTEGER DEFAULT 1
          )''')


c.execute("CREATE TABLE IF NOT EXISTS lr (guild_id INTEGER, level INTEGER, role INTEGER, PRIMARY KEY (guild_id, level))")

# c.execute('''CREATE TABLE IF NOT EXISTS leveling (
#              guild_id INTEGER,
#              user_id INTEGER,
#              level INTEGER DEFAULT 0,
#              xp INTEGER DEFAULT 0,
#              PRIMARY KEY (guild_id, user_id)
#           )''')

connect.commit()

def add_role(guild_id:int, level:int, roleid:int):
    try:
        c.execute("INSERT OR REPLACE INTO lr (guild_id, level, role) VALUES (?, ?, ?)", (guild_id, level, roleid))
        connect.commit()
        return True
    except KeyError:
        return False

def enable(guild_id:int):
    c.execute("UPDATE guild_settings SET leveling_enabled = 1 WHERE guild_id = ?", (guild_id,))
    connect.commit()
    return True

def disable(guild_id:int):
    c.execute("UPDATE guild_settings SET leveling_enabled = 0 WHERE guild_id = ?", (guild_id,))
    connect.commit()
    return True

def get_enabled(guild_id:int):
    c.execute("SELECT leveling_enabled FROM guild_settings WHERE guild_id = ?", (guild_id,))
    connect.commit()
    row = c.fetchone()
    try:
        if row[0] == 1:
            return True
        else:
            return False
    except TypeError as e:
        raise e

def get_one_role(guild_id:int, level:int):
    c.execute("SELECT level, role FROM lr WHERE guild_id = ?", (guild_id,))
    connect.commit()
    row = c.fetchall()
    for data in row:
        level_getting, role_id = data
        if level_getting == level:
            return data[0]
        else:
            return None

def get_all_rewards(guild_id:int):
    c.execute("SELECT level, role FROM lr WHERE guild_id = ?", (guild_id,))
    connect.commit()
    row = c.fetchall()
    return row


def Convert(give_list:list) -> dict:
    it = iter(give_list)
    res_dct = dict(zip(it, it))
    return res_dct


def check_whether_if(server_id:int):
    c.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (server_id,))
    rows = c.fetchone()
    if rows is None:
        c.execute("INSERT INTO guild_settings (guild_id, leveling_enabled) VALUES (?, ?)", (server_id, 1))
        connect.commit()
    else:
        c.execute("UPDATE guild_settings SET leveling_enabled = leveling_enabled WHERE guild_id = ?", (server_id,))
        connect.commit()

# def add_xp_or_level(guild_id:int, user_id:int, xp:int, level:int):
#     c.execute("INSERT OR REPLACE INTO leveling (guild_id, user_id, level, xp) VALUES (?, ?, ?, ?)", (guild_id, user_id, level, xp))
#     connect.commit()
#     return True
