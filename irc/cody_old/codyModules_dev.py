#codyModules.py
import time, os, sys, stat, inspect, random, re, smtplib, socket, py_compile, datetime, feedparser
from pytz import timezone
from urllib2 import Request, urlopen, URLError 
from subprocess import Popen, PIPE, STDOUT

#   DEFINE READCONFIG() AND THEN READ IT INTO CONSTANTS (VALUES ARE FETCHED FROM CODY.CFG)

def readConfig():

	config = open('/root/Dropbox/Cody/cody.cfg', 'r').read().splitlines()

	configDict = {}
	i = 1

	for line in config:

		#set up identifiers
		equalsPos = line.find('=')
		lineValue = line[equalsPos + 1:]
		lineSetting = line[:equalsPos]

		#handle special exceptions
		if 'CODY_REPLY_TRIGGERS' in lineSetting:
			lineValue = lineValue + ' '

		if 'CHANNEL' in lineSetting:
			lineValue = lineValue.replace(';',',')


		#if there are multiple values, seperate them using ; as delimiter
		if ';' in lineValue \
		and '=' in line:
			configDict[lineSetting] = lineValue.split(';')

		#if there isn't, just assign them.
		elif '=' in line:
			configDict[lineSetting] = lineValue


	return configDict

CONFIGURATION 		= 	readConfig()
BOT_NICKNAME		=	CONFIGURATION['BOT_NICKNAME']
ADMIN_HOSTS			=	CONFIGURATION['ADMIN_HOSTS']
ADMIN_NICKS			=	CONFIGURATION['ADMIN_NICKS']
CODY_REPLY_TRIGGERS	=	CONFIGURATION['CODY_REPLY_TRIGGERS']
CODY_REPLIES 		=	CONFIGURATION['CODY_REPLIES']
HOME_CHANNEL 		=	CONFIGURATION['HOME_CHANNEL']
RSS_FEEDS 			=   CONFIGURATION['RSS_FEEDS']
RSS_FEED_CHANNELS	=   CONFIGURATION['RSS_FEED_CHANNELS']
ADMIN_GREETINGS 	=	[ CONFIGURATION['ADMIN1_GREETINGS'], CONFIGURATION['ADMIN2_GREETINGS'], 
						  CONFIGURATION['ADMIN3_GREETINGS'], CONFIGURATION['ADMIN4_GREETINGS'] ]


#   FIGURE OUT FILE NAME
MODULES_FILE_PATH			= inspect.getfile(inspect.currentframe())
MODULES_FILE_NAME 			= MODULES_FILE_PATH[MODULES_FILE_PATH.lower().find('codymodules'):]


### SCRIPT FUNCTIONS ###

#validation
def authenticateHost(HOST, ADMIN_HOSTS):
	return HOST.lower()[HOST.find('@')+1:] in ADMIN_HOSTS

def authenticateNick(NICK, ADMIN_NICKS):
	return NICK.lower() in ADMIN_NICKS


#MakeFile(file_name): makes a file.
def MakeFile(file_path):

	filevar = open(file_path, 'w')
	filevar.write('')
	filevar.close()
 

#data parser
def dataParse(console):
	if ':' in console:
		#first let's fetch the NICK
		parseMsg = console[1:]
		bangPos  = parseMsg.find('!')
		NICK	 = parseMsg[:bangPos]  
	
		#next, we'll fetch the hostname
		parseMsg = parseMsg[bangPos + 1:]
		spacePos = parseMsg.find(' ')
		HOSTNAME = parseMsg[:spacePos]
	
		#now we'll fetch MSG_TYPE
		parseMsg = parseMsg[spacePos + 1:]
		spacePos = parseMsg.find(' ')
		MSG_TYPE = parseMsg[:spacePos]
	
		#we fetch CHANNEL
		parseMsg = parseMsg[spacePos + 1:]
		spacePos = parseMsg.find(' ')
		CHANNEL  = parseMsg[:spacePos]
	
		#now we'll fetch MESSAGE
		parseMsg = parseMsg[spacePos + 2:] # +2 to skip the colon
		MESSAGE  = parseMsg[:]

		#use regex to remove junk from CHANNEL name
		try:
			channel = re.search(r'(\Q#\E\w+)[?\r\n]', CHANNEL)
			print 'channel = '+ str(channel.group(1))
			CHANNEL = channel.group(1)

		except:
			pass
		
		#then return everything
		return [NICK, HOSTNAME, MSG_TYPE, CHANNEL, MESSAGE]
	
	else:
		#DO NOT PARSE
		return ['NULL','NULL','NULL','NULL','NULL']



