#!/usr/bin/python
import socket, time, datetime, inspect, select
from codyModules_dev import *

### SETTING UP CONSTANTS ###  

#   SOCKETS
IRC 				=    socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
SOCKET_TIMEOUT		= 	 1

#   STATES
CONNECTED 				= False
POST_CODY_FEEDS 		= False
POST_CODY_FILE_UPDATES 	= True

#   INITALIZE TIME
NOW 				= 	 datetime.datetime.now() 
START_TIME			=	 time.time()
YEAR				=	 NOW.year
MONTH				=	 NOW.month
DAY 				=	 NOW.day 
DATE 				=	 str(DAY) + '/' + str(MONTH) + '-' + str(YEAR)  

#   FIGURE OUT FILE NAME
BOT_FILE_PATH				= inspect.getfile(inspect.currentframe())
BOT_FILE_NAME 				= BOT_FILE_PATH[BOT_FILE_PATH.lower().find('cody_'):]

#   DECLARE TRIGGER->FUNCTION DICTIONARIES     
CODY_ADMIN_FUNCTIONS 		= 	{'!cody.join':joinChannel,			'!cody.part':partChannel, 		'!cody.reload':codyReload, 	
								 '!cody.load':codyReload,   		'!cody.mail':codyMail, 			'!cody.quit':codyQuit, 
								 '!cody.updates':codyFileUpdates, 	'!cody.feeds':codyFeeds}

CODY_PUBLIC_FUNCTIONS		=	{'!cody.python':codyPython,		' cody':hiCody,					'!cody.version':codyVersion, 				 
								 '!cody.feature':codyReport,	'!cody.bug':codyReport,			'!cody.uptime':codyUptime,
								 ' in ':codyConvert, 			'!cody.help':codyHelp}

CODY_HOME_FUNCTIONS 		=	{'http':getTitle} 

CODY_PASSIVE_FUNCTIONS		=   {'codyGreeting':codyGreeting, 'codyFileUpdates':codyFileUpdates, 'codyFeeds':codyFeeds} 

#   READ CONFIG (VALUES ARE FETCHED FROM CODY.CFG) 
CONFIGURATION 			= 	readConfig()
NICKSERV_ADRESS			=	CONFIGURATION['NICKSERV_ADRESS']
NETWORK_ADRESS			=	CONFIGURATION['NETWORK_ADRESS']
NETWORK_PORT			=	CONFIGURATION['NETWORK_PORT']
BOT_NICKNAME			=	CONFIGURATION['BOT_NICKNAME']
BOT_REALNAME			=	CONFIGURATION['BOT_REALNAME']
AUTH_PASS				=	CONFIGURATION['AUTH_PASS']
BOT_CHANNELS			=	CONFIGURATION['BOT_CHANNELS']
HOME_CHANNEL 			=	CONFIGURATION['HOME_CHANNEL']
HOME_CHANNEL_PASSWORD 	=  	CONFIGURATION['HOME_CHANNEL_PASSWORD']

#   SESSION DATA
SESSION_DATA				=	 {	'NICK':'NULL', 		'HOST':'NULL', 			   'MSG_TYPE':'NULL',	   		'CHANNEL':'NULL', 
									'MESSAGE':'NULL',   'START_TIME':START_TIME,   'DATE':DATE,'IRC':IRC,  		'BOT_FILE_PATH':BOT_FILE_PATH, 
									'CODY_PUBLIC_FUNCTIONS':CODY_PUBLIC_FUNCTIONS, 'CODY_HOME_FUNCTIONS':CODY_HOME_FUNCTIONS,
									'CODY_ADMIN_FUNCTIONS':CODY_ADMIN_FUNCTIONS,   'HOME_CHANNEL':HOME_CHANNEL, 'BOT_FILE_NAME':BOT_FILE_NAME,
									'POST_CODY_FEEDS':POST_CODY_FEEDS, 			   'POST_CODY_FILE_UPDATES':POST_CODY_FILE_UPDATES }


#   IRC CONNECTION

#connect to server
IRC.connect		( ( NETWORK_ADRESS, int(NETWORK_PORT) ) )
IRC.send		( 'USER cody '+NETWORK_ADRESS+' bla :'+BOT_REALNAME+'\r\n' )
IRC.send 		( 'NICK '+BOT_NICKNAME+'\r\n' )


### BOT CONNECTS TO IRC ###
while True:

	consoleHasData = select.select([IRC], [],[], SOCKET_TIMEOUT)

	if consoleHasData[0]:
		console = IRC.recv ( 4096 )
		print console
		
	else:
		console = ''

	if 'PING' in console:
		IRC.send ( 'PONG ' + console.split() [ 1 ] + '\r\n' )

	if 'MOTD' in console \
	and not CONNECTED:
		IRC.send ('PRIVMSG '+NICKSERV_ADRESS+' :auth '+BOT_REALNAME+' '+AUTH_PASS+'\r\n')
		time.sleep(3)
		IRC.send ( 'JOIN '+BOT_CHANNELS+'\r\n' )
		IRC.send ( 'JOIN '+HOME_CHANNEL+' '+HOME_CHANNEL_PASSWORD+'\r\n' )
		CONNECTED = True
	

	#Parse chat data into chunks

	if 		CONNECTED :
		parsedMessage 						= 	dataParse(console)
		SESSION_DATA['NICK'] 				= 	parsedMessage[0]
		SESSION_DATA['HOST']				= 	parsedMessage[1]
		SESSION_DATA['MSG_TYPE']			= 	parsedMessage[2]
		SESSION_DATA['CHANNEL']				= 	parsedMessage[3]
		SESSION_DATA['MESSAGE'] 			= 	parsedMessage[4]

	
	## CHECKING IF ANY OF THE PUBLIC FUNCTION TRIGGERS APPEAR IN MESSAGE
	for trigger in CODY_PUBLIC_FUNCTIONS.keys():

		if trigger in SESSION_DATA['MESSAGE']:
			functionToRun = CODY_PUBLIC_FUNCTIONS[trigger]
			functionToRun(SESSION_DATA, trigger)


	## CHECKING IF ANY OF THE HOME FUNCTIONS APPEAR IN MESSAGE
	for trigger in CODY_HOME_FUNCTIONS.keys():

		if trigger in SESSION_DATA['MESSAGE']  \
		and HOME_CHANNEL in SESSION_DATA['CHANNEL'] :

			functionToRun = CODY_HOME_FUNCTIONS[trigger]
			functionToRun(SESSION_DATA, trigger)


	## CHECKING IF ANY OF THE ADMIN FUNCTIONS APPEAR IN MESSAGE
	for trigger in CODY_ADMIN_FUNCTIONS.keys():

		if   trigger in SESSION_DATA['MESSAGE']  \
		and  authenticateHost(SESSION_DATA['HOST'], ADMIN_HOSTS):

			functionToRun = CODY_ADMIN_FUNCTIONS[trigger]
			functionToRun(SESSION_DATA, trigger)


	## TESTING ALL THE PASSIVE FUNCTIONS
	for trigger in CODY_PASSIVE_FUNCTIONS.keys():

		functionToRun = CODY_PASSIVE_FUNCTIONS[trigger]
		functionToRun(SESSION_DATA, trigger)


###   END OF FILE ###