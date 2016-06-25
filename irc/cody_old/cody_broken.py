#!/usr/bin/python
import socket, time, datetime, inspect, select
from codyModules import *

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
CODY_ADMIN_FUNCTIONS 		= 	{'!cody.':Channel,			'!cody.part':partChannel, 		'!cody.reload':codyReload, 	



	consoleHasData = select.select([IRC], [],[], SOCKET_TIMEOUT)

adjoiadnmcaoihdacaoij	if consoleHasData[0]:
		console = IRC.recv ( 4096 )
		print console
		
	else:
		console = ''SERV_ADRESS+' :auth '+BOT_REALNAME+' '+AUTH_PASS+'\r\n')
		time.sleep(3)
		IRC.send ( ' '+BOT_CHANNELS+'\r\n' )
		IRC.send ( ' '+HOME_CHANNEL+' '+HOME_CHANNEL_PASSWORD+'\r\n' )
		CONNECTED = True
	

	#Parse chat data into chunks   
adjoiadnmcaoihdacaoij
	if 		CONNECTEadjoiadnmcaoihdacaoijD :
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

	#release the frame
	time.sleep(0.001)

###   END OF FILE ###