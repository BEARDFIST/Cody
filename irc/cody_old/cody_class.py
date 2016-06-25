import time, os, sys, stat, inspect, random, re, smtplib, socket, py_compile, datetime, feedparser, socket, select
from pytz import timezone
from urllib2 import Request, urlopen, URLError 
from subprocess import Popen, PIPE, STDOUT


class Cody():


	def __init__(self):

		#   SOCKETS
		self.IRC 						=   socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
		self.SOCKET_TIMEOUT				=   1

		#   STATES
		self.CONNECTED 					=   False   
		self.POST_CODY_FEEDS 			=   False
		self.POST_CODY_FILE_UPDATES 	=   True

		#   INITALIZE TIME
		self.NOW 						=   datetime.datetime.now() 
		self.START_TIME					=   time.time()
		self.YEAR						=   self.NOW.year
		self.MONTH						=   self.NOW.month   
		self.DAY 						=   self.NOW.day 
		self.DATE 						=   str(self.DAY) + '/' + str(self.MONTH) + '-' + str(self.YEAR)

		#   FIGURE OUT FILE NAME
		self.FILE_PATH					=   inspect.getfile(inspect.currentframe())
		self.FILE_NAME 					=   self.FILE_PATH[self.FILE_PATH.lower().find('cody_'):] 


		#   DECLARE TRIGGER->FUNCTION DICTIONARIES     
		self.ADMIN_FUNCTIONS 			= 	{	 '!cody.join':self.joinChannel,			'!cody.part':self.partChannel, 			'!cody.reload':self.codyReload, 	
												 '!cody.load':self.codyReload,   		'!cody.mail':self.codyMail, 			'!cody.quit':self.codyQuit, 
												 '!cody.updates':self.codyFileUpdates, 	'!cody.feeds':self.codyFeeds, 			'!cody.feedme':self.codyFeeds     }
	
		self.PUBLIC_FUNCTIONS			=	{	 '!cody.python':self.codyPython,		' cody':self.hiCody,					'!cody.version':self.codyVersion, 				 
												 '!cody.feature':self.codyReport,		'!cody.bug':self.codyReport,			'!cody.uptime':self.codyUptime,
												 ' in ':self.codyConvert, 				'!cody.help':self.codyHelp, 			'!cody.time':self.codyTime 		 }
	
		self.HOME_FUNCTIONS 			=	{	 'http':self.getTitle    } 
	
		self.PASSIVE_FUNCTIONS			=   {	 'codyGreeting':self.codyGreeting, 		'codyFileUpdates':self.codyFileUpdates, 'codyFeeds':self.codyFeeds 	 }


		#   READ CONFIG (VALUES ARE FETCHED FROM CODY.CFG) 
		self.CONFIGURATION 				= 	self.readConfig()
		self.NICKSERV_ADRESS			=	self.CONFIGURATION['NICKSERV_ADRESS']
		self.NETWORK_ADRESS				=	self.CONFIGURATION['NETWORK_ADRESS']
		self.NETWORK_PORT				=	self.CONFIGURATION['NETWORK_PORT']
		self.BOT_NICKNAME				=	self.CONFIGURATION['BOT_NICKNAME']
		self.BOT_REALNAME				=	self.CONFIGURATION['BOT_REALNAME']
		self.AUTH_PASS					=	self.CONFIGURATION['AUTH_PASS']
		self.BOT_CHANNELS				=	self.CONFIGURATION['BOT_CHANNELS']
		self.HOME_CHANNEL 				=	self.CONFIGURATION['HOME_CHANNEL']
		self.HOME_CHANNEL_PASSWORD 		=  	self.CONFIGURATION['HOME_CHANNEL_PASSWORD']
		self.LOG_PATH 					=   self.CONFIGURATION['LOG_PATH']

		#	IF WE'RE RUNNING THE DEV VERSION, CONNECT ONLY TO THE HOME_CHANNEL
		if 'dev' in self.FILE_NAME:
			self.BOT_CHANNELS 			=   self.CONFIGURATION['HOME_CHANNEL']



	def main_loop(self):

		#   IRC CONNECTION

		#connect to server
		self.IRC.connect		( ( self.NETWORK_ADRESS, int(self.NETWORK_PORT) ) )
		self.IRC.send			( 'USER cody '+self.NETWORK_ADRESS+' bla :'+self.BOT_REALNAME+'\r\n' )
		self.IRC.send 			( 'NICK '+self.BOT_NICKNAME+'\r\n' )



		### BOT CONNECTS TO IRC ###
		while True:

			consoleHasData = select.select([self.IRC], [],[], self.SOCKET_TIMEOUT)

			if consoleHasData[0]:
				console = self.IRC.recv ( 4096 )
				print console
				
			else:
				console = ''

			if 'PING' in console:
				self.IRC.send ( 'PONG ' + console.split() [ 1 ] + '\r\n' )

			if 'MOTD' in console \
			and not self.CONNECTED:
				self.IRC.send ('PRIVMSG '+self.NICKSERV_ADRESS+' :auth '+self.BOT_REALNAME+' '+self.AUTH_PASS+'\r\n')
				time.sleep(3)
				self.IRC.send ( 'JOIN '+self.BOT_CHANNELS+'\r\n' )
				self.IRC.send ( 'JOIN '+self.HOME_CHANNEL+' '+self.HOME_CHANNEL_PASSWORD+'\r\n' )
				self.CONNECTED = True
			

			if self.CONNECTED:

				#Parse chat data into chunks   
				parsedMessage 			= 	self.dataParse(console)
				self.MSG_NICK			= 	parsedMessage[0]
				self.MSG_HOST			= 	parsedMessage[1]
				self.MSG_TYPE			= 	parsedMessage[2]
				self.MSG_CHANNEL		= 	parsedMessage[3]
				self.MSG_BODY			= 	parsedMessage[4]

			
				## CHECKING IF ANY OF THE PUBLIC FUNCTION TRIGGERS APPEAR IN MESSAGE BODY
				for trigger in self.PUBLIC_FUNCTIONS.keys():

					if trigger in self.MSG_BODY:
						
						self.PUBLIC_FUNCTIONS[trigger]
						


				## CHECKING IF ANY OF THE HOME FUNCTION TRIGGERS APPEAR IN MESSAGE BODY
				for trigger in self.HOME_FUNCTIONS.keys():

					if trigger in self.MSG_BODY  \
					and self.HOME_CHANNEL in self.MSG_CHANNEL :

						self.HOME_FUNCTIONS[trigger]
						


				## CHECKING IF ANY OF THE ADMIN FUNCTION TRIGGERS APPEAR IN MESSAGE BODY
				for trigger in self.ADMIN_FUNCTIONS.keys():

					if   trigger in self.MESSAGE  \
					and  authenticateHost(self.self.MSG_HOST, self.self.ADMIN_HOSTS):

						self.ADMIN_FUNCTIONS[trigger]
						


				## EXECUTE ALL PASSIVE FUNCTIONS
				for trigger in self.PASSIVE_FUNCTIONS.keys():

					self.PASSIVE_FUNCTIONS[trigger]
					


			## RELEASE THE FRAME
			time.sleep(0.001)



	def readConfig(self):

		config = open('cody.cfg', 'r').read().splitlines()

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

	#validation
	def authenticateHost(self):
		return self.MSG_HOST.lower()[self.MSG_HOST.find('@')+1:] in self.ADMIN_HOSTS

	def authenticateNick(self):
		return self.MSG_NICK.lower() in self.ADMIN_NICKS


	#create_file(file_name): makes a file.
	def create_file(self, file_path):

		filevar = open(file_path, 'w')
		filevar.write('')
		filevar.close()
	 

	#data parser
	def dataParse(self, console):

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

	def getTitle(self):

		URLstart = self.MSG_BODY.find("http://")
		URLend = self.MSG_BODY[URLstart:].find(' ')
		url = self.MSG_BODY[URLstart:URLend]

		try:
			page = urlopen(url).read()
			title = page[page.find("<title>")+len("<title>"):page.find('</title>')]
			if len(title) < 50:
				self.IRC.send ( 'PRIVMSG '+self.CHANNEL+' :'+title+'\r\n')
			else:
				print 'title was too big to post'
					
		except:
			print 'failed to get title'


	#!cody.uptime
	def codyUptime(self):

		currentUptime				= time.time() - self.START_TIME
		
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
	        
		self.IRC.send ( 'PRIVMSG '+self.CHANNEL+' :I\'ve been awake for ' + str(uptimeString) + '. I last woke up ' + self.DATE + '\r\n' )
		

	#!cody.reload
	def codyReload(self):

		if len(self.MSG_BODY) > len('!cody.reload \r\n'):
			try:
				newCody 				= self.MSG_BODY.split()
				newCody 				= newCody[1]

			except:
				newCody 				= 'NULL'
					
		#else if no file is supplied, reload the running version
		else:
			newCody					= self.FILE_NAME

		folderPath 				= ''
		
		if os.path.isfile(folderPath + newCody):
		
			try:
				py_compile.compile(folderPath + newCody, doraise = True)
				py_compile.compile(MODULES_FILE_PATH, doraise = True)
						
			except py_compile.PyCompileError as e:
				errorMessage = str(e)
				self.IRC.send ( 'PRIVMSG '+self.CHANNEL+' :'+errorMessage+'. \r\n' )

			else:
				os.chmod(folderPath + newCody, stat.S_IRWXU)
				self.IRC.send ( 'QUIT :reloading myself\r\n' )
				exec(open(folderPath + newCody))
		

		else:
			self.IRC.send ( 'PRIVMSG '+self.CHANNEL+' :File not found! \r\n' )	


	#hiCody
	def hiCody(self):

		proximityMaximum = 3

		for trigger in self.CODY_REPLY_TRIGGERS:
			if trigger in self.MSG_BODY.lower()\
			and self.MSG_BODY.lower().find(trigger) < self.MSG_BODY.lower().find('cody')\
			and self.MSG_BODY.lower().find(trigger) + len(trigger) + proximityMaximum >= self.MSG_BODY.lower().find('cody'):
			
				self.IRC.send ( 'PRIVMSG '+self.CHANNEL+' :'+random.choice(self.CODY_REPLIES)+'\r\n' )


	#joinChannel
	def joinChannel(self):
		
		if len(self.MSG_BODY) > len('!cody.join\r\n') \
		and '#' in self.MSG_BODY :
			self.IRC.send 				( 'PRIVMSG '+self.CHANNEL+' :Joining channel:'+self.MSG_BODY[len('!cody.join'):]+'\r\n')
			self.IRC.send 				( 'JOIN '+self.MSG_BODY[len('!cody.join'):]+'\r\n' )
			
		else:
			self.IRC.send('PRIVMSG '+self.CHANNEL+' :Usage: !cody.join [#channel]\r\n' )	

	#partChannel
	def partChannel(self):

		if len(self.MSG_BODY) > len('!cody.join\r\n') \
		and '#' in self.MSG_BODY :
			self.IRC.send 	( 'PRIVMSG '+self.CHANNEL+' :Leaving channel:'+self.MSG_BODY[len('!cody.part'):]+'\r\n')
			self.IRC.send 	( 'PART '+self.MSG_BODY[len('!cody.part'):]+'\r\n' )
		else:
			self.IRC.send 	('PRIVMSG '+self.CHANNEL+' :Usage: !cody.part [#channel] ' + '\r\n' )


	#codyPython    
	def codyPython(self):
		
		if len(self.MSG_BODY) > len('!cody.python\r\n'):
			pythonExpression 	= self.MSG_BODY
			pythonParseURI 		= 'http://tumbolia.appspot.com/py/'
			pyInput 			= pythonExpression[len('!cody.python '):]
			pyInput 			= pyInput.replace(' ','%20')
			pyInput 			= pyInput.replace('\\n','%0A')
			pyInput 			= pyInput.replace('\\t','%09')
			tumboliaRequest 	= Request(pythonParseURI + pyInput)  

			try:
				response = urlopen(tumboliaRequest).read()
				self.IRC.send ( 'PRIVMSG '+self.CHANNEL+' :' + response + '\r\n')
			
			except URLError, e:
				if hasattr(e, 'reason'):
					self.IRC.send ( 'PRIVMSG '+self.CHANNEL+' :Failed to reach the server. Reason: '+e.reason+' \r\n')		
				elif hasattr(e, 'code'):
					self.IRC.send ( 'PRIVMSG '+self.CHANNEL+' :The server couldn\'t fulfill the request. Reason: ' + e.code + '\r\n')
		else:
			self.IRC.send('PRIVMSG '+self.CHANNEL+' :Usage: !cody.python [python code] ' + '\r\n' )



	#cody.greeting
	def codyGreeting(self):
		
		if  self.HOME_CHANNEL in self.CHANNEL\
		and 'JOIN' in self.MSG_TYPE\
		and self.BOT_NICKNAME not in self.MSG_NICK:
			
			try:
				adminNumber 				= self.ADMIN_NICKS.index(self.NICK.lower())
				self.IRC.send 	('PRIVMSG #code :'+ str(random.choice(self.ADMIN_GREETINGS[adminNumber])) +'\r\n')
			except:
				pass
			

	#!cody.version
	def codyVersion(self):

		path 						= self.FILE_NAME #get path of currently running file, including filename
		codyVersion 				= path[-6:-3]
		self.IRC.send 					( 'PRIVMSG '+self.CHANNEL+' :I am currently running version: '+codyVersion+'\r\n' ) #print version number to IRC


	#!cody.report
	def codyReport(self):
		
		if len(self.MSG_BODY) > len(trigger + '\r\n'):
		
			codyReport				= self.MSG_BODY.split(' ', 1)
			codyReport				= codyReport[1]
		
			#OPEN FILES FOR READ AND READ THEM INTO LOCAL
			if 'bug' in trigger:
				readReport 				= open("userFeedback/bugReports.txt", "r")

			if 'feature' in trigger:
				readReport		 		= open("userFeedback/featureRequests.txt", "r")
								
			reportData 				= readReport.read().splitlines()
			startLine 				= len(reportData) / 2
			codyReport				= str(startLine) + '. ' + codyReport[:-2] + ' [' + self.NICK + ']' + '\r\n'
			reportData.append(codyReport)
				
			#WRITE STRINGS TO FILES
			if 'bug' in trigger:
				writeReport				= open("userFeedback/bugReports.txt", "w")

			if 'feature' in trigger:
				writeReport		 		= open("userFeedback/featureRequests.txt", "w")

			for element in reportData:

				print>>writeReport, reportData[int(reportData.index(element))]
			

			readReport.close()


			# REPORT THE RESULT TO CHANNEL
			if 'feature' in trigger:
				self.IRC.send 					( 'PRIVMSG '+self.CHANNEL+' :Your feature request has been saved and will be reviewed by my developers.\r\n' )
			elif 'bug' in trigger:
				self.IRC.send 					( 'PRIVMSG '+self.CHANNEL+' :Your bug has been saved and will be reviewed by my developers.\r\n' )
			else:
				self.IRC.send 					('PRIVMSG '+self.CHANNEL+' :Usage: !cody.bug [your bug report] ' + '\r\n' )


	#!cody.help
	def codyHelp(self):

		self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.CHANNEL+' :Available Commands:\r\n' )
		
		if authenticateHost(self.MSG_HOST, self.ADMIN_HOSTS):

			for lists in SESSION_DATA['PUBLIC_FUNCTIONS'], SESSION_DATA['HOME_FUNCTIONS'], SESSION_DATA['ADMIN_FUNCTIONS']:
				for trigger in lists:
					self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.CHANNEL+' :'+trigger+'\r\n' )
			
			self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.CHANNEL+' :For more information about how to use a specific command, type the command without supplying any additional information.\r\n' )

		else:

			for trigger in SESSION_DATA['PUBLIC_FUNCTIONS']:

				self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.CHANNEL+' :'+trigger+'\r\n' )
			
			self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.CHANNEL+' :For more information about how to use a specific command, type the command without supplying any additional information.\r\n' )


	#!cody.mail
	def codyMail(self):

		if len(self.MSG_BODY) > len('!cody.mail\r\n'):
			mailToPos 	= self.MSG_BODY.find('TO:') 		
			messagePos 	= self.MSG_BODY.find('MESSAGE:') 

			sendTo		= self.MSG_BODY[mailToPos  + len('TO: ') :messagePos]
			subject 	= 'Mail from ' + self.MSG_NICK + ', sent from ' + self.CHANNEL
			body 	 	= self.MSG_BODY[messagePos + len('MESSAGE: ') :]

			sender = 'cody@ec2-46-137-14-14.eu-west-1.compute.amazonaws.com'
			message = "From: "+self.MSG_NICK+' <cody@ec2-46-137-14-14.eu-west-1.compute.amazonaws.com>\nTo: '+sendTo+'<'+sendTo+'>\nSubject: '+subject+'\n'+body
			
			smtpObj = smtplib.SMTP('localhost')
			smtpObj.sendmail(sender, [sendTo], message)

			self.IRC.send('PRIVMSG '+self.CHANNEL+' :Okay '+ self.MSG_NICK + ', I\'ve sent your message to the following adress: ' + sendTo + '\r\n' )
			time.sleep(2)
		
		else:
			self.IRC.send('PRIVMSG '+self.CHANNEL+' :Usage: !cody.mail TO: [email@email.com] MESSAGE: [your message] ' + '\r\n' )


	#!cody.convert ( in ) 
	def codyConvert(self):

		findAmount 			= re.search(r'\d+', self.MSG_BODY)
		findOutputUnit		= re.search(r' in (.+)', self.MSG_BODY.lower())

		#check if any of the regex searches returned None. Calling group() on a variable == None would cause Cody to crash
		if findAmount 	   \
		and findOutputUnit :
		
			#fetch console from MESSAGE to be sent to google
			inputAmount  =  findAmount.group()
			inputUnit 	 =  self.MSG_BODY[findAmount.end() : findOutputUnit.start()]
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

				self.IRC.send('PRIVMSG '+self.CHANNEL+' :'+inputAmount+inputUnit+" = "+str(format(value, ",d"))+" cash money"+'\r\n')

				
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
				self.IRC.send('PRIVMSG '+self.CHANNEL+' :'+inputAmount+inputUnit+' = '+convertedAmount+'\r\n' )

			elif 'error: "4"' in convertedAmount:
				print "Request failed: unit not recognized"			

			elif 'error: "Unit mismatch"' in convertedAmount:
				print "Request failed: units are not related"

			else:
				pass

	
	#!cody.quit
	def codyQuit(self):
		self.IRC.send ( 'QUIT :terminating..\r\n' )
		exit()


	#!cody.fileUpdates
	def codyFileUpdates(self):     

		if '!cody.updates' in trigger\
		and self.POST_CODY_FILE_UPDATES:
			self.POST_CODY_FILE_UPDATES = False
			self.IRC.send('PRIVMSG '+self.CHANNEL+' :File updates are now turned off.\r\n')

		elif '!cody.updates' in trigger\
		and not self.POST_CODY_FILE_UPDATES:
			self.POST_CODY_FILE_UPDATES = True
			self.IRC.send('PRIVMSG '+self.CHANNEL+' :File updates are now turned on.\r\n')

		elif 'codyFileUpdates' in trigger:

			if (datetime.datetime.now().second % 3) == 0 : 
				
				#fetch filename last updated
				fetchCodyTime 	 	= 'date -r '+self.FILE_PATH

				getTimeCodyCommunicate 	 	= Popen(fetchCodyTime, 	shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
				getTimeCody, gTCComErr		= getTimeCodyCommunicate.communicate()
		 
				#lastUpdatedCody == 'Fri Feb  1 18:36:14 UTC 2013'
				lastUpdatedCody		= str(getTimeCody)
				
				lastRecorded 		= open("resources/lastupdated.db", "r")
				lastRecordedlines	= lastRecorded.read().splitlines()
				lastRecordedCody 	= lastRecordedlines[0]
				lastRecorded.close()



				if str(lastRecordedCody+'\n') != str(lastUpdatedCody):
					if self.POST_CODY_FILE_UPDATES:
						self.IRC.send('PRIVMSG '+self.HOME_CHANNEL+' :'+self.FILE_NAME+' has been updated.\r\n')
					dbWrite = open("resources/lastupdated.db", "w")
					dbWrite.write(lastUpdatedCody+lastUpdatedModules)
					dbWrite.close()

								

	def codyFeeds(self):

		#TURN OFF FEEDS
		if '!cody.feeds' in trigger \
		and self.POST_CODY_FEEDS:
			self.POST_CODY_FEEDS = False
			self.IRC.send('PRIVMSG '+self.CHANNEL+' :RSS feeds are now turned off.\r\n')

		#TURN ON FEEDS
		elif '!cody.feeds' in trigger \
		and not self.POST_CODY_FEEDS:
			self.POST_CODY_FEEDS = True
			self.IRC.send('PRIVMSG '+self.CHANNEL+' :RSS feeds are now turned on.\r\n')

	    #CHECK FOR NEW DATA 4 TIMES AN HOUR
		elif 'codyFeeds' in trigger \
		and (datetime.datetime.now().minute % 14) == 0 \
		or '!cody.feedme' in trigger:
			
			#FETCH THE FEEDS AND PREPARE DATA FOR POSTING
			#try:
				feed = feedparser.parse(RSS_FEEDS)
							
				
				#SPECIAL EXCEPTION - NYAA.EU
				feedData 	= {}
				checkfile 	= open("resources/rssFeeds.db", "r").read()
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
						with open("resources/rssFeeds.db", "w") as feedfile:
							for item in feedData.keys():
								feedfile.write('\n')
								feedfile.write(feedData[item]['content'] + '\r\n')

							feedfile.close()

					#IF NOT, JUST APPEND TO IT
					else:
						with open("resources/rssFeeds.db", "a") as feedfile:
							for item in newData:
								feedfile.write('\n')
								feedfile.write(newData[newData.index(item)] + '\r\n')

							feedfile.close()
				
				#PRINT NEW DATA TO CHANNEL
				for item in newData:
					
					self.IRC.send('PRIVMSG '+self.RSS_FEED_CHANNELS+' :' + newData[newData.index(item)] + '\r\n' )
					time.sleep(1.5)

					
			#except Exception as e:
			#	self.IRC.send('PRIVMSG '+HOME_CHANNEL+' :codyFeeds failed: '+str(e)+'\r\n' ) 


	#!cody.time

	#codyPython
	def codyTime(self):
		
		if len(self.MSG_BODY) > len('!cody.time\r\n'):

			location = self.MSG_BODY[self.MSG_BODY.find('!cody.time ')+len('!cody.time '):-len('\r\n')].title().replace(' ', '_')
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
				self.IRC.send('PRIVMSG '+self.CHANNEL+' :The current time in '+location+' is '+converted_time+'\r\n' )

			else: 
				self.IRC.send('PRIVMSG '+self.CHANNEL+' :'+str(location)+' was not found. '+'\r\n' )
			
		else:
			self.IRC.send('PRIVMSG '+self.CHANNEL+' :Usage: !cody.time [location], or !cody.time [timezone]' + '\r\n' )


if __name__ == "__main__":
	cody = Cody()
	cody.main_loop()