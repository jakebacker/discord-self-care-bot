import discord
import json
from os import path
from datetime import datetime
import re

"""
TODO:
Check the system time, if past 2am and user ID = declan, Luke, anyone else who opts in react with :zzz:
Maybe even let it be configurable
Could probably do it per user if I wanted to
Kick people who activate "hard mode"

"""


client = discord.Client()

user_data = {}
config = {}  # late, morning

DATA_FILE = "data.json"
CONFIG_FILE = "config.json"

BOT_CHANNEL_ID = 664999941374083072

ADMIN_ROLE_ID = 665000607291277376

TOKEN_FILE = "token.txt"
TOKEN = ""


def get_hour():
    return int(datetime.now().strftime("%H"))


def read_token():
    global TOKEN
    with open(TOKEN_FILE, 'r') as token_file:
        TOKEN = token_file.read()


def does_file_exist(file_name):
    return not path.exists(file_name)


def file_to_dict(file_name):
    with open(file_name, 'r') as file:
        return json.loads(file.read())


def write_file(data, file_name):
    json_data = json.dumps(data)
    with open(file_name, "w") as file:
        file.write(json_data)
    return


def init_user(user_id, key, default):
    if not user_data.__contains__(user_id):
        user_data[user_id] = {}

    if not user_data[user_id].__contains__(key):
        user_data[user_id][key] = default


def set_user_data(user_id, key, value):
    init_user(user_id, key, value)
    user_data[user_id][key] = value
    write_file(user_data, DATA_FILE)


def toggle_data(user_id, key, on, off):
    init_user(user_id, key, off)
    user_dict = user_data[user_id]
    if user_dict[key] == on:
        set_user_data(user_id, key, off)
        return off
    else:
        set_user_data(user_id, key, on)
        return on


def in_between(now, start, end):
    if start <= end:
        return start <= now < end
    else:  # over midnight e.g., 23:30-04:15
        return start <= now or now < end


async def send_help_message(channel):
    message = "Commands all start with %care \n" \
              "Valid commands:\n" \
              "**opt-in**                  Opt into sleep reminders\n" \
              "**set**                       Set a config option\n" \
              "                             Options: sleep_start, sleep_end\n" \
              "**help**                     Send this message"
    await channel.send(message)


@client.event
async def on_ready():
    global user_data
    global config
    print('We have logged in as {0.user}'.format(client))
    if does_file_exist(DATA_FILE):
        print("File does not exist!")
        write_file(user_data, DATA_FILE)
        write_file(config, CONFIG_FILE)
    else:
        user_data = file_to_dict(DATA_FILE)
        config = file_to_dict(CONFIG_FILE)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("%") and message.channel == client.get_channel(BOT_CHANNEL_ID):
        parts = message.content.split(" ")
        user_str = str(message.author.id)
        if parts[0] == "%care":
            if len(parts) == 1:
                await send_help_message(message.channel)
            elif parts[1] == "opt-in":
                data = toggle_data(user_str, "opt-in", "true", "false")
                if not user_data[user_str].__contains__("sleep_start"):
                    set_user_data(user_str, "sleep_start", "00")
                if not user_data[user_str].__contains__("sleep_end"):
                    set_user_data(user_str, "sleep_end", "06")
                await message.channel.send("New opt-in status for user {0}: {1}\n"
                                           "Default range for alerts is 00 to 06".format(message.author.mention, data))
            elif parts[1] == "set":
                key = parts[2]
                value = parts[3]

                if key == "sleep_start" or key == "sleep_end":
                    if not len(value) == 2 or not re.match("^\\d{2}$", value) or not 0 <= int(value) <= 23:
                        await message.channel.send("Invalid data for {0}. "
                                                   "Data must be a number between 00 and 23".format(key))
                    else:
                        set_user_data(user_str, key, value)
                        await message.channel.send("Set value {0} to {1} for user {2}".format(key, value, user_str))
                else:
                    set_user_data(user_str, key, value)
                    await message.channel.send("Set value {0} to {1} for user {2}".format(key, value, user_str))
            elif parts[1] == "help":
                await send_help_message(message.channel)

    else:
        hour = get_hour()

        str_id = str(message.author.id)
        if user_data.__contains__(str_id) and user_data[str_id]["opt-in"] == "true":
            if in_between(hour, int(user_data[str_id]["sleep_start"]), int(user_data[str_id]["sleep_end"])):
                await message.channel.send("{0} Get some sleep so you feel great tomorrow!"
                                           .format(message.author.mention))


read_token()
client.run(TOKEN)
