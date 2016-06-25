#!/usr/bin/python
#-*- coding: utf8 -*-

#usage: python cody_xxx.py restart
#error logs can be found in /var/logs/cody or C:\WINDOWS\Temp\cody

# standard pylibs
import time, os, sys, stat, inspect, random, re, smtplib, py_compile, datetime, socket, select, json, threading 
from urllib2    import Request, urlopen, URLError
from urllib     import urlencode
from subprocess import Popen, PIPE, STDOUT

# codypy libs
import codyfunctions.admin
import codyfunctions.public
import codyfunctions.home
import codyfunctions.passive
from codyfunctions.error_handling 	import writeError


# third party libs
try:
	import feedparser, 	linux_metrics
	from daemon 		import Daemon
	from pytz       	import timezone

	#from twitter    import *


except Exception as e:
	writeError("a thirdparty library did not load successfully "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

class Cody(Daemon):

	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
		
		#	start process silently 
	
		self.stdin   = stdin
		self.stdout  = stdout
		self.stderr  = stderr
		self.pidfile = pidfile

		#	MESSAGE TYPES AND COLOURCODES
		#	colour example: self.ircmsg_Color + self.ircmsg_Orange

		self.ACTIONSTART				=	"\x01ACTION "
		self.ACTIONEND					=	"\x01"
		self.ircmsg_White				=   "0"  # White 
		self.ircmsg_Black				=   "1"  # Black 
		self.ircmsg_DarkBlue			=   "2"  # Dark blue 
		self.ircmsg_DarkGreen			=   "3"  # Dark green 
		self.ircmsg_Red					=   "4"  # Red 
		self.ircmsg_DarkRed				=   "5"  # Dark red 
		self.ircmsg_DarkViolet			=   "6"  # Dark violet 
		self.ircmsg_Orange				=   "7"  # Orange 
		self.ircmsg_Yellow				=   "8"  # Yellow 
		self.ircmsg_LightGreen			=   "9"  # Light green 
		self.ircmsg_Cyan				=   "10" # Cornflower blue 
		self.ircmsg_LightCyan			=   "11" # Light cyan 
		self.ircmsg_Blue				=   "12" # Blue 
		self.ircmsg_Violet				=   "13" # Violet 
		self.ircmsg_DarkGray			=   "14" # Dark gray 
		self.ircmsg_LightGray			=   "15" # Light gray 
		self.ircmsg_Bold				= "\x02" # Bold 
		self.ircmsg_Color				= "\x03" # Color 
		self.ircmsg_Italic				= "\x09" # Italic 
		self.ircmsg_StrikeThrough		= "\x13" # Strike-Through 
		self.ircmsg_Reset				= "\x0F" # Reset 
		self.ircmsg_Underline			= "\x15" # Underline 
		self.ircmsg_Underline2			= "\x1F" # Underline 
		self.ircmsg_Reverse				= "\x16" # Reverse 

		#   SOCKETS
		self.IRC 						=   socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
		self.SOCKET_TIMEOUT				=   1

		#	ping pong, if timeout reached restart cody
		self.last_ping 					=   time.time()
		self.THRESHOLD					=   240.0 #seconds

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
		self.MONITOR_CHECK				=   100  # Prevents first run of self.codyMonitor from failing. This var will contain the last minute a check was done.
		self.ALERT_HOUR					=   100  # Prevents spamming of critical server alerts.



		#   FIGURE OUT FILE NAME
		self.FILE_NAME 					=   inspect.getfile(inspect.currentframe())
		self.FILE_PATH 					=  	os.path.abspath(self.FILE_NAME)
		self.FILE_DIR					=   self.FILE_PATH[:self.FILE_PATH.find('cody')]


		#   DECLARE TRIGGER->FUNCTION DICTIONARIES     
		self.ADMIN_FUNCTIONS 			= 	{	 '!cody.join':codyfunctions.admin.joinChannel,			'!cody.part':codyfunctions.admin.partChannel, 			'!cody.reload':codyfunctions.admin.codyReload, 	
												 '!cody.load':codyfunctions.admin.codyReload,   		'!cody.quit':codyfunctions.admin.codyQuit, 				'!cody.nick':codyfunctions.admin.codyNick,
												 '!cody.portscan':codyfunctions.admin.codyPortscan,		'!cody.diag':codyfunctions.admin.codyDiag,				'!cody.ghost':codyfunctions.admin.codyGhost,
												 '!cody.refresh':'codyRefresh'}
	
		self.PUBLIC_FUNCTIONS			=	{	 '!cody.python':codyfunctions.public.codyPython,		' cody':codyfunctions.public.hiCody,					'!cody.version':codyfunctions.public.codyVersion, 				 
												 '!cody.feature':codyfunctions.public.codyReport,		'!cody.bug':codyfunctions.public.codyReport,			'!cody.uptime':codyfunctions.public.codyUptime,
												 ' in ':codyfunctions.public.codyConvert, 				'!cody.help':codyfunctions.public.codyHelp, 			'!cody.time':codyfunctions.public.codyTime, 		 
												 'right':codyfunctions.public.rightCody, 				'!cody.name':codyfunctions.public.codyName,				'!cody.resolve':codyfunctions.public.codyResolve, 			
												 '!cody.dict':codyfunctions.public.codyGetDefinition,   '!cody.thes':codyfunctions.public.codyGetSynonyms,	 	'!cody.action':codyfunctions.public.codyAction, 			
												 '!cody.google':codyfunctions.public.codyGoogle, 		'!cody.image':codyfunctions.public.codyImage, 			'!cody.shorten':codyfunctions.public.codyShorten,
												 '!cody.roulette':codyfunctions.public.codyRoulette }
	
		self.HOME_FUNCTIONS 			=	{	 'http':codyfunctions.home.codyGetTitle    } 
	
		self.PASSIVE_FUNCTIONS			=   {	 'codyGreeting':codyfunctions.passive.codyGreeting, 		'codyFileUpdates':codyfunctions.passive.codyFileUpdates, 'codyFeeds':codyfunctions.passive.codyFeeds, 'codyMonitor':codyfunctions.passive.codyMonitor}


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


	def run(self):

		#   IRC CONNECTION

		try:

			#connect to server
			self.IRC.connect	( ( self.NETWORK_ADRESS, int(self.NETWORK_PORT) ) )
			self.IRC.send		( 'USER cody '+self.NETWORK_ADRESS+' bla :'+self.BOT_REALNAME+'\r\n' )
			self.IRC.send 		( 'NICK '+self.BOT_NICKNAME+'\r\n' )

			### BOT CONNECTS TO IRC ###
			while True:

				consoleHasData = select.select([self.IRC], [],[], self.SOCKET_TIMEOUT)

				if consoleHasData[0]:
					console = self.IRC.recv ( 4096 )
					#writeError(console)
					
				else:
					console = ''

				if 'PING' in console:
					self.IRC.send ( 'PONG ' + console.split() [ 1 ] + '\r\n' )
					self.last_ping = time.time()

				if 'Nickname is already in use.' in console:
					timeout_nick = random.randint(1,99)
					self.IRC.send( 'NICK '+self.BOT_NICKNAME+str(timeout_nick)+'\r\n' )
				
				if (time.time() - self.last_ping) > self.THRESHOLD:
					self.IRC.send ( 'PING ' + str(random.randint(10000,99999)) + '\r\n' )
					self.last_ping = time.time()

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
							thread = threading.Thread(target=functionToRun, args=(self, trigger)) 	
							thread.start()



					## CHECKING IF ANY OF THE HOME FUNCTION TRIGGERS APPEAR IN MESSAGE BODY
					for trigger in self.HOME_FUNCTIONS.keys():

						if  trigger in self.MSG_BODY  \
						and self.HOME_CHANNEL in self.MSG_CHANNEL :

							functionToRun = self.HOME_FUNCTIONS[trigger]
							thread = threading.Thread(target=functionToRun, args=(self, trigger)) 	
							thread.start()
					


					## CHECKING IF ANY OF THE ADMIN FUNCTION TRIGGERS APPEAR IN MESSAGE BODY
					for trigger in self.ADMIN_FUNCTIONS.keys():

						if   trigger in self.MSG_BODY  \
						and  self.authenticateHost():

							functionToRun = self.ADMIN_FUNCTIONS[trigger]
							thread = threading.Thread(target=functionToRun, args=(self, trigger)) 	
							thread.start()

							## RELOAD MODULES EXCEPTION
							if 'refresh' in trigger:

								try:
									#functions inside modules are not reload!
									reload(codyfunctions.admin)
									reload(codyfunctions.public)
									reload(codyfunctions.home)
									reload(codyfunctions.passive)
									reload(codyfunctions.error_handling)
									self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :All modules reloaded successfully.\r\n")

								except Exception as e:
									writeError("CRITICAL: refresh() in main loop "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))								



					## EXECUTE ALL PASSIVE FUNCTIONS
					for trigger in self.PASSIVE_FUNCTIONS.keys():

						functionToRun = self.PASSIVE_FUNCTIONS[trigger]
						thread = threading.Thread(target=functionToRun, args=(self, trigger)) 	
						thread.start()



				## RELEASE THE FRAME
				time.sleep(0.001)

		except Exception as e:
			writeError("CRITICAL: self.run() in cody_dev.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))


	def readConfig(self):

		config = open(self.FILE_DIR+'cody.cfg', 'r').read().splitlines()

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

	#create_file(file_name)+" line "+str((sys.exc_info()[2]).tb_lineno)): makes a file.
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

			except Exception as e:
				#writeError("INFORMATION: channel regex in cody_dev.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))
				pass
			
			#then return everything
			return [NICK, HOSTNAME, MSG_TYPE, CHANNEL, MESSAGE]
		
		else:
			#DO NOT PARSE
			return ['NULL','NULL','NULL','NULL','NULL']

if __name__ == "__main__":
	daemon = Cody('/tmp/cody_process.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)