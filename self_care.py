import discord
import json
from os import path


client = discord.Client()

data = {}

DATA_FILE = "data.json"

BOT_CHANNEL_ID = 664999941374083072

ADMIN_ROLE_ID = 665000607291277376

TOKEN_FILE = "token.txt"
TOKEN = ""


def read_token():
    global TOKEN
    with open(TOKEN_FILE, 'r') as token_file:
        TOKEN = token_file.read()


def does_file_exist():
    return not path.exists(DATA_FILE)


def file_to_dict():
    with open(DATA_FILE, 'r') as file:
        return json.loads(file.read())


def write_file():
    json_data = json.dumps(data)
    with open(DATA_FILE, "w") as file:
        file.write(json_data)
    return


@client.event
async def on_ready():
    global data
    print('We have logged in as {0.user}'.format(client))
    if does_file_exist():
        print("File does not exist!")
        # Do initialization
    else:
        data = file_to_dict()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Do bot things


client.run(TOKEN)
