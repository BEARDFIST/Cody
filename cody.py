#-*- encoding: utf-8 -*-
import discord
import traceback
import os
import sys

from functions import commands
from functions import configparser

botfile     = __file__
botpath     = sys.path[0] #os.sep.join(__file__.split(os.sep)[:-1])
client      = discord.Client()
conf        = configparser.config()
bot         = conf['botname']
account     = conf['account']
password    = conf['password']
server_name = conf['server']['name']
server_id   = conf['server']['id']
home_name   = conf['home_channel']['name']
home_id     = conf['home_channel']['id']
server      = discord.Server(name=server_name, id=server_id)
home        = discord.Channel(name=home_name, id=home_id, server=server)
prev_resp   = ''
reload_msg  = "reloading..."

# extend conf dict with bot file context
conf['botfile'] = botfile
conf['botpath'] = botpath

switch = {
    '!apache'   : commands.apache,
    '!reload'   : commands.reload,
    '!diag'     : commands.diag,
    '!username' : commands.username,
    '!roles'    : commands.roles,
    '!channel'  : commands.channel,
    '!server'   : commands.server,
    '!error'    : commands.error,
    '!help'     : commands.help,
    '!web'      : commands.web,
    '!currency' : commands.currency,
    '!kpm'      : commands.kpm,
    '!image'    : commands.image,
    '!gif'      : commands.gif
}

# raise Exception("Deliberate error in main")

@client.event
async def on_message(message):
    mc = message.content.lower()

    if " " in mc:
        trigger, msg = mc.split(" ", 1)
    else:
        trigger = mc

    try:
        # we do not want the bot to reply to itself
        if message.author == client.user:
            return
        
        # triggers
        elif trigger in switch.keys():
            response = switch[trigger](trigger, message, conf)
            await client.send_message(message.channel, response)

        # conversation
        elif mc.endswith(' cody'):
            global prev_resp
            response, prev_resp = commands.hi(message, conf, prev_resp)
            await client.send_message(message.channel, response)

    except SystemExit:
        await client.send_message(message.channel, '*'+reload_msg+'*')
        exit(1)

    except:
        err = '''```python\n{}```'''.format(traceback.format_exc())
        await client.send_message(home, err)

try:
    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

        async for message in client.logs_from(home, limit=50):
            if reload_msg in message.content:
                if message.author == client.user:
                    await client.send_message(home,"*reloaded successfully*")
                    await client.delete_message(message)
                    break
        

    client.run(account, password)
except KeyboardInterrupt:
    print('quit')
    exit()