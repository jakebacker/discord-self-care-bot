import discord
import json
from os import path
from datetime import datetime

"""
TODO:
Check the system time, if past 2am and user ID = declan, Luke, anyone else who opts in react with :zzz:
Maybe even let it be configurable
Could probably do it per user if I wanted to

"""


client = discord.Client()

user_data = {}
config = {}  # opt_in_id, late, morning

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
async def on_raw_reaction_add(payload):
    # Add user to DB

    if payload.message_id == config["opt_in_id"] and str(payload.emoji) == '💤':
        user_data[payload.user_id] = "in"  # For now, just an on or off. This leaves room for changes
        write_file(user_data, DATA_FILE)


@client.event
async def on_raw_reaction_remove(payload):

    if payload.message_id == config["opt_in_id"] and str(payload.emoji) == '💤':
        user_data[payload.user_id] = "out"  # For now, just an on or off. This leaves room for changes
        write_file(user_data, DATA_FILE)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("%care opt-in") and message.channel == client.get_channel(BOT_CHANNEL_ID) \
            and discord.utils.get(message.guild.roles, id=ADMIN_ROLE_ID) in message.author.roles:
        opt_message = await message.channel.send("React to this message with :zzz: to be added to the self-care bot!")
        config["opt_in_id"] = opt_message.id
        write_file(config, CONFIG_FILE)

    hour = get_hour()
    if config["late"] <= hour < config["morning"]:
        str_id = str(message.author.id)
        if user_data.__contains__(str_id) and user_data[str_id] == "in":
            await message.channel.send("{0} Get some sleep so you feel great tomorrow!".format(message.author.mention))


read_token()
client.run(TOKEN)
