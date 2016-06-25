#twisted imports
from twisted.words.protocols 	import irc
from twisted.internet 			import reactor, protocol, task

# system imports
import time, sys, random, glob, os, inspect, datetime

#local imports
import botfunctions

class Client(irc.IRCClient):
	"""An IRC client."""
	
	def __init__(self, cfg):

		#read the .cfg file
		self.cfg = self.readConfig(cfg)

		"""     self.NICKSERV_ADRESS    =   self.CONFIGURATION['NICKSERV_ADRESS']
		self.NETWORK_ADRESS             =   self.CONFIGURATION['NETWORK_ADRESS']
		self.NETWORK_PORT               =   self.CONFIGURATION['NETWORK_PORT']
		self.BOT_NICKNAME               =   self.CONFIGURATION['BOT_NICKNAME']
		self.BOT_REALNAME               =   self.CONFIGURATION['BOT_REALNAME']
		self.AUTH_PASS                  =   self.CONFIGURATION['AUTH_PASS']
		self.BOT_CHANNELS               =   self.CONFIGURATION['BOT_CHANNELS']
		self.HOME_CHANNEL               =   self.CONFIGURATION['HOME_CHANNEL']
		self.HOME_CHANNEL_PASSWORD      =   self.CONFIGURATION['HOME_CHANNEL_PASSWORD']
		self.LOG_PATH                   =   self.CONFIGURATION['LOG_PATH']
		self.ADMIN_HOSTS                =   self.CONFIGURATION['ADMIN_HOSTS']
		self.ADMIN_NICKS                =   self.CONFIGURATION['ADMIN_NICKS']
		self.CODY_REPLY_TRIGGERS        =   self.CONFIGURATION['CODY_REPLY_TRIGGERS']
		self.CODY_REPLIES               =   self.CONFIGURATION['CODY_REPLIES']
		self.CODY_INSULTS               =   self.CONFIGURATION['CODY_INSULTS']
		self.RSS_FEEDS                  =   self.CONFIGURATION['RSS_FEEDS']
		self.RSS_FEED_CHANNELS          =   self.CONFIGURATION['RSS_FEED_CHANNELS']
		self.ADMIN_GREETINGS            =[  self.CONFIGURATION['ADMIN1_GREETINGS'], self.CONFIGURATION['ADMIN2_GREETINGS'], 
											self.CONFIGURATION['ADMIN3_GREETINGS'], self.CONFIGURATION['ADMIN4_GREETINGS'] ]"""

		#set important member variables
		self.nickname 		  =  self.cfg["NICKNAME"]
		self.home_channel 	  =  self.cfg["HOME_CHANNEL"]
		self.google_api		  =  self.cfg["GOOGLE_API"]

		#set time globals
		self.NOW 			  =  datetime.datetime.now() 
		self.START_TIME		  =  time.time()
		self.YEAR			  =  self.NOW.year
		self.MONTH			  =  self.NOW.month   
		self.DAY 			  =  self.NOW.day 
		self.DATE 			  =  str(self.DAY) + '/' + str(self.MONTH) + '-' + str(self.YEAR)

		#   FIGURE OUT FILE NAME
		self.FILE_NAME 					=   inspect.getfile(inspect.currentframe())
		self.FILE_PATH 					=  	os.path.abspath(self.FILE_NAME)
		self.FILE_DIR					=   self.FILE_PATH[:self.FILE_PATH.find('cody')]

		#functionality objects
		self.public   		  =  botfunctions.Public(self)

		#declare function dictionaries
		self.PUBLIC_FUNCTIONS			=	{	 '.short':self.public.shorten_url, 	'.uptime':self.public.uptime, 		'right '+self.nickname.lower():self.public.decide,
												 '.google':self.public.google, 	    '.g':self.public.google, 			'.python':self.public.python,
												 '.py':self.public.python, 	        '.version':self.public.version,     '.help':self.listFunctions	}



	# helper functions
	def readConfig(self, path):
		'''reads the .cfg file located at path and returns a dictionary with its keys and values'''

		config = open(path, 'r').read().splitlines()

		configDict = {}
		i = 1

		for line in config:

			#set up identifiers
			equalsPos = line.find('=')
			lineValue = line[equalsPos + 1:]
			lineSetting = line[:equalsPos]

			#handle special exceptions
			#if 'REPLY_TRIGGERS' in lineSetting:
				#lineValue = lineValue + ' '

			#if 'CHANNEL' in lineSetting:
				#lineValue = lineValue.replace(';',',')


			#if there are multiple values, split them into a list
			if ';' in lineValue \
			and '=' in line:
				configDict[lineSetting] = lineValue.split(';')

			#if there isn't, just assign them.
			elif '=' in line:
				configDict[lineSetting] = lineValue


		return configDict	

	def writeError(self, errorMessage):
		logpath = '/log/'+self.nickname+'.log'

		timestamp = time.time()
		timenow   = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

		if os.path.exists(logpath):
			with open(logpath,'a') as log: #append
				log.write(timenow +" : "+ errorMessage+'\r\n')
			log.close

		else:
			with open(logpath,'w') as log: #append
				log.write(timenow +" : "+ errorMessage+'\r\n')
			log.close


	def listFunctions(self):

		functions = self.PUBLIC_FUNCTIONS
		display_f = []
		display_t = []

		for function in functions.keys():

			function_name = str(functions[function]).split()[2]

			if function[0] == '.' and function_name not in display_f:

				display_t.append(function)
				display_f.append(function_name)

		return 'Available functions: '+', '.join(display_t)+'. To learn more about a specific function, simply run it.'

	# callbacks for events - these are called automatically by Twisted when an event occurs    
	def connectionMade(self):
		irc.IRCClient.connectionMade(self)

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
   
	def signedOn(self):
		"""Called when bot has succesfully signed on to server."""
		self.join(self.home_channel)

	def joined(self, channel):
		"""This will get called when the bot joins the channel."""
		return

	def callFunction(self, msg, functions):
		'''calls a function from the provided function dictionary'''

		if msg[0] == '.' or 'right' in msg and self.nickname.lower() in msg.lower():
			for trigger in functions:

				if trigger in msg.lower():

					try:
						
						#strip out the trigger
						msg = msg.split(' ', 1)[1]

						#call the relevant function
						msg = self.PUBLIC_FUNCTIONS[trigger](msg)

						#post its return
						return msg

					#user didn't type anything after the trigger
					except (IndexError, TypeError):
						
						#check if the function requires input or not
						try:
							#call the relevant function with no input
							msg = functions[trigger]()

							#return it
							return msg

						except:
							#if the function requires input, inform the user of usage
							use = functions[trigger].__doc__
							return use

					#something else went wrong
					except Exception as e:
						err = "'" + trigger + "' in botfunctions.py: "+str(e)+" (line "+str(sys.exc_traceback.tb_lineno)+")"
						self.writeError(err)
						return str(e)

		else:
			return None
					


	def privmsg(self, user, channel, msg):
		"""This will get called when the bot receives a message."""

		#turn Nick!userid@host.host into Nick
		user = user.split('!', 1)[0]

		#save trigger
		trigger = msg.split()[0]

		try:
		
			# check if any of the triggers are found in the input
			msg = self.callFunction(msg, self.PUBLIC_FUNCTIONS)

		except Exception as e:

			msg = str(e)


		if msg:
			print msg
			# Check to see if they're sending me a private message
			if channel == self.nickname:
				self.msg(user, msg)
			

			#handle .help
			elif trigger == '.help':
				self.notice(user, msg)
			
			#public message
			else:
				self.msg(channel, msg)

			


	def action(self, user, channel, msg):
		"""This will get called when the bot sees someone do an action."""
		return

	# irc callbacks

	def irc_NICK(self, prefix, params):
		"""Called when an IRC user changes their nickname."""
		#old_nick = prefix.split('!')[0]
		#new_nick = params[0]
		return


	# For fun, override the method that determines how a nickname is changed on
	# collisions. The default method appends an underscore.
	def alterCollidedNick(self, nickname):
		"""
		Generate an altered version of a nickname that caused a collision in an
		effort to create an unused related name for subsequent registration.
		"""
		return nickname + str(random.randint(11,100))

	#on-demand methods
	def announce(self):
		msg = "ten seconds have passed!"
		channel = "#test"
		self.msg(channel, msg)

