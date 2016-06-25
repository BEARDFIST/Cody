#!/usr/bin/python
#-*- coding: utf8 -*-
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
												 '!cody.updates':self.codyFileUpdates, 	'!cody.feeds':self.codyFeeds, 			'!cody.feedme':self.codyFeeds,     
												 '!cody.portscan':self.portscan }
	
		self.PUBLIC_FUNCTIONS			=	{	 '!cody.python':self.codyPython,		' cody':self.hiCody,					'!cody.version':self.codyVersion, 				 
												 '!cody.feature':self.codyReport,		'!cody.bug':self.codyReport,			'!cody.uptime':self.codyUptime,
												 ' in ':self.codyConvert, 				'!cody.help':self.codyHelp, 			'!cody.time':self.codyTime, 		 
												 '!cody.kickstarter':self.kickstarter,	'right':self.RightCody, 				'!cody.name':self.name,
												 '!cody.resolve':self.resolve, 			'!cody.dict':self.get_definition,       '!cody.thes':self.get_synonyms,
												 '!cody.delrio':self.delrio }
	
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
		self.ADMIN_HOSTS				=	self.CONFIGURATION['ADMIN_HOSTS']
		self.ADMIN_NICKS				=	self.CONFIGURATION['ADMIN_NICKS']
		self.CODY_REPLY_TRIGGERS		=	self.CONFIGURATION['CODY_REPLY_TRIGGERS']
		self.CODY_REPLIES 				=	self.CONFIGURATION['CODY_REPLIES']
		self.CODY_INSULTS 				=	self.CONFIGURATION['CODY_INSULTS']
		self.RSS_FEEDS 					=  	self.CONFIGURATION['RSS_FEEDS']
		self.RSS_FEED_CHANNELS			=  	self.CONFIGURATION['RSS_FEED_CHANNELS']
		self.ADMIN_GREETINGS 			=[ 	self.CONFIGURATION['ADMIN1_GREETINGS'], self.CONFIGURATION['ADMIN2_GREETINGS'], 
								  			self.CONFIGURATION['ADMIN3_GREETINGS'], self.CONFIGURATION['ADMIN4_GREETINGS'] ]

		#	IF WE'RE RUNNING THE DEV VERSION, CONNECT ONLY TO THE HOME_CHANNEL
		if 'dev' in self.FILE_NAME:
			self.BOT_CHANNELS 			=   self.CONFIGURATION['HOME_CHANNEL']


	def delrio(self, trigger):

		self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :delrio, quit your job.\r\n')
		time.sleep(5)
		self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :you will never be a guy if you don\'t quit your job.\r\n')
		time.sleep(5)
		self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :if you don\'t quit your job, I\'m going to cry.\r\n')



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
						
						functionToRun = self.PUBLIC_FUNCTIONS[trigger]
						functionToRun(trigger)


				## CHECKING IF ANY OF THE HOME FUNCTION TRIGGERS APPEAR IN MESSAGE BODY
				for trigger in self.HOME_FUNCTIONS.keys():

					if  trigger in self.MSG_BODY  \
					and self.HOME_CHANNEL in self.MSG_CHANNEL :

						functionToRun = self.HOME_FUNCTIONS[trigger]
						functionToRun(trigger)					


				## CHECKING IF ANY OF THE ADMIN FUNCTION TRIGGERS APPEAR IN MESSAGE BODY
				for trigger in self.ADMIN_FUNCTIONS.keys():

					if   trigger in self.MSG_BODY  \
					and  self.authenticateHost():

						functionToRun = self.ADMIN_FUNCTIONS[trigger]
						functionToRun(trigger)


				## EXECUTE ALL PASSIVE FUNCTIONS
				for trigger in self.PASSIVE_FUNCTIONS.keys():

					functionToRun = self.PASSIVE_FUNCTIONS[trigger]
					functionToRun(trigger)


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

	def getTitle(self, trigger):

		URLstart = self.MSG_BODY.find("http://")
		URLend = self.MSG_BODY[URLstart:].find(' ')
		url = self.MSG_BODY[URLstart:URLend]

		try:
			page = urlopen(url).read()
			title = page[page.find("<title>")+len("<title>"):page.find('</title>')]
			if len(title) < 50:
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :'+title+'\r\n')
			else:
				print 'title was too big to post'
					
		except:
			print 'failed to get title'


	#!cody.uptime
	def codyUptime(self, trigger):

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
	        
		self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :I\'ve been awake for ' + str(uptimeString) + '. I last woke up ' + self.DATE + '\r\n' )
		

	#!cody.reload
	def codyReload(self, trigger):

		if len(self.MSG_BODY) > len(trigger + '\r\n'):
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
						
			except py_compile.PyCompileError as e:
				errorMessage = str(e)
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :'+errorMessage+'. \r\n' )

			else:
				os.chmod(folderPath + newCody, stat.S_IRWXU)
				self.IRC.send ( 'QUIT :reloading myself\r\n' )
				exec(open(folderPath + newCody))
		

		else:
			self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :File not found! \r\n' )	


	#hiCody
	def hiCody(self, trigger):

		proximityMaximum = 3

		for trigger in self.CODY_REPLY_TRIGGERS:
			if trigger in self.MSG_BODY.lower()\
			and self.MSG_BODY.lower().find(trigger) < self.MSG_BODY.lower().find('cody')\
			and self.MSG_BODY.lower().find(trigger) + len(trigger) + proximityMaximum >= self.MSG_BODY.lower().find('cody'):
			
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :'+random.choice(self.CODY_REPLIES)+'\r\n' )


	#joinChannel
	def joinChannel(self, trigger):
		
		if len(self.MSG_BODY) > len(trigger + '\r\n') \
		and '#' in self.MSG_BODY :
			self.IRC.send 				( 'PRIVMSG '+self.MSG_CHANNEL+' :Joining channel:'+self.MSG_BODY[len('!cody.join'):]+'\r\n')
			self.IRC.send 				( 'JOIN '+self.MSG_BODY[len('!cody.join'):]+'\r\n' )
			
		else:
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.join [#channel]\r\n' )	

	#partChannel
	def partChannel(self, trigger):

		if len(self.MSG_BODY) > len('!cody.join\r\n') \
		and '#' in self.MSG_BODY :
			self.IRC.send 	( 'PRIVMSG '+self.MSG_CHANNEL+' :Leaving channel:'+self.MSG_BODY[len('!cody.part'):]+'\r\n')
			self.IRC.send 	( 'PART '+self.MSG_BODY[len('!cody.part'):]+'\r\n' )
		else:
			self.IRC.send 	('PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.part [#channel] ' + '\r\n' )


	#codyPython    
	def codyPython(self, trigger):
		
		if len(self.MSG_BODY) > len(trigger + '\r\n'):
			pythonExpression 	= self.MSG_BODY
			pythonParseURI 		= 'http://tumbolia.appspot.com/py/'
			pyInput 			= pythonExpression[len('!cody.python '):]
			pyInput 			= pyInput.replace(' ','%20')
			pyInput 			= pyInput.replace('\\n','%0A')
			pyInput 			= pyInput.replace('\\t','%09')
			tumboliaRequest 	= Request(pythonParseURI + pyInput)  

			try:
				response = urlopen(tumboliaRequest).read()
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :' + response + '\r\n')
			
			except URLError, e:
				if hasattr(e, 'reason'):
					self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :Failed to reach the server. Reason: '+e.reason+' \r\n')		
				elif hasattr(e, 'code'):
					self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :The server couldn\'t fulfill the request. Reason: ' + e.code + '\r\n')
		else:
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.python [python code] ' + '\r\n' )



	#cody.greeting
	def codyGreeting(self, trigger):
		
		if  self.HOME_CHANNEL in self.MSG_CHANNEL\
		and 'JOIN' in self.MSG_TYPE\
		and self.BOT_NICKNAME not in self.MSG_NICK:
			
			try:
				adminNumber 				= self.ADMIN_NICKS.index(self.MSG_NICK.lower())
				self.IRC.send 	('PRIVMSG #code :'+ str(random.choice(self.ADMIN_GREETINGS[adminNumber])) +'\r\n')
			except:
				pass
			

	#!cody.version
	def codyVersion(self, trigger):

		path 						= self.FILE_NAME #get path of currently running file, including filename
		codyVersion 				= path[-6:-3]
		self.IRC.send 					( 'PRIVMSG '+self.MSG_CHANNEL+' :I am currently running version: '+codyVersion+'\r\n' ) #print version number to IRC


	#!cody.report
	def codyReport(self, trigger):
		
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
			codyReport				= str(startLine) + '. ' + codyReport[:-2] + ' [' + self.MSG_NICK + ']' + '\r\n'
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
				self.IRC.send 					( 'PRIVMSG '+self.MSG_CHANNEL+' :Your feature request has been saved and will be reviewed by my developers.\r\n' )
			elif 'bug' in trigger:
				self.IRC.send 					( 'PRIVMSG '+self.MSG_CHANNEL+' :Your bug has been saved and will be reviewed by my developers.\r\n' )
			else:
				self.IRC.send 					('PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.bug [your bug report] ' + '\r\n' )


	#!cody.help
	def codyHelp(self, trigger):

		self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.MSG_CHANNEL+' :Available Commands:\r\n' )
		
		if self.authenticateHost():

			for lists in self.PUBLIC_FUNCTIONS, self.HOME_FUNCTIONS, self.ADMIN_FUNCTIONS:
				for trigger in lists:
					self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.MSG_CHANNEL+' :'+trigger+'\r\n' )
			
			self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.MSG_CHANNEL+' :For more information about how to use a specific command, type the command without supplying any additional information.\r\n' )

		else:

			for trigger in self.PUBLIC_FUNCTIONS:

				self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.MSG_CHANNEL+' :'+trigger+'\r\n' )
			
			self.IRC.send ( 'NOTICE '+self.MSG_NICK+' '+self.MSG_CHANNEL+' :For more information about how to use a specific command, type the command without supplying any additional information.\r\n' )


	#!cody.mail
	def codyMail(self, trigger):

		if len(self.MSG_BODY) > len(trigger + '\r\n'):
			mailToPos 	= self.MSG_BODY.find('TO:') 		
			messagePos 	= self.MSG_BODY.find('MESSAGE:') 

			sendTo		= self.MSG_BODY[mailToPos  + len('TO: ') :messagePos]
			subject 	= 'Mail from ' + self.MSG_NICK + ', sent from ' + self.MSG_CHANNEL
			body 	 	= self.MSG_BODY[messagePos + len('MESSAGE: ') :]

			sender = 'cody@ec2-46-137-14-14.eu-west-1.compute.amazonaws.com'
			message = "From: "+self.MSG_NICK+' <cody@ec2-46-137-14-14.eu-west-1.compute.amazonaws.com>\nTo: '+sendTo+'<'+sendTo+'>\nSubject: '+subject+'\n'+body
			
			smtpObj = smtplib.SMTP('localhost')
			smtpObj.sendmail(sender, [sendTo], message)

			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :Okay '+ self.MSG_NICK + ', I\'ve sent your message to the following adress: ' + sendTo + '\r\n' )
			time.sleep(2)
		
		else:
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.mail TO: [email@email.com] MESSAGE: [your message] ' + '\r\n' )


	#!cody.convert ( in ) 
	def codyConvert(self, trigger):

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

				self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :'+inputAmount+inputUnit+" = "+str(format(value, ",d"))+" cash money"+'\r\n')

				
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
				self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :'+inputAmount+inputUnit+' = '+convertedAmount+'\r\n' )

			elif 'error: "4"' in convertedAmount:
				print "Request failed: unit not recognized"			

			elif 'error: "Unit mismatch"' in convertedAmount:
				print "Request failed: units are not related"

			else:
				pass

	
	#!cody.quit
	def codyQuit(self, trigger):
		self.IRC.send ( 'QUIT :terminating..\r\n' )
		exit()


	#!cody.fileUpdates
	def codyFileUpdates(self, trigger):     

		if '!cody.updates' in trigger\
		and self.POST_CODY_FILE_UPDATES:
			self.POST_CODY_FILE_UPDATES = False
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :File updates are now turned off.\r\n')

		elif '!cody.updates' in trigger\
		and not self.POST_CODY_FILE_UPDATES:
			self.POST_CODY_FILE_UPDATES = True
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :File updates are now turned on.\r\n')

		elif 'codyFileUpdates' in trigger:

			if (datetime.datetime.now().second % 3) == 0 : 
				
				#fetch current file update time - syntax is 'Sun Apr 21 20:24:36 2013'
				lastUpdatedRealTime = time.ctime(os.path.getmtime(self.FILE_PATH))
				lastUpdatedCody 	= lastUpdatedRealTime.split()
				
				#fetch last recorded update time
				lastRecorded 		= open("resources/lastupdated.db", "r")
				lastRecordedCody	= lastRecorded.read().split()
				lastRecorded.close()
				
				#parse recorded time into datetime ints
				if len(lastRecordedCody) == 5:
					lastRecordedYear 	= int(lastRecordedCody[4])
					lastRecordedMonth   = int(time.strptime(lastRecordedCody[1],'%b').tm_mon)
					lastRecordedDay		= int(lastRecordedCody[2])
					lastRecordedTime 	= lastRecordedCody[3].split(':')
					lastRecordedHour	= int(lastRecordedTime[0])
					lastRecordedMinute	= int(lastRecordedTime[1])
					lastRecordedSecond	= int(lastRecordedTime[2])

				#parse current time into datetime ints
				lastUpdatedYear 	= int(lastUpdatedCody[4])
				lastUpdatedMonth    = int(time.strptime(lastUpdatedCody[1],'%b').tm_mon)
				lastUpdatedDay		= int(lastUpdatedCody[2])
				lastUpdatedTime 	= lastUpdatedCody[3].split(':')
				lastUpdatedHour		= int(lastUpdatedTime[0])
				lastUpdatedMinute	= int(lastUpdatedTime[1])
				lastUpdatedSecond	= int(lastUpdatedTime[2])

				#turn them both into datetime objects
				if len(lastRecordedCody) == 5:
					lastRecordedCody 	= datetime.datetime(lastRecordedYear, lastRecordedMonth, lastRecordedDay, lastRecordedHour, lastRecordedMinute, lastRecordedSecond)

				else: 
					lastRecordedCody 	= datetime.datetime(2000,1,1)
				
				lastUpdatedCody 	= datetime.datetime(lastUpdatedYear,  lastUpdatedMonth,  lastUpdatedDay,  lastUpdatedHour, 	lastUpdatedMinute, 	lastUpdatedSecond)

				#check if it has changed
				if lastRecordedCody < lastUpdatedCody :
					if self.POST_CODY_FILE_UPDATES:
						self.IRC.send('PRIVMSG '+self.HOME_CHANNEL+' :'+self.FILE_NAME+' has been updated.\r\n')
					dbWrite = open("resources/lastupdated.db", "w")
					dbWrite.write(lastUpdatedRealTime)
					dbWrite.close()

								

	def codyFeeds(self, trigger):

		#TURN OFF FEEDS
		if '!cody.feeds' in trigger \
		and self.POST_CODY_FEEDS:
			self.POST_CODY_FEEDS = False
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :RSS feeds are now turned off.\r\n')

		#TURN ON FEEDS
		elif '!cody.feeds' in trigger \
		and not self.POST_CODY_FEEDS:
			self.POST_CODY_FEEDS = True
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :RSS feeds are now turned on.\r\n')

	    #CHECK FOR NEW DATA 4 TIMES AN HOUR
		elif 'codyFeeds' in trigger \
		and (datetime.datetime.now().minute % 14) == 0 \
		or '!cody.feedme' in trigger:
			
			#FETCH THE FEEDS AND PREPARE DATA FOR POSTING
			#try:
				feed = feedparser.parse(self.RSS_FEEDS)
							
				
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
	def codyTime(self, trigger):
		
		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			location 	= self.MSG_BODY[self.MSG_BODY.find('!cody.time ')+len('!cody.time '):-len('\r\n')].title().replace(' ', '_')
			format 		= "%H:%M UTC%z"
			local_time 	= datetime.datetime.now(timezone('UTC'))
			offset 		= ''
			match_found = False
			exceptions  = {'CST':'Central', 'PST':'Pacific', 'MST':'Mountain', 'EST':'Eastern', \
						   'CDT':'UTC-5',   'PDT':'UTC-7',   'MDT':'UTC-6',    'EDT':'UTC-4' }
			zones 		= ['Europe/', 'America/', 'Australia/', 'Pacific/', 'Asia/', 'Africa/', 
						   'US/', 	  'Canada/',  'Atlantic/']



			#MAKE EXCEPTIONS FOR COMMON TIMEZONES WITH WEIRD NAMES
			if location.upper() in exceptions.keys():
				location = exceptions[location.upper()]

			#FIGURE OUT THE CONTINENT BY TRYING THEM ALL
			for zone in zones:

				try:
					converted_time = local_time.astimezone(timezone(zone+location)).strftime(format)
					match_found = True
									
				except:
					continue

				
			if not match_found:
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
				self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :The current time in '+location+' is '+converted_time+'\r\n' )

			else: 
				self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :'+str(location)+' was not found. '+'\r\n' )
			
		else:
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.time [location], or !cody.time [timezone]' + '\r\n' )

	def kickstarter(self, trigger):

		def IntCutter(fullstring, starter, ender):
			stringAndSuffix = fullstring.partition(starter)
			stringpart		= str(stringAndSuffix[2]).partition(ender)
			stringsplit		= stringpart[0].split(".")

			return stringsplit[0]


		if len(self.MSG_BODY) > len('!cody.kickstarter\r\n'):
			if "/projects/" in self.MSG_BODY:
				 projectToAddsplit = self.MSG_BODY.split(" ")
				 if len(projectToAddsplit) != 3:
				 	self.IRC.send('NOTICE '+self.MSG_NICK+' '+self.MSG_CHANNEL+' :Could not add project. Remember to give the project a name after the url: "!cody.ks /project/blabla name_here"' )


				 else:
				 	kickfile = open('resources/kickstarter.db', 'a')
				 	kickfile.write(projectToAddsplit[1]+"="+projectToAddsplit[2]+'\r\n')
				 	kickfile.close()

			if "projects/" not in self.MSG_BODY:
				projectsplit = self.MSG_BODY.split(" ")	
				if len(projectsplit) == 2:
					
					kickfile = open('resources/kickstarter.db', 'r')
					for line in kickfile.read().splitlines():
						if len(line) != 0:
							projectandname = line.split("=")

							one = projectsplit[1].strip("\r\n").lower()
							two = projectandname[1].lower()

							if str(one) == str(two):
								projectname 		= projectandname[1]
								kickstarterpage 	= projectandname[0]

								website				= "http://www.kicktraq.com"
								fullurl				= website+kickstarterpage

								req 				= Request(fullurl)
								req.add_header		('User-agent', 'Mozilla 5.10')
								result 				= urlopen(req)
								html 				= result.read()

								if "Funding Unsuccessful" in html:
									funded = IntCutter(html, 'Funded: ', '<br />')
									self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+ ' :'+projectname+" was unsuccessful with: "+funded+'\r\n')

								elif "Funding Successful" in html:
									funded = IntCutter(html, 'Funded: ', '<br />')
									self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+ ' :'+projectname+" got successfully funded with: "+funded+'\r\n')

								else:
									funded				= IntCutter(html, 'Funding: ', '<br />')
									backers 			= IntCutter(html, 'Backers: ', '<br />' )
									averagedaily		= IntCutter(html, 'Average Daily Pledges: ', '<br />')
									averageperbacker	= IntCutter(html, 'Average Pledge Per Backer: ', '<br />')
									day 				= IntCutter(html, 'clock-days">0', '<span class="timedesc">days')
									hour 				= IntCutter(html, 'clock-hours">', '<span class="timedesc">hours')
									minute 				= IntCutter(html, 'clock-mins">', '<span class="timedesc">minutes')
									
									self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+ ' :' 										+projectname+ 
																				' Funding: ' 								+funded+
																				' - Backers: '								+backers+
																				' - Average daily: '						+averagedaily+
																				' - Average per backer: '					+averageperbacker+
																				' - Time left: '							+day+
																				' days '									+hour+
																				':'											+minute+
																				' hours - website: http://kickstarter.com'	+kickstarterpage+
																															'\r\n')
					kickfile.close()

		else:
			kickfile = open('resources/kickstarter.db', 'r')
			for line in kickfile.read().splitlines():
				projectsadded = line.split("=")
				if len(projectsadded) > 1:
					self.IRC.send('NOTICE '+self.MSG_NICK+' '+self.MSG_CHANNEL+ ' :'+projectsadded[1]+'\r\n')
			kickfile.close()
			self.IRC.send('NOTICE '+self.MSG_NICK+' '+self.MSG_CHANNEL+ ' :'+"To add a kickstarter: !cody.kickstarter /project/project-project-blabla name_of_project"+'\r\n')

	def RightCody(self, trigger):
		if "cody?" in self.MSG_BODY.lower():
			self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :trufax bro\r\n")

	def name(self, trigger):
		
		length 		= random.randint(1,8)
		consonants 	= ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','x','z']
		vowels 		= ['a','e','i','o','u','y']
		word 		= ""
		i 			= 0
		
		while length >= i: 
			intC = random.randint(0,18)
			intV = random.randint(0,5)

			if i%2 != 0:
				word += vowels[intV]

			if i%2 == 0:
				word += consonants[intC]
			i = i+1

		word = word.title()
		
		self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :"+word+"\r\n")

	def portscan(self, trigger):

		if len(self.MSG_BODY) > len(trigger + '\r\n'):
			if "/" not in self.MSG_BODY \
			and "," not in self.MSG_BODY \
			and "-" not in self.MSG_BODY:

				commandinput = self.MSG_BODY.split(' ')
				
				if len(commandinput) == 3:

					ip = str(commandinput[2][:-len('\r\n')])
					port = str(commandinput[1])
					cmd = ["nmap","-PN", "-p", port, ip]

					pro = Popen(cmd, stdout = PIPE, stderr = PIPE)

					output = pro.communicate()

					if output[0]:
						yanked 				= output[0]
						splityank 			= yanked.partition("SERVICE")
						
						print splityank[2]

						if "MAC" in splityank[2]:
							splityankagain 	= splityank[2].partition("MAC")
							result 			= splityankagain[0]
							result 			= result.split()

						else:
							splityankagain 	= splityank[2].partition("Nmap")
							result 			= splityankagain[0]
							
							if result:
								result 		= result.split()

						if len(result) > 0:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :port: "+str(result[0])+" state: "+str(result[1])+"\r\n")

						else:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :no information could be retrieved\r\n")
					else:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :service not available\r\n")
				else:		
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :wrong command, try again\r\n")
			else:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :Illegal character detected\r\n")
		else:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :usage: !cody.portscan <portnumber> <ipaddress>\r\n")

	def resolve(self, trigger):

		if len(self.MSG_BODY) > len(trigger + '\r\n'):
			commandinput 	= self.MSG_BODY.split(' ')
			nameToResolve 	= str(commandinput[1][:-len('\r\n')])
			cmd 			= ["host", nameToResolve]
			pro 			= Popen(cmd, stdout = PIPE, stderr = PIPE)
			output			= pro.communicate()

			if output[0]:
				resolvedoutput 	= str(output[0]).split(' ')


				if "not" not in str(output):
					if "pointer" in resolvedoutput[3]:
						replaced = resolvedoutput[3].replace("pointer", resolvedoutput[4])
						self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :"+nameToResolve+" resolved to "+str(replaced)+"\r\n")
						
					else:
						self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :"+nameToResolve+" resolved to "+str(resolvedoutput[3])+"\r\n")

				else:
					self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :could not resolve "+str(nameToResolve)+"\r\n")
			else:
				self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :"+str(nameToResolve)+" returned an empty string, sorry."+"\r\n")
		else:
			self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :usage: !cody.resolve <hostname.com> or <ipaddress>\r\n")


	def get_definition(self, trigger):

		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			word 			= self.MSG_BODY.split()[1]

			url_prefix 		= 'http://dictionary.reference.com/browse/'
			page 			= urlopen(url_prefix + word).read()
			wordtype_start 	= page.find('<span class="pg">') + len('<span class="pg">')
			wordtype_end	= page[wordtype_start:].find('</span>') + wordtype_start
			def_start       = page.find('<meta name="description" content="') + len('<meta name="description" content="')
			def_end			= page.find('See more."/>')

			if def_end < 0:
				self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + random.choice(self.CODY_INSULTS) + "\r\n")

			else:

				wordtype 		= page[wordtype_start:wordtype_end].replace(' ', '')
				wordtype 		= wordtype.replace(',', '')
				definition  	= page[def_start:def_end].split(', ')[1]

				self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + wordtype + '; ' + definition + "\r\n")

		else:
			self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :Usage: !cody.dict <word to look up>\r\n")

	def get_synonyms(self, trigger):

		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			word 			= self.MSG_BODY.split()[1]

			url_prefix		= 'http://thesaurus.com/browse/'
			page 			= urlopen(url_prefix + word).read()

			print 'url = ' + url_prefix + word
			print 'thesaurus results?' + str('no thesaurus results' in page)

			if 'no thesaurus results' in page:
				self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + random.choice(self.CODY_INSULTS) + "\r\n")

			else:

				#locate synonyms
				syns_start 		= page.find('<div class="relevancy-list">') + len('<div class="relevancy-list"> ')
				syns_end		= page[syns_start:].find('<div id="filter-0">') + syns_start

				synonyms_list   = page[syns_start:syns_end].split('<span class="text">')

				result_list 	= []

				for synonym in synonyms_list[1:]:

					result_list.append(synonym[:synonym.find('</span>')])

				return_string   = '\"' + word + '\"' + ' has the following synonyms: '
			 
			 	for result in result_list:

			 		if len(result_list) != 10:

				 		if result_list.index(result) != len(result_list) - 1:

				 			return_string += result + ', '

				 		else:

				 			return_string += result


			 	self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + return_string + "\r\n")

		else:
			self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :Usage: !cody.thes <word to look up>\r\n")


if __name__ == "__main__":
	cody = Cody()
	cody.main_loop()