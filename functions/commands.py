import random
import psutil
import py_compile
import compileall
import os
import traceback
import urllib.request
import re
import subprocess
import datetime
import pprint
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from imgurpython import ImgurClient


''' HELPER FUNCTIONS '''

def run_command(cmd, get_output=True):
    """given shell command, returns output"""
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    # get the output and return it
    if get_output:

        printable_output = '```' + 'cody@beardfist.com:~# ' + cmd + '\n\n'
        
        for line in iter(p.stdout.readline, b''):
            printable_output += str(line)[2:-3] + "\n"

        printable_output += '```'

        return printable_output

def user(msg):
    ''' find the user for the previous provided message '''
    username = str(msg.author.name)+'#'+str(msg.author.discriminator)
    return username


# IMAGE SEARCH SYSTEMS

def _google_image_search(query, conf):
    ''' returns an image from google image search '''

    api_key = conf['google_api_key']
    cse_id  = conf['google_cse_id']
    list_of_responses = []    
    
    service = build("customsearch", "v1", developerKey=api_key)

    try:
        res = service.cse().list(q=query, cx=cse_id, searchType="image", num=10).execute()
    except HttpError as err:
        if err.resp.status == 403:
            return 403
        else:
            return 'ERROR: ' + err[1:-1]
    
    try:
        for result in res['items']:
            list_of_responses.append(result['link'])
    except: 
        return "No images found for query: '%s'" % query
    
    return random.choice(list_of_responses)   

def _pixplorer_image_search(query):
    ''' returns a thumbnail from pixplorer.co.uk '''

    list_of_images = []

    query_encode = urllib.parse.quote_plus(query)

    query_string = 'http://api.pixplorer.co.uk/image?word=%s&amount=10' % query_encode

    request      = urllib.request.Request(query_string)
    result       = urllib.request.urlopen(request)
    charset      = result.info().get_content_charset()
    html         = result.read().decode(charset)
    json_results = json.loads(html)

    try:
        for result in json_results['images']:
            list_of_images.append(result['imageurl'])
    except:
        return "No images found for query: '%s'" % query

    return random.choice(list_of_images)  

def _imgur_search(conf, query="", filetype='gif', random_result=False):
    ''' returns an image from imgur '''

    # basic api client setup
    client_id      = conf['imgur_client_id']
    client_secret  = conf['imgur_client_secret']
    client         = ImgurClient(client_id, client_secret)

    # get the image url for an imgur album
    def _get_direct_url(url):

        scrape_start = '<link rel="image_src"'
        scrape_end   = '"/>'

        request      = urllib.request.Request(url)
        result       = urllib.request.urlopen(request)
        charset      = result.info().get_content_charset()
        html         = result.read().decode(charset)

        direct_url   = html[html.find(scrape_start):]
        direct_url   = direct_url[direct_url.find('href="') + len('href="'):direct_url.find(scrape_end)]

        return direct_url

    # handle random
    if random_result:
        gifs = []

        for item in client.gallery_random():        
            if item.is_album:
                direct_url = _get_direct_url(item.link)
        
            else:
                direct_url = item.link
        
            if '.gif' in direct_url:
                gifs.append(direct_url)
        
        return random.choice(gifs)


    # handle queries
    else:
        query = query.split(' ')    
        advanced_dict = {'q_all':query, 'q_type':filetype}    
        item = random.choice(client.gallery_search("", advanced=advanced_dict))
    
        if item.is_album:    
            return _get_direct_url(item.link)
    
        else:    
            return item.link


''' UNIT TESTING '''
def test_google_image_search():
    pass

''' BOT COMMANDS '''

def apache(trigger, message, conf):
    
    if user(message) in conf['admins']:
        return run_command('service apache2 restart')

    else:
        return '-- insufficient access --'

def help(trigger, message, conf):
    ''' !help '''
    help_content = '''```
    !help     - shows this help message
    !diag     - get current server metrics
    !reload   - forces cody to quit and restart
    !error    - a python stacktrace
    !username - username and id
    !channel  - channel name and id
    !roles    - your roles on the server
    !server   - server name and id
    !web      - status codes for hosted sites
    !currency - `!currency 99 aud in cad`
    !image    - returns an image of whatever you specify
    !gif      - returns a gif of whatever you specify, or a random gif with no query.
    ```'''
    return help_content


def image(trigger, message, conf):
    ''' !image '''

    if ' ' not in message.content:
        return 'an image of what?'
    else:
        query = message.content.split(' ', 1)[1]

    google_response = _google_image_search(query, conf)

    if google_response == 403:
        return _pixplorer_image_search(query)
    else:
        return google_response

def gif(trigger, message, conf):
    ''' !gif '''

    if ' ' not in message.content:
        return _imgur_search(conf, random_result=True)
    
    else:
        query_string = message.content.split(' ', 1)[1]
        return _imgur_search(conf, query=query_string)




def diag(trigger, message, conf):
    ''' !diag '''

    cpu    = repr(psutil.cpu_percent(interval=0.2)).rjust(4, ' ')
    disk   = repr(psutil.disk_usage('/').percent).rjust(4, ' ')
    memory = repr(psutil.virtual_memory().percent).rjust(4, ' ')
    
    wrapper = """\
    ```yaml
    usage:
      cpu:  {0}%
      ram:  {1}%
      disk: {2}%
    ```""".format(cpu, memory, disk)

    return wrapper

