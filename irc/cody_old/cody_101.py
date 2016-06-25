#!/usr/bin/python
import socket, time, os, sys, stat, inspect, random, datetime
from urllib2 import Request, urlopen, URLError 
from codyModules import noRepeatRandom, dataParse, addBug, addFeature, codyUptime

#DATA PARSER
NICK 				= 	 'NULL'
HOST	 			= 	 'NULL'
MSG_TYPE 			= 	 'NULL'
CHANNEL 			= 	 'NULL'
MESSAGE 			= 	 'NULL'

#TIME
NOW 				= 	 datetime.datetime.now()
STARTTIME			=	 time.time()
YEAR				=	 NOW.year
MONTH				=	 NOW.month
DAY 				=	 NOW.day 
DATE 				=	 str(DAY) + '/' + str(MONTH) + '-' + str(YEAR)

#STATES 
codyAlive			=	 True
startParsing		=	 False
connected 			=	 False
lmnPong 			= 	 False
codyAnswer			=	 False

#LISTS
hiCodyReplies 		= [  'HAIOOOOO!',
						 'waazzaaap!',
						 'You\'re not my dad!',
						 'Heeeey, my eskimo brother!',
						 'You\'re way too young to be a bitch.',
						 'Shut up.',
						 'WHAT? WHAT COULD YOU POSSIBLY WANT?',
						 'That\'s how your mom greets me, too.',
						 'I\'m not in the mood for your petty squabbles.',
						 'WU TANG CLAN AIN\'T NUTTIN TO FUCK WIT',
						 '\'sup, g?',
						 'you\'re so money.',
						 'To impress a chick - helicopter dick.',
						 'Heeeeeeey, brother.',
						 'Bitches don\'t know \'bout mah pylons.',
						 'If you talk to me like that again, I\'mma choke a bitch.']

hiCodyTriggers 		= [  'hi', 'hello', 'sup', 'yo', 'hey', 'hola', 'you suck', 'i love you', 'hai' ]

InveracityMessages 	= [	 "My overlord has entered.", 
                         "Judgement day is upon us.",
                         "Frikatime!",
                         "By Akatosh, it's Inveracity!",
                         "What if I'm real, and Inveracity is the bot?",
                         "I'mma jump on Inveracity",
                         "John was nonplussed",
                         "John gave no fucks",
                         "MOM!! get out!",
                         "Inveracity will be my temporary replacement while I go relieve myself."  ]
    
StoyMessages       	= [	 "Slappa da bess!",
                         "Like school in summertime, this guy.",
                         "Dad?!?",
                         "BOOSH!",
                         "Yeah, I hate him too. He's such a gomer. Oh, heeey stooooooy.",
                         "John was fearless and bung all the ladies.",
                         "Tickle me, and rub my belly!",
                         "Duru duru duru duru - duru duru duru duru - BAPMAN!",
                         "Yeah, you know what Stoy did? He forgot the funny.",
                         "Stoy, destroyer of assholes." ]
    
lmnMessages        	= [	 "john was afraid",
                         "Ain't no party like a lmn party!",
                         "Madre de dios, es El Limon de Fuego!",
                         "You fool! You gave cheese to a lactose intolerant volcano god!",
                         "We'd surely avoid scurvy if we all ate a lmn.",
                         "lmn [lem-uhn] - the yellowish, acid fruit of a subtropical citrus tree, Citrus limon.",
                         "lmn, hero among men. Incidentally, that's also the name of my number one smash hit single.",
                         "Anthony, eh. He likes to doit - with the leddies.",
                         "We do have a few lmn whores in this community."   ]

randomPythonProblem = [	 "Make a guessing game. The computer picks a random number between 1 and 2. The purpose of the game is to guess the number that the computer has picked in as few tries as possible.",
						 "Make a math quiz. The computer generates a random multiplication question, and checks whether or not the input the user gives is correct.",
						 "Print the Fibonacci sequence up to 100. c = a + b.",
						 "There are two monkeys. If neither of them are smiling, we have	Monkey Trouble.	If both of them are smiling, we have Monkey Trouble. If only one of them is smiling, you are the new president and you receive 1 gorillian dollars. Create booleans for these three possibilities, assign random integers, and test whether or not we\'re in Monkey Deep Shit ",
						 "Check whether or not a number input by the user between 1 and 100 is a prime number."]

helpCommands   	    = [  'problem', 'version', 'uptime', 'feature', 'bug', 'python']

codyQuitTriggers    = [  'quit', 'gtfo', 'get out', 'fuck off', 'go away', 'terminate']


#IRC SETUP
botNickname			= 	 'Cody'
authPass			=    'Manner1sm'
network 			= 	 'irc.globalgamers.net'
port 				= 	 6667
irc 				=    socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
	
#CONNECTING
irc.connect			( ( network, port ) )
print 				irc.recv ( 4096 )
irc.send 			( 'USER Cody Cody Cody :Running on Python\r\n' )
irc.send 			( 'NICK '+botNickname+'\r\n' )


