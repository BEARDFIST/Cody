#python3
#-*- encoding: utf-8 -*-

import sys

if sys.version_info.major.__str__() != "3":
    print("ERROR: Python 3 is necessary")
    exit(1)

import discord
import random
from configparser import parsejson

config = parsejson()
email = config["account"]["email"]
password = config["account"]["password"]

choices = [":fire:",":skier:"]

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if botname in message.content.lower() or botname in message.content.lower():
        response = random.choice(choices)
        await client.send_message(message.channel, response)

try:
    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    client.run(email, password)
except KeyboardInterrupt:
    print('quit')
    exit()