### BOT FUNCTIONS ##

#getTitle 

def getTitle(SESSION_DATA, trigger):

	URLstart = SESSION_DATA['MESSAGE'].find("http://")
	URLend = SESSION_DATA['MESSAGE'][URLstart:].find(' ')
	url = SESSION_DATA['MESSAGE'][URLstart:URLend]

	try:
		page = urlopen(url).read()
		title = page[page.find("<title>")+len("<title>"):page.find('</title>')]
		if len(title) < 50:
			SESSION_DATA['IRC'].send ( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :'+title+'\r\n')
		else:
			print 'title was too big to post'
				
	except:
		print 'failed to get title'


#!cody.uptime
def codyUptime(SESSION_DATA, trigger):

	currentUptime				= time.time() - SESSION_DATA['START_TIME']
	
    #Defining time variables:
	MINUTE  =   60
	HOUR    =   MINUTE  * 60
	DAY     =   HOUR    * 24
 
    #Calculate seconds into days, hours and minutes:
	days    = int(  currentUptime / DAY  )          
	hours   = int( (currentUptime % DAY  ) / HOUR   )
	minutes = int( (currentUptime % HOUR ) / MINUTE )
 
    # UPTIME = X days, X hours, X minutes
	uptimeString = ""

	if days > 0:
		uptimeString += str(days) + " " + (days == 1 and "day" or "days" ) + ", "

	if len(uptimeString) > 0 or hours > 0:
		uptimeString += str(hours) + " " + (hours == 1 and "hour" or "hours" ) + ", "

	uptimeString += str(minutes) + " " + (minutes == 1 and "minute" or "minutes" ) + ". "
        
	SESSION_DATA['IRC'].send ( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :I\'ve been awake for ' + str(uptimeString) + '. I last woke up ' + SESSION_DATA['DATE'] + '\r\n' )
	

#!cody.reload
def codyReload(SESSION_DATA, trigger):

	if len(SESSION_DATA['MESSAGE']) > len('!cody.reload \r\n'):
		try:
			newCody 				= SESSION_DATA['MESSAGE'].split()
			newCody 				= newCody[1]

		except:
			newCody 				= 'NULL'
				
	#else if no file is supplied, reload the running version
	else:
		newCody					= SESSION_DATA['BOT_FILE_NAME']

	folderPath 				= '/root/Dropbox/Cody/'
	
	if os.path.isfile(folderPath + newCody):
	
		try:
			py_compile.compile(folderPath + newCody, doraise = True)
			py_compile.compile(MODULES_FILE_PATH, doraise = True)
					
		except py_compile.PyCompileError as e:
			errorMessage = str(e)
			SESSION_DATA['IRC'].send ( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :'+errorMessage+'. \r\n' )

		else:
			os.chmod(folderPath + newCody, stat.S_IRWXU)
			reload(sys.modules[MODULES_FILE_NAME[:-(len('.py'))]])
			SESSION_DATA['IRC'].send ( 'QUIT :reloading myself\r\n' )
			exec(open(folderPath + newCody))
	

	else:
		SESSION_DATA['IRC'].send ( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :File not found! \r\n' )	


#hiCody
def hiCody(SESSION_DATA, trigger):

	proximityMaximum = 3

	for trigger in CODY_REPLY_TRIGGERS:
		if trigger in SESSION_DATA['MESSAGE'].lower()\
		and SESSION_DATA['MESSAGE'].lower().find(trigger) < SESSION_DATA['MESSAGE'].lower().find('cody')\
		and SESSION_DATA['MESSAGE'].lower().find(trigger) + len(trigger) + proximityMaximum >= SESSION_DATA['MESSAGE'].lower().find('cody'):
		
			SESSION_DATA['IRC'].send ( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :'+random.choice(CODY_REPLIES)+'\r\n' )


#joinChannel
def joinChannel(SESSION_DATA, trigger):
	
	if len(SESSION_DATA['MESSAGE']) > len('!cody.join\r\n') \
	and '#' in SESSION_DATA['MESSAGE'] :
		SESSION_DATA['IRC'].send 				( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :Joining channel:'+SESSION_DATA['MESSAGE'][len('!cody.join'):]+'\r\n')
		SESSION_DATA['IRC'].send 				( 'JOIN '+SESSION_DATA['MESSAGE'][len('!cody.join'):]+'\r\n' )
		
	else:
		SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :Usage: !cody.join [#channel]\r\n' )	

#partChannel
def partChannel(SESSION_DATA, trigger):

	if len(SESSION_DATA['MESSAGE']) > len('!cody.join\r\n') \
	and '#' in SESSION_DATA['MESSAGE'] :
		SESSION_DATA['IRC'].send 	( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :Leaving channel:'+SESSION_DATA['MESSAGE'][len('!cody.part'):]+'\r\n')
		SESSION_DATA['IRC'].send 	( 'PART '+SESSION_DATA['MESSAGE'][len('!cody.part'):]+'\r\n' )
	else:
		SESSION_DATA['IRC'].send 	('PRIVMSG '+SESSION_DATA['CHANNEL']+' :Usage: !cody.part [#channel] ' + '\r\n' )


#codyPython    
def codyPython(SESSION_DATA, trigger):
	
	if len(SESSION_DATA['MESSAGE']) > len('!cody.python\r\n'):
		pythonExpression 	= SESSION_DATA['MESSAGE']
		pythonParseURI 		= 'http://tumbolia.appspot.com/py/'
		pyInput 			= pythonExpression[len('!cody.python '):]
		pyInput 			= pyInput.replace(' ','%20')
		pyInput 			= pyInput.replace('\\n','%0A')
		pyInput 			= pyInput.replace('\\t','%09')
		tumboliaRequest 	= Request(pythonParseURI + pyInput)  

		try:
			response = urlopen(tumboliaRequest).read()
			SESSION_DATA['IRC'].send ( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :' + response + '\r\n')
		
		except URLError, e:
			if hasattr(e, 'reason'):
				SESSION_DATA['IRC'].send ( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :Failed to reach the server. Reason: '+e.reason+' \r\n')		
			elif hasattr(e, 'code'):
				SESSION_DATA['IRC'].send ( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :The server couldn\'t fulfill the request. Reason: ' + e.code + '\r\n')
	else:
		SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :Usage: !cody.python [python code] ' + '\r\n' )



#cody.greeting
def codyGreeting(SESSION_DATA, trigger):
	
	if  HOME_CHANNEL in SESSION_DATA['CHANNEL']\
	and 'JOIN' in SESSION_DATA['MSG_TYPE']\
	and BOT_NICKNAME not in SESSION_DATA['NICK']: #added this, instead of having the try-exception
		try:
			adminNumber 				= ADMIN_NICKS.index(SESSION_DATA['NICK'].lower()) #added .lower()
			SESSION_DATA['IRC'].send 	('PRIVMSG #code :'+ str(random.choice(ADMIN_GREETINGS[adminNumber])) +'\r\n')
		except:
			pass
		

#!cody.version
def codyVersion(SESSION_DATA, trigger):

	path 						= SESSION_DATA['BOT_FILE_NAME'] #get path of currently running file, including filename
	codyVersion 				= path[-6:-3]
	SESSION_DATA['IRC'].send 					( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :I am currently running version: '+codyVersion+'\r\n' ) #print version number to IRC


#!cody.report
def codyReport(SESSION_DATA, trigger):
	
	if len(SESSION_DATA['MESSAGE']) > len(trigger + '\r\n'):
	
		codyReport				= SESSION_DATA['MESSAGE'].split(' ', 1)
		codyReport				= codyReport[1]
	
		#OPEN FILES FOR READ AND READ THEM INTO LOCAL
		if 'bug' in trigger:
			readReport 				= open("/root/Dropbox/Cody/userFeedback/bugReports.txt", "r")

		if 'feature' in trigger:
			readReport		 		= open("/root/Dropbox/Cody/userFeedback/featureRequests.txt", "r")
							
		reportData 				= readReport.read().splitlines()
		startLine 				= len(reportData) / 2
		codyReport				= str(startLine) + '. ' + codyReport[:-2] + ' [' + SESSION_DATA['NICK'] + ']' + '\r\n'
		reportData.append(codyReport)
			
		#WRITE STRINGS TO FILES
		if 'bug' in trigger:
			writeReport				= open("/root/Dropbox/Cody/userFeedback/bugReports.txt", "w")

		if 'feature' in trigger:
			writeReport		 		= open("/root/Dropbox/Cody/userFeedback/featureRequests.txt", "w")

		for element in reportData:

			print>>writeReport, reportData[int(reportData.index(element))]


		"""		## THIS DEFINITELY WORKS, BUT IS UGLY ##
		i = 0
		while i < len(reportData):
				
			if reportData[i] != '':
				print>>writeReport, reportData[i]
				print>>writeReport, ''
				i += 1

			else:
				i += 1

		"""
		readReport.close()


		# REPORT THE RESULT TO CHANNEL
		if 'feature' in trigger:
			SESSION_DATA['IRC'].send 					( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :Your feature request has been saved and will be reviewed by my developers.\r\n' )
		elif 'bug' in trigger:
			SESSION_DATA['IRC'].send 					( 'PRIVMSG '+SESSION_DATA['CHANNEL']+' :Your bug has been saved and will be reviewed by my developers.\r\n' )
		else:
			SESSION_DATA['IRC'].send 					('PRIVMSG '+SESSION_DATA['CHANNEL']+' :Usage: !cody.bug [your bug report] ' + '\r\n' )


#!cody.help
def codyHelp(SESSION_DATA, trigger):

	SESSION_DATA['IRC'].send ( 'NOTICE '+SESSION_DATA['NICK']+' '+SESSION_DATA['CHANNEL']+' :Available Commands:\r\n' )
	
	if authenticateHost(SESSION_DATA['HOST'], ADMIN_HOSTS):

		for lists in SESSION_DATA['CODY_PUBLIC_FUNCTIONS'], SESSION_DATA['CODY_HOME_FUNCTIONS'], SESSION_DATA['CODY_ADMIN_FUNCTIONS']:
			for trigger in lists:
				SESSION_DATA['IRC'].send ( 'NOTICE '+SESSION_DATA['NICK']+' '+SESSION_DATA['CHANNEL']+' :'+trigger+'\r\n' )
		
		SESSION_DATA['IRC'].send ( 'NOTICE '+SESSION_DATA['NICK']+' '+SESSION_DATA['CHANNEL']+' :For more information about how to use a specific command, type the command without supplying any additional information.\r\n' )

	else:

		for trigger in SESSION_DATA['CODY_PUBLIC_FUNCTIONS']:

			SESSION_DATA['IRC'].send ( 'NOTICE '+SESSION_DATA['NICK']+' '+SESSION_DATA['CHANNEL']+' :'+trigger+'\r\n' )
		
		SESSION_DATA['IRC'].send ( 'NOTICE '+SESSION_DATA['NICK']+' '+SESSION_DATA['CHANNEL']+' :For more information about how to use a specific command, type the command without supplying any additional information.\r\n' )


#!cody.mail
def codyMail(SESSION_DATA, trigger):

	if len(SESSION_DATA['MESSAGE']) > len('!cody.mail\r\n'):
		mailToPos 	= SESSION_DATA['MESSAGE'].find('TO:') 		
		messagePos 	= SESSION_DATA['MESSAGE'].find('MESSAGE:') 

		sendTo		= SESSION_DATA['MESSAGE'][mailToPos  + len('TO: ')		:messagePos]
		subject 	= 'Mail from ' + SESSION_DATA['NICK'] + ', sent from ' + SESSION_DATA['CHANNEL']
		body 	 	= SESSION_DATA['MESSAGE'][messagePos + len('MESSAGE: ') :]

		sender = 'cody@ec2-46-137-14-14.eu-west-1.compute.amazonaws.com'
		message = "From: "+SESSION_DATA['NICK']+' <cody@ec2-46-137-14-14.eu-west-1.compute.amazonaws.com>\nTo: '+sendTo+'<'+sendTo+'>\nSubject: '+subject+'\n'+body
		
		smtpObj = smtplib.SMTP('localhost')
		smtpObj.sendmail(sender, [sendTo], message)

		SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :Okay '+ SESSION_DATA['NICK'] + ', I\'ve sent your message to the following adress: ' + sendTo + '\r\n' )
		time.sleep(2)
	
	else:
		SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :Usage: !cody.mail TO: [email@email.com] MESSAGE: [your message] ' + '\r\n' )


#!cody.convert ( in ) 
def codyConvert(SESSION_DATA, trigger):

	findAmount 			= re.search(r'\d+', SESSION_DATA['MESSAGE'])
	findOutputUnit		= re.search(r' in (.+)', SESSION_DATA['MESSAGE'].lower())

	#check if any of the regex searches returned None. Calling group() on a variable == None would cause Cody to crash
	if findAmount 	   \
	and findOutputUnit :
	
		#fetch console from MESSAGE to be sent to google
		inputAmount  =  findAmount.group()
		inputUnit 	 =  SESSION_DATA['MESSAGE'][findAmount.end() : findOutputUnit.start()]
		outputUnit 	 =  findOutputUnit.group(1)

		#handle special exceptions
		if 'cash money' in outputUnit \
		or 'cash moneys' in outputUnit  \
		or 'cmo' in outputUnit:
			
			value = 0

			for letter in inputUnit:
				if ord(letter) == random.randint(65,122):
					value = value + (int(inputAmount) * (ord(letter) / 5 * 31))
				elif ord(letter) == 97:
					value = value + (int(inputAmount) * 1)
				elif ord(letter) == 112:
					value = value + (int(inputAmount) * 100)
				elif ord(letter) == 120:
					value = value + (int(inputAmount) * (ord(letter) / 5 * 63))
				elif ord(letter) < 65:
					value = value + (int(inputAmount) * (ord(letter) / 4 * 13))
				elif ord(letter) >= 65:
					value = value + (int(inputAmount) * (ord(letter) / 3 * 5))

			SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :'+inputAmount+inputUnit+" = "+str(format(value, ",d"))+" cash money"+'\r\n')

			
	#check if there are any spaces in our console and, if so, convert them to %20 so we can use them in a URL
		if ' ' in inputAmount:
			inputAmount = inputAmount.replace(' ', '%20')
		
		if ' ' in inputUnit:
			inputUnit = inputUnit.replace(' ', '%20')

		if ' ' in outputUnit:
			outputUnit = outputUnit.replace(' ', '%20')
		
		#request conversion from google calculator
		try:
			convertedAmount = urlopen('http://www.google.com/ig/calculator?hl=en&q=' + inputAmount + inputUnit + '%3D%3F' + outputUnit).read()

		except URLError, e:
				if hasattr(e, 'reason'):
					print 'Failed to reach the server. Reason: '+e.reason
					convertedAmount = ''
				elif hasattr(e, 'code'):
					print 'The server couldn\'t fulfill the request. Reason: ' + e.code
					convertedAmount = ''

		#convert %20's back to spaces so we don't print them to the channel
		if '%20' in inputAmount:
			inputAmount = inputAmount.replace('%20', ' ')
		
		if '%20' in inputUnit:
			inputUnit = inputUnit.replace('%20', ' ')

		if '%20' in outputUnit:
			outputUnit = outputUnit.replace('%20', ' ')

		#first, we make sure the request didn't fail
		if 'error: ""' in convertedAmount:
		
			#parsing: convertedAmount now looks like this: {lhs: "100 British pounds",rhs: "916.326154 Norwegian kroner",error: "",icc: true}
			rhsPos = convertedAmount.find('rhs: "') + len('rhs: "')
			if '.' in convertedAmount:
				dotPos = convertedAmount.find('.', rhsPos)
			else:
				dotPos = rhsPos
			spacePos = convertedAmount.find(' ', dotPos)
			errorPos = convertedAmount.find('",error')

			#first we get the amount, and the currency type
			outputAmount = convertedAmount[rhsPos:spacePos]
			outputCurrency   = convertedAmount[spacePos:errorPos]

			#check if there are weird characters or spaces in our amount, and if so, remove them.
			fixedOutput = ''
				
			for character in outputAmount:
				if character.isdigit() 	 \
				or character == '.'		 \
				and '.' not in fixedOutput :
					fixedOutput = fixedOutput + character

			outputAmount = fixedOutput

			#round the number to 2 digits (if the number is a float)
			if '.' in str(outputAmount):
				outputAmount = round(float(outputAmount), 2)

			#combine the amount with the currency type
			convertedAmount = str(outputAmount) + outputCurrency
			
			#and then print it to the channel
			SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :'+inputAmount+inputUnit+' = '+convertedAmount+'\r\n' )

		elif 'error: "4"' in convertedAmount:
			print "Request failed: unit not recognized"			

		elif 'error: "Unit mismatch"' in convertedAmount:
			print "Request failed: units are not related"

		else:
			pass

#!cody.worldtime ( time in <city or state> )
#def codyWorldtime(SESSION_DATA, trigger):
#	if "time in" in SESSION_DATA['MESSAGE']:

#https://www.google.com/search?q=time+Copenhagen&btnG=Search

#!cody.quit
def codyQuit(SESSION_DATA, trigger):
	SESSION_DATA['IRC'].send ( 'QUIT :terminating..\r\n' )
	exit()


#!cody.fileUpdates
def codyFileUpdates(SESSION_DATA, trigger):     

	if '!cody.updates' in trigger\
	and SESSION_DATA['POST_CODY_FILE_UPDATES']:
		SESSION_DATA['POST_CODY_FILE_UPDATES'] = False
		SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :File updates are now turned off.\r\n')

	elif '!cody.updates' in trigger\
	and not SESSION_DATA['POST_CODY_FILE_UPDATES']:
		SESSION_DATA['POST_CODY_FILE_UPDATES'] = True
		SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :File updates are now turned on.\r\n')


	elif 'codyFileUpdates' in trigger:

		if (datetime.datetime.now().second % 3) == 0 : 
			#fetch filename last updated
		#if 'dropboxCheck' in SESSION_DATA['MESSAGE']: #for testing purposes
			fetchCodyTime 	 	= 'date -r '+SESSION_DATA['BOT_FILE_PATH']
			fetchModulesTime 	= 'date -r '+MODULES_FILE_PATH

			getTimeCodyCommunicate 	 	= Popen(fetchCodyTime, 	shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
			getTimeCody, gTCComErr		= getTimeCodyCommunicate.communicate()

			getTimeModulesCommunicate  	= Popen(fetchModulesTime, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True) 
			getTimeModules, gTMComErr	= getTimeModulesCommunicate.communicate() 
	 
			#lastUpdatedCody == 'Fri Feb  1 18:36:14 UTC 2013'

			lastUpdatedCody		= str(getTimeCody)
			lastUpdatedModules 	= str(getTimeModules)
			
			lastRecorded 		= open("/root/Dropbox/Cody/resources/lastupdated.db", "r")
			lastRecordedlines	= lastRecorded.read().splitlines()
			lastRecordedCody 	= lastRecordedlines[0]
			lastRecordedModules = lastRecordedlines[1]
			lastRecorded.close()



			if str(lastRecordedCody+'\n') != str(lastUpdatedCody):
				if SESSION_DATA['POST_CODY_FILE_UPDATES']:
					SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['HOME_CHANNEL']+' :'+SESSION_DATA['BOT_FILE_NAME']+' has been updated.\r\n')
				dbWrite = open("/root/Dropbox/Cody/resources/lastupdated.db", "w")
				dbWrite.write(lastUpdatedCody+lastUpdatedModules)
				dbWrite.close()

			
			elif str(lastRecordedModules+'\n') != str(lastUpdatedModules):
				if SESSION_DATA['POST_CODY_FILE_UPDATES']:
						SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['HOME_CHANNEL']+' :'+MODULES_FILE_NAME+' has been updated.\r\n')
				dbWrite = open("/root/Dropbox/Cody/resources/lastupdated.db", "w")
				dbWrite.write(lastUpdatedCody+lastUpdatedModules)
				dbWrite.close()


def codyFeeds(SESSION_DATA, trigger):

	#TURN OFF FEEDS
	if '!cody.feeds' in trigger \
	and SESSION_DATA['POST_CODY_FEEDS']:
		SESSION_DATA['POST_CODY_FEEDS'] = False
		SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :RSS feeds are now turned off.\r\n')

	#TURN ON FEEDS
	elif '!cody.feeds' in trigger \
	and not SESSION_DATA['POST_CODY_FEEDS']:
		SESSION_DATA['POST_CODY_FEEDS'] = True
		SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :RSS feeds are now turned on.\r\n')

    #CHECK FOR NEW DATA 4 TIMES AN HOUR
	elif 'codyFeeds' in trigger \
	and (datetime.datetime.now().minute % 14) == 0 \
	or '!cody.feedme' in trigger:
		
		#FETCH THE FEEDS AND PREPARE DATA FOR POSTING
		#try:
			feed = feedparser.parse(RSS_FEEDS)
						
			
			#SPECIAL EXCEPTION - NYAA.EU
			feedData 	= {}
			checkfile 	= open("/root/Dropbox/Cody/resources/rssFeeds.db", "r").read()
			newData 	= []

			#FILL A DICTIONARY WITH THE RESULTS OF THE FEEDPARSER.PARSE METHOD
			for item in feed["entries"]:
				feedData[feed["entries"].index(item)]							= {}
				feedData[feed["entries"].index(item)]['torrentlink']			= feed["entries"][feed["entries"].index(item)]["id"]
				feedData[feed["entries"].index(item)]['title'] 					= feed["entries"][feed["entries"].index(item)]["title"]
				feedData[feed["entries"].index(item)]['subsFilter']		 		= feed["entries"][feed["entries"].index(item)]["tags"][0]["term"]
				feedData[feed["entries"].index(item)]['content']				= feedData[feed["entries"].index(item)]['title'] + " --> " + feedData[feed["entries"].index(item)]['torrentlink']
			
			#CHECK THE DICTIONARY
			for item in feedData.keys():

				#CREATE A TEMP VARIABLE
				newDataItem = ''

				#THROW OUT NON-ASCII CHARACTERS
				for char in feedData[item]['content']:
					newDataItem = newDataItem + char.encode('ascii', 'ignore')
				
				#CHECK FOR AND THROW OUT RESULTS WITH BAD SUBS OR NON-ENGLISH SUBS
				if feedData[item]['subsFilter'] != "English-translated Anime" \
				or  "horrible" 	in feedData[item]['title'].lower():
					feedData.pop(item)

				#COMPARE DICTIONARY TO FILE, CHECK FOR NEW DATA
				elif newDataItem not in checkfile:
					newData.append(newDataItem)
				
			#WRITE NEW DATA TO FILE IF IT EXISTS
			if newData:
				
				#REMAKE THE FILE IF THE FILE NOW EXCEEDS 500 LINES
				if len(checkfile.splitlines()) > 500:
					with open("/root/Dropbox/Cody/resources/rssFeeds.db", "w") as feedfile:
						for item in feedData.keys():
							feedfile.write('\n')
							feedfile.write(feedData[item]['content'] + '\r\n')

						feedfile.close()

				#IF NOT, JUST APPEND TO IT
				else:
					with open("/root/Dropbox/Cody/resources/rssFeeds.db", "a") as feedfile:
						for item in newData:
							feedfile.write('\n')
							feedfile.write(newData[newData.index(item)] + '\r\n')

						feedfile.close()
			
			#PRINT NEW DATA TO CHANNEL
			for item in newData:
				
				SESSION_DATA['IRC'].send('PRIVMSG '+RSS_FEED_CHANNELS+' :' + newData[newData.index(item)] + '\r\n' )
				time.sleep(1.5)

				
		#except Exception as e:
		#	SESSION_DATA['IRC'].send('PRIVMSG '+HOME_CHANNEL+' :codyFeeds failed: '+str(e)+'\r\n' ) 


#!cody.time

#codyPython
def codyTime(SESSION_DATA, trigger):
	
	if len(SESSION_DATA['MESSAGE']) > len('!cody.time\r\n'):

		location = SESSION_DATA['MESSAGE'][SESSION_DATA['MESSAGE'].find('!cody.time ')+len('!cody.time '):-len('\r\n')].title().replace(' ', '_')
		format = "%H:%M UTC%z"
		local_time = datetime.datetime.now(timezone('UTC'))
		offset = ''

		#FIGURE OUT THE CONTINENT BY TRYING THEM ALL
		try:
			converted_time = local_time.astimezone(timezone('Europe/'+location)).strftime(format)
		except:
		
			try:
				converted_time = local_time.astimezone(timezone('America/'+location)).strftime(format)
			except:
		
				try:
					converted_time = local_time.astimezone(timezone('Australia/'+location)).strftime(format)
				except:
		
					try:
						converted_time = local_time.astimezone(timezone('Asia/'+location)).strftime(format)
					except:

						try:
							converted_time = local_time.astimezone(timezone('Africa/'+location)).strftime(format)
						except:
							
							try:
								#if there's a + in the timezone, remove that stuff before we call pytz. we will be calculating it manually.
								if '+' in location:
									offset = location[location.find('+')+len('+'):]
									offsetType = '+'
									location = location[:location.find('+')].upper()

								elif '-' in location:
									offset = location[location.find('-')+len('-'):]
									offsetType = '-'
									location = location[:location.find('-')].upper()

								else:
									location = location.upper()

								converted_time = local_time.astimezone(timezone(location)).strftime(format)[:-len(' UTC+0100')]
								
								#check if the timezone has an offset (eg: GMT+1)
								if offset:
									
									if '+' in offsetType:
										offset_hours 		= int(converted_time[:len('xx')]) + int(offset)

									elif '-' in offsetType:
										offset_hours 		= int(converted_time[:len('xx')]) - int(offset)

									#check if we've gone over 24 hours
									if offset_hours > 23:
										offset_hours = offset_hours - 24

									#or under 0 hours
									if offset_hours < 0:
										offset_hours = offset_hours + 24
									
									#check if we need to add a 0 to make the number two digits
									if len(str(offset_hours)) < 2:
										offset_hours = '0' + str(offset_hours)

									#add it all together
									converted_time = str(offset_hours) + converted_time[2:]
									location = location + offsetType + str(offset)

							except:
								converted_time = 'not_found'
								location = location.title()

		location = location.replace('_', ' ')

		if 'not_found' not in converted_time:
			SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :The current time in '+location+' is '+converted_time+'\r\n' )

		else: 
			SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :'+str(location)+' was not found. '+'\r\n' )
		
	else:
		SESSION_DATA['IRC'].send('PRIVMSG '+SESSION_DATA['CHANNEL']+' :Usage: !cody.time [location], or !cody.time [timezone]' + '\r\n' )	 