class ClientFactory(protocol.ClientFactory):
	"""A factory for IRC clients.

	A new protocol instance will be created each time we connect to the server.
	"""

	def __init__(self, cfg):
		self.clients    = []
		self.cfg_file   = cfg
		#self.lc         = task.LoopingCall(self.announce)
		#self.lc.start(10)


	def announce(self):
		
		for client in self.clients:

			client.msg("#test", "I'm a wizard, 'arry!")

	def buildProtocol(self, addr):
		protocol = Client(self.cfg_file)
		protocol.factory = self
		self.clients.append(protocol)
		return protocol

	def clientConnectionLost(self, connector, reason):
		"""If we get disconnected, reconnect to server."""
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()


if __name__ == "__main__":

	#   FIGURE OUT FILE NAME
	FILE_NAME    =   inspect.getfile(inspect.currentframe()).split("\\")[-1]    # irc_client.py
	FILE_PATH    =   os.path.abspath(FILE_NAME) 							    # /root/Dropbox/Cody/irc_client.py
	FILE_DIR     =   FILE_PATH[:FILE_PATH.find(FILE_NAME)] 					    # /root/Dropbox/Cody/

	#make a list with all *.cfg files in this folder
	cfg_files = glob.glob(FILE_DIR+'*.cfg')

	#make a dictionary with all the bots in it
	bots      =  {}

	for cfg in cfg_files:

		name = cfg.split('.')[0]

		# create factory protocol and application
		bots[name] = ClientFactory(cfg)



	# connect factory to this host and port
	for bot in bots:
		reactor.connectTCP("irc.globalgamers.net", 6667, bots[bot])

	# run bot
	reactor.run()


"""
	daemon = Cody('/tmp/cody_process.pid')
	

	#service argument handling
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
"""