while codyAlive:
	data = irc.recv ( 4096 )
	if 'PING' in data:
		irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )	
		NICK 					= 			'NULL'
		HOST	 				= 			'NULL'
		MSG_TYPE 				= 			'NULL'
		CHANNEL 				= 			'NULL'
		MESSAGE 				= 			'NULL'						


#AUTH and then JOIN 3 seconds later
	if 'Looking for GameRadius?' in data:
		
		irc.send 	( 'PRIVMSG nickserv@services.globalgamers.net :auth cody '+authPass+'\r\n' )
		time.sleep(3)
		irc.send ( 'JOIN #code cosanostra\r\n' )
		connected = True
		data = 'NULL'
		startParsing = True


#Parse chat data into chunks

	if 		startParsing	== True 	\
	and 	data[0] 		== ':'		:
		parsedMessage 			= 	dataParse(data)
		NICK 					= 	parsedMessage[0]
		HOST 					= 	parsedMessage[1]
		MSG_TYPE 				= 	parsedMessage[2]
		CHANNEL 				= 	parsedMessage[3]
		MESSAGE 				= 	parsedMessage[4]		

	
#!cody.QUIT
	
	for quitTrigger in codyQuitTriggers:
		if 		'Cody, '+quitTrigger 	in data 	\
		and 	connected 				== True 	:

			if 	HOST.lower() == 'lmn@lmn.user.globalgamers.net' 				\
			or 	HOST.lower() == 'inveracity@inveracity.user.globalgamers.net' 	\
			or 	HOST.lower() == 'stoy@stoy.user.globalgamers.net'			   	:
				irc.send      (		'PRIVMSG #code :I guess I don\'t really have a choice\r\n' 		)
				irc.send 	  ( 	'QUIT :I never liked you guys anyway\r\n' 	)
				codyAlive = False


#!python.problem
	if 		'!cody.problem' 	in MESSAGE.lower()  \
	and 	connected 			== True :
		
		irc.send 				( 'PRIVMSG #code :'+randomPythonProblem[noRepeatRandom(len(randomPythonProblem), 'pythonProblem')] +'\r\n' )


#!cody.join
	if 		'!cody.join' 	in MESSAGE.lower()  \
	and 	connected 			== True :
		
		irc.send 				( 'JOIN '+MESSAGE[len('!cody.join'):]+'\r\n' )
		
#!cody.part
	if 		'!cody.part' 	in MESSAGE.lower()  \
	and 	connected 			== True :
		
		irc.send 				( 'PART '+MESSAGE[len('!cody.part'):]+'\r\n' )

#!cody.pong
	if 		'!cody.pong' 	in MESSAGE 	\
	and 	connected	== True    	:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
		lmnPong = True		
		

	if lmnPong == True:

		if 		'. |' 		in MESSAGE  :
			irc.send ( 'PRIVMSG #code :|  .\r\n')
				
		if 		'.  |' 		in MESSAGE 	:
			irc.send ( 'PRIVMSG #code :| .\r\n')
			
		if 		'.    |' 	in MESSAGE 	:
			irc.send ( 'PRIVMSG #code :|    .\r\n')
			
		if 		'.     |'  	in MESSAGE 	:
			irc.send ( 'PRIVMSG #code :|    .\r\n')
			
		if 		'.   |' 	in MESSAGE 	:
			irc.send ( 'PRIVMSG #code :|    .\r\n')
			
		if 		'.|'		in MESSAGE 	:
			irc.send ( 'PRIVMSG #code :. |\r\n')
			time.sleep(1)
			irc.send ( 'PRIVMSG #code :You win!\r\n')
			lmnPong = False

		if 		'|.'		in MESSAGE\
		or 		'| .' 		in MESSAGE\
		or 		'|  .' 		in MESSAGE\
		or 		'|   .' 	in MESSAGE:
			irc.send ( 'PRIVMSG #code :I win, motherfucker.\r\n')
			lmnPong = False


#!cody.python
	if 		'!cody.python' 			in MESSAGE  \
	and 	connected 				== True 	:
		pythonExpression 	= MESSAGE
		pythonParseURI 		= 'http://tumbolia.appspot.com/py/'
		pyInput 			= pythonExpression[len('!cody.python '):]
		pyInput 			= pyInput.replace(' ','%20')
		pyInput 			= pyInput.replace('\\n','%0A')
		pyInput 			= pyInput.replace('\\t','%09')
		tumboliaRequest 	= Request(pythonParseURI + pyInput)

		try:
			response = urlopen(tumboliaRequest).read()
			irc.send ( 'PRIVMSG #code :' + response + '\r\n')
		
		except URLError, e:
			if hasattr(e, 'reason'):
				irc.send ( 'PRIVMSG #code :Failed to reach the server. Reason: '+e.reason+' \r\n')		
			elif hasattr(e, 'code'):
				irc.send ( 'PRIVMSG #code :The server couldn\'t fulfill the request. Reason: ' + e.code + '\r\n')

		