def hi(message, conf, prev_response):
    ''' hi cody '''

    choices = ["HAIOOOOO!","waazzaaap!","You're not my dad!","Heeeey, my eskimo brother!","You're way too young to be a bitch.","Shut up.","WHAT? WHAT COULD YOU POSSIBLY WANT?","That's how your mom greets me, too.","I'm not in the mood for your petty squabbles.","WU TANG CLAN AINT NUTTIN' TO FUCK WIT'","'sup, g?,You're so money.","To impress a chick - helicopter dick.","Heeeeeeey, brother.","Bitches dont know bout mah pylons.","If you talk to me like that again","I'mma choke a bitch."]
    response = random.choice(choices)

    while response == prev_response:
        response = random.choice(choices)
        
    return (response, response)


def reload(trigger, message, conf):
    ''' !reload 
        Tries to compile all .py files the bot requires,
        and if all files compile successfully,
        reloads the bot. If a file fails to compile,
        prevents the reload and returns a traceback.
    '''
    # exit cody with an errorcode to trigger supervisor restart

    botfile = conf['botfile']
    botpath = conf['botpath']
    features = botpath + '/functions'

    # compile a list of all .py files in the /functions subfolder
    pyfiles = []

    for root, dirs, files in os.walk(features):
        for file in files:
            if file.endswith(".py"):
                pyfiles.append(features + '/' + file)

    try:
        # try to compile main file
        py_compile.compile(botfile, doraise = True)

        # try to compile subfiles
        for file in pyfiles:
            py_compile.compile(file, doraise = True)
    
        
    except:
        # return a traceback
        return '```python\n{}```'.format(traceback.format_exc())

    # reload the bot
    print ("reloading")
    exit(1)


def error(trigger, message, conf):
    raise Exception("this is a test failure")


def username(trigger, message, conf):
    ''' !username '''
    account = "```"+user(message)+"```"
    return account


def roles(trigger, message, conf):
    ''' !roles '''
    list_of_roles = []
    for role in message.author.roles:
        list_of_roles.append(role.name)
    result = "```"+repr(list_of_roles)+"```"
    return result


def channel(trigger, message, conf):
    ''' !channel '''
    channel_out = """```yaml
    channel_id:   {0}
    channel_name: {1}
    ```""".format(repr(message.channel.id), repr(message.channel.name))
    return channel_out


def server(trigger, message, conf):
    ''' !server '''

    server_out = """```yaml
    server_id:   {0}
    server_name: {1}
    ```""".format(repr(message.server.id), repr(message.server.name))
    return server_out


def web(trigger, message, conf):
    ''' !web '''

    website_config_path = '/etc/apache2/sites-enabled'
    webconfig = []
    for root, dirs, files in os.walk(website_config_path):
        for file in files:
            with open(website_config_path+os.sep+file, 'r') as webconffile:
                webconfig.append(webconffile.readlines())

    websites = []
    for file in webconfig:
        for line in file:
            if "ServerName" in line:
                websites.append(line.strip().replace("ServerName ",''))

    results = ''
    for website in websites:
        try:
            req = urllib.request.Request('http://www.'+website, method='GET')
            res = urllib.request.urlopen(req)
            results += website.ljust(25,' ') +': '+ str(res.status)+' '+str(res.reason)+"\n"
        except:
            pass

    webstatus = '''```{}```'''.format(results)
    return webstatus

def currency(trigger, message, conf):
    ''' !currency 100 dkk in usd '''
    #return repr(message)
    message        = message.content
    findAmount     = re.search('\d+', message)
    findOutputUnit = re.search(' in (.+)', message.lower())

    #check if any of the regex searches returned None. Calling group() on a variable == None would cause Cody to crash
    if findAmount      \
    and findOutputUnit :
    
        #fetch console from MESSAGE to be sent to google
        inputAmount  =  findAmount.group()
        inputUnit    =  message[findAmount.end() : findOutputUnit.start()]
        outputUnit   =  findOutputUnit.group(1)     

        if " " in inputAmount:
            inputAmount = inputAmount.replace(" ","")

        if " " in inputUnit:
            inputUnit = inputUnit.replace(" ","")

        if " " in outputUnit:
            outputUnit = outputUnit.replace(" ","")

        if len(inputUnit) <= 4 \
        and len(outputUnit) <= 4:
            google          = "https://www.google.com/finance/converter?a="+str(inputAmount)+"&from="+str(inputUnit)+"&to="+str(outputUnit)
            googlereq       = urllib.request.Request(google)
            googleresult    = urllib.request.urlopen(googlereq)
            charset         = googleresult.info().get_content_charset()
            html            = googleresult.read().decode(charset)
            htmlsplit1      = html.partition("<span class=bld>")
            outputAmount    = htmlsplit1[2].partition("</span>")

            if outputAmount[0]:
                return "{0} {1} = {2}".format(str(inputAmount), str(inputUnit), str(outputAmount[0]))

def kpm(trigger, message, conf):

    if user(message) in conf['lmn']:

        # regenerate timesheets
        if "regen" in message.content:
            return run_command("python /var/www/website/scripts/kpmtransport_backup.py regen", get_output=False)

            current_date = datetime.datetime.now()
            

            return "Timesheet regeneration initiated for %s." % current_date.strftime("%B")


        else:
            return "Invalid argument."

    else:
        return "Insufficient access."