import json

# Create a dictionary to store the channel IDs for each server
channel_ids = {}

# Load the channel IDs from the JSON file
with open('settings.json', 'r') as f:
    channel_ids = json.load(f)

# Function to get the channel ID for a specific server and category
def get_value(server_id, category):
    if server_id in channel_ids and category in channel_ids[server_id]:
        return channel_ids[server_id][category]
    else:
        return None

# Function to set the channel ID for a specific server and category
def set_value(server_id, category, value):
    if server_id not in channel_ids:
        channel_ids[server_id] = {}
    channel_ids[server_id][category] = value
    with open('settings.json', 'w') as f:
        json.dump(channel_ids, f)