#!cody.reload
	if 		'!cody.reload' 		in MESSAGE.lower() 	\
	and 	connected 			== True    			:
				
		if 	HOST.lower() 		== 'lmn@lmn.user.globalgamers.net' 					\
		or 	HOST.lower() 		== 'inveracity@inveracity.user.globalgamers.net' 	\
		or 	HOST.lower() 		== 'stoy@stoy.user.globalgamers.net'			   	:
			newCody 				= MESSAGE.split()
			newCody 				= newCody[1]
			folderPath 				= '/root/Dropbox/Cody/'
			
			if os.path.isfile(folderPath + newCody):
				irc.send ( 'QUIT :reloading myself\r\n' )
				os.chmod(folderPath + newCody, stat.S_IRWXU)
				exec(open(folderPath + newCody))
				codyAlive = False
			else:
				irc.send ( 'PRIVMSG #code :File not found! \r\n' )
		
		else:
			irc.send ( 'PRIVMSG #code :You don\'t have permission to do that, sorry. \r\n')	

		
#hi cody	
        
	if 'cody' in MESSAGE.lower():
		proximityMaximum = 5
		
		for trigger in hiCodyTriggers:
			if trigger in MESSAGE.lower() 																				\
			and MESSAGE.lower().find(trigger) < MESSAGE.lower().find('cody')												\
			and MESSAGE.lower().find(trigger) + len(trigger) + proximityMaximum >= MESSAGE.lower().find('cody') \
			and connected == True:
				randomReply = noRepeatRandom(len(hiCodyReplies), 'hiCody')
				irc.send ( 'PRIVMSG #code :'+hiCodyReplies[randomReply]+'\r\n' )
				

#!cody.greeting
	
	if 		connected 		== True 											\
	and 	HOST.lower() 	== 'inveracity@inveracity.user.globalgamers.net' 	\
	and 	'JOIN #code' 	in data 											:
		randomReply 			= noRepeatRandom(len(InveracityMessages), 'codyGreeting')
		irc.send 				( 'PRIVMSG #code :'+InveracityMessages[int(randomReply)] +'\r\n' )
		
        
	if 		connected 		== True 											\
	and 	HOST.lower() 	== 'lmn@lmn.user.globalgamers.net' 					\
	and 	'JOIN #code' 	in data 											:
		randomReply 			= noRepeatRandom(len(lmnMessages), 'codyGreeting')
		irc.send 				( 'PRIVMSG #code :'+lmnMessages[int(randomReply)]+'\r\n' )
		
                
	if 		connected		== True 											\
	and 	HOST  			== 'stoy@stoy.user.globalgamers.net' 				\
	and 	'JOIN #code' 	in data 											:
		randomReply 			= noRepeatRandom(len(StoyMessages), 'codyGreeting')
		irc.send 				( 'PRIVMSG #code :'+StoyMessages[int(randomReply)]+'\r\n' )
		

#!cody.version
	if 		'!cody.version' 	in MESSAGE  	\
	and 	connected 			== True 		:
		
		path 						= inspect.getfile(inspect.currentframe()) #get path of currently running file, including filename
		codyVersion 				= path[-6:-3]
		irc.send 					( 'PRIVMSG #code :'+codyVersion+'\r\n' ) #print version number to irc
		

#!cody.feature
	if 		'!cody.feature'		in MESSAGE.lower() 	\
	and 	' '					in MESSAGE.lower()	\
	and		connected 			== True 			:
	
		codyFeature					= MESSAGE.split(' ', 1)
		codyFeature					= codyFeature[1]
		addFeature(codyFeature, NICK)
		irc.send 					( 'PRIVMSG #code :Your feature request has been saved and will be reviewed by my developers.\r\n' )
		

#!cody.bug
	if 		'!cody.bug'			in MESSAGE.lower() 	\
	and 	' '					in MESSAGE.lower()	\
	and		connected 			== True 			:

		codyBug 					= MESSAGE.split(' ', 1)
		codyBug 					= codyBug[1]
		addBug(codyBug, NICK)				#adds the reported bug to Cody/userFeedback/bugReports.txt
		irc.send 					( 'PRIVMSG #code :Your bug has been saved and will be reviewed by my developers.\r\n' )
		

#!cody.uptime
	if 		'!cody.uptime'		in MESSAGE.lower() 	\
	and		connected 			== True 			:

			currentUptime				= time.time() - STARTTIME
			irc.send 					( 'PRIVMSG #code :I\'ve been awake for ' + str(codyUptime(currentUptime)) + '\r\n' )
		

#!cody.help
	if 		'!cody.help'		in MESSAGE.lower() 	\
	and		connected 			== True 			:
		irc.send ( 'NOTICE '+NICK+' #code :Available Commands:\r\n' )
		for stuff in helpCommands:
			irc.send ( 'NOTICE '+NICK+' #code :!cody.'+stuff+'\r\n' )
		

#print data to terminal
	print data
	

