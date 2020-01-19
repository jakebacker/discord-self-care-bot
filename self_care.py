import sys

import discord
import json
from os import path
from datetime import datetime
import re

# Set up discord
client = discord.Client()

# A few dictionaries to store data
user_data = {}
config = {}  # late, morning

# Help embed information
help_embed = discord.Embed(title="Commands", color=0x00ff00)
help_embed.description = "All commands start with prefix %care"
help_embed.add_field(name="Command", value="opt-in\nset\n\nhelp", inline=True)
help_embed.add_field(name="Description",
                     value="Opt into sleep reminders\nSet a config option\n\tOptions: sleep_start, sleep_end, "
                     "hard_mode\nSend this message",
                     inline=True)

# Data file locations
# Current config file layout
# {"106466406924562432": {"opt-in": "true", "sleep_start": "00", "sleep_end": "06", "hard_mode": "false"}}
DATA_FILE = "data.json"
CONFIG_FILE = "config.json"

# IDs of some things
BOT_CHANNEL_ID = 567179438047887381

ADMIN_ROLE_ID = 576464175430238208

# Where the token is
TOKEN_FILE = "token.txt"
TOKEN = ""

# Misc Configs

COOL_DOWN = 600


# Get the current hour
def get_hour():
    return int(datetime.now().strftime("%H"))


# Read the auth token from the file
def read_token():
    global TOKEN
    curr_dir = sys.argv[0]
    print(curr_dir)
    last_index = curr_dir.rfind("/")
    curr_dir = curr_dir[:last_index]
    with open(curr_dir + "/" + TOKEN_FILE, 'r') as token_file:
        TOKEN = token_file.read().strip()


# Check if a file exists
def does_file_exist(file_name):
    return not path.exists(file_name)


# Reads a file into a dictionary
def file_to_dict(file_name):
    with open(file_name, 'r') as file:
        return json.loads(file.read())


# Writes a dictionary to a file
def write_file(data, file_name):
    json_data = json.dumps(data)
    with open(file_name, "w") as file:
        file.write(json_data)
    return


# Initialize a user's dictionary if it hasn't been done already
def init_user(user_id, key, default):
    if not user_data.__contains__(user_id):
        user_data[user_id] = {}

    if not user_data[user_id].__contains__(key):
        user_data[user_id][key] = default


# Set a piece of data for a user
def set_user_data(user_id, key, value):
    init_user(user_id, key, value)
    user_data[user_id][key] = value
    write_file(user_data, DATA_FILE)


# Toggle a piece of data for a user
def toggle_data(user_id, key, on, off):
    init_user(user_id, key, off)
    user_dict = user_data[user_id]
    if user_dict[key] == on:
        set_user_data(user_id, key, off)
        return off
    else:
        set_user_data(user_id, key, on)
        return on


# Check if the current time is between a start and end time
def in_between(now, start, end):
    if start <= end:
        return start <= now < end
    else:  # over midnight e.g., 23:30-04:15
        return start <= now or now < end


# Send the help message to a channel
async def send_help_message(channel):
    await channel.send(embed=help_embed)


# Set up config files and such
@client.event
async def on_ready():
    global user_data
    global config
    global help_embed

    print('We have logged in as {0.user}'.format(client))
    if does_file_exist(DATA_FILE):
        print("File does not exist!")
        write_file(user_data, DATA_FILE)
        write_file(config, CONFIG_FILE)
    else:
        user_data = file_to_dict(DATA_FILE)
        config = file_to_dict(CONFIG_FILE)


# Run when a message is sent
@client.event
async def on_message(message):
    # Ignore the message if it is from the bot
    if message.author == client.user:
        return

    # Make sure it starts with % and is in the bot channel or in direct messages
    if message.content.startswith("%care") and message.channel == client.get_channel(BOT_CHANNEL_ID):
        parts = message.content.split(" ")

        user_str = str(message.author.id)

        if parts[0] == "%care":  # Make sure it is actually a command we care about
            if len(parts) == 1:  # If there isn't anything else, just send the help message
                await send_help_message(message.channel)
            elif parts[1] == "opt-in":  # If the command is opt-in, toggle the user's opt-in status
                data = toggle_data(user_str, "opt-in", "true", "false")

                # Set up some more config options related to opt-in
                if not user_data[user_str].__contains__("sleep_start"):
                    set_user_data(user_str, "sleep_start", "00")
                if not user_data[user_str].__contains__("sleep_end"):
                    set_user_data(user_str, "sleep_end", "06")
                if not user_data[user_str].__contains__("hard_mode"):
                    set_user_data(user_str, "hard_mode", "false")

                # Notify the user that it worked
                await message.channel.send("New opt-in status for user {0}: {1}\n"
                                           "Default range for alerts is 00 to 06".format(message.author.mention,
                                                                                         data))

            elif parts[1] == "set":  # Set a configuration value
                key = parts[2]
                value = parts[3]

                if key == "sleep_start" or key == "sleep_end":  # Config sleeping times
                    # Make sure it is valid
                    if not len(value) == 2 or not re.match("^\\d{2}$", value) or not 0 <= int(value) <= 23:
                        await message.channel.send("Invalid data for {0}. "
                                                   "Data must be a number between 00 and 23".format(key))
                    else:
                        # If the data is valid, set the user's config value
                        set_user_data(user_str, key, value)
                        await message.channel.send("Set value {0} to {1} for user {2}".format(key, value, user_str))
                elif key == "hard_mode":  # Config "hard mode"
                    if not value == "true" and not value == "false":
                        await message.channel.send("Invalid data for {0}."
                                                   "Data must be either `true` or `false`".format(key))
                    else:
                        set_user_data(user_str, key, value)
                        await message.channel.send("Set value {0} to {1} for user {2}".format(key, value, user_str))

            elif parts[1] == "help":  # Print the help message
                await send_help_message(message.channel)

    else:
        hour = get_hour()

        str_id = str(message.author.id)

        # Check if the user has opted in
        if user_data.__contains__(str_id) and user_data[str_id]["opt-in"] == "true":

            # If the current time is in between the user's defined sleeping times...
            if in_between(hour, int(user_data[str_id]["sleep_start"]), int(user_data[str_id]["sleep_end"])):
                # Otherwise, just send them a message
                if user_data[str_id].__contains__("last_message"):
                    last_ts = int(user_data[str_id]["last_message"])
                    if datetime.now().timestamp() - last_ts < COOL_DOWN:
                        return

                user_data[str_id]["last_message"] = datetime.now().timestamp()
                await client.get_channel(BOT_CHANNEL_ID).send("{0} Get some sleep so you feel great tomorrow!"
                                               .format(message.author.mention))


# Read the token from the file and connect to the server
read_token()
client.run(TOKEN)
