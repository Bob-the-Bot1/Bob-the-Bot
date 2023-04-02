# import json

# # Create a dictionary to store the channel IDs for each server
# channel_ids = {}

# # Load the channel IDs from the JSON file
# with open('channel_ids.json', 'r') as f:
#     channel_ids = json.load(f)

# # Function to get the channel ID for a specific server and category
# def get_channel_id(server_id, category) -> int:
#     if server_id in channel_ids and category in channel_ids[server_id]:
#         return channel_ids[server_id][category]
#     else:
#         return None

# # Function to set the channel ID for a specific server and category
# def set_channel_id(server_id, category, channel_id):
#     if server_id not in channel_ids:
#         channel_ids[server_id] = {}
#     elif category not in channel_ids:
#         channel_ids[server_id][category] = {}
#     else:
#         channel_ids[server_id][category] = channel_id
#     with open('channel_ids.json', 'w') as f:
#         json.dump(channel_ids, f, indent=4)


import sqlite3

conn = sqlite3.connect('channel_ids.db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS channels (server_id TEXT, logging TEXT, welcome TEXT, levelup TEXT, birthday TEXT)''')
# cur.execute("INSERT INTO channels (server_id, logging, welcome, levelup) VALUES (?, ?, ?, ?)", (str(100), str(1123456798), str(1200), str(454)))
conn.commit()

def get_channel_id(server, category:str):
    category.lower()
    cur.execute(f"SELECT {category} FROM channels WHERE server_id = ?",(server.id,))
    data = cur.fetchone()
    data_fetch_to_list = []
    if data is not None:
        data_fetch_to_list.extend(data)
        listToStr = ' '.join([str(elem) for elem in data_fetch_to_list])
        channel_id = data[0]
    else:
        channel_id = None

    if channel_id is None or server.get_channel(int(channel_id)) is None:
        return None
    
    else:
        return int(channel_id)

# print(get_channel_id(100, "LOGGING"))


def set_channel_id(server_id:int, category:str, channel_id:int) -> None:
    category.lower()
    cur.execute(f"UPDATE channels SET {category} = ? WHERE server_id = ?", (channel_id, server_id))
    conn.commit()

# def join_or_none(server_id:int):
#     cur.execute(f"SELECT logging, welcome, levelup FROM channels WHERE server_id = ?",(str(server_id),))
#     data = cur.fetchone()
#     if data is not None:
#         data.sort()
#         logging, welcome, levelup = data
#         if logging is None:
#             logging = "Logging is not setup"
#         elif welcome is None:
#             welcome = 'Welcome not setup'
#         elif levelup is None:
#             levelup = 'Levelup not setup'
#         cur.execute("INSERT INTO channels (server_id, logging, welcome, levelup) VALUES (?, ?, ?, ?)", (str(server_id), logging, welcome, levelup))
#         conn.commit()

def check_whether_if(server_id:int):
    cur.execute("SELECT * FROM channels WHERE server_id = ?", (server_id,))
    rows = cur.fetchone()
    if rows is None:
        cur.execute("INSERT INTO channels (server_id, logging, welcome, levelup) VALUES (?, ?, ?, ?)", (server_id, None, None, None))
        conn.commit()
    else:
        cur.execute("UPDATE channels SET logging = logging, welcome = welcome, levelup = levelup WHERE server_id = ?", (server_id,))
        conn.commit()