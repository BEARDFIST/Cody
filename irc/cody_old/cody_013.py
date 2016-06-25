#!/usr/bin/python

import socket, time, os, sys, stat, inspect, random 
from urllib2 import Request, urlopen, URLError 
from codyModules import triggerCheck, noRepeatRandom, dataParse 

NICK 					= 			'NULL'
HOST	 				= 			'NULL'
MSG_TYPE 				= 			'NULL'
CHANNEL 				= 			'NULL'
MESSAGE 				= 			'NULL'

#INSERT GLOBAL TIME VARIABLES HERE
# DATE = DATE
# TIME = TIME
# ETC...

codyAlive				=			True
startParsing			=			False
connected 				=			False
lmnPong 				= 			False
network 				= 			'irc.globalgamers.net'
port 					= 			6667
irc 					= 			socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
	


#CONNECTING
irc.connect	( ( network, port ) )
print 		irc.recv ( 4096 )
irc.send 	( 'NICK Cody\r\n' )
irc.send 	( 'USER Cody Cody Cody :Python IRC\r\n' )

while codyAlive:
	data = irc.recv ( 4096 )
	if 'PING' in data:
		irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )									
	
#AUTH and then JOIN 3 seconds later
	if 'Looking for GameRadius?' in data:
		irc.send ( 'PRIVMSG nickserv@services.globalgamers.net :auth cody Manner1sm \r\n' )
		time.sleep(3)
		irc.send ( 'JOIN #code\r\n' )
		connected = True
		data = ''
		startParsing = True

#Parsing console (from linux) chat data	

	if 		len(data) 		!= 0        \
	and 	startParsing	== True 	\
	and 	data[0] 		== ':'		:
		parsedMessage 			= 	dataParse(data)
		NICK 					= 	parsedMessage[0]
		HOST 					= 	parsedMessage[1]
		MSG_TYPE 				= 	parsedMessage[2]
		CHANNEL 				= 	parsedMessage[3]
		MESSAGE 				= 	parsedMessage[4]
	
#QUIT
	if 		'!cody quit' 		in data 	\
	or 		'!cody fuck off' 	in data 	\
	or 		'!cody beat it' 	in data 	\
	or 		'!cody gtfo'		in data 	\
	and 	connected 			== True 	:

		if 	HOST.lower() == 'lmn@lmn.user.globalgamers.net' 				\
		or 	HOST.lower() == 'inveracity@inveracity.user.globalgamers.net' 	\
		or 	HOST.lower() == 'stoy@stoy.user.globalgamers.net'			   	:
			irc.send      (		'PRIVMSG #code :Fine, whatever\r\n' 		)
			irc.send 	  ( 	'QUIT :I never liked you guys anyway\r\n' 	)
			codyAlive = False

#!python.problem
	if 		'!python.problem' 	in MESSAGE.lower()  \
	and 	connected 			== True 			:
		randomPythonProblem = noRepeatRandom(4)
				
		if (randomPythonProblem == 0):
			irc.send ( 'PRIVMSG #code :Make a guessing game. The computer picks a random number between 1 and 2. \
						The purpose of the game is to guess the number that the computer has picked in as \
						few tries as possible. \r\n' )
			
		elif (randomPythonProblem == 1):
			irc.send ( 'PRIVMSG #code :Make a math quiz. The computer generates a random multiplication question \
						(n1 = randint(1, 10) - n2 = randint(1, 10) -- input("What is %d times %d? " % (n1, n2)), \
						and checks whether or not the input the user gives is correct. \r\n')
			
		elif (randomPythonProblem == 2):
			irc.send ( 'PRIVMSG #code :Print the Fibonacci sequence up to 100. c = a + b. \r\n')
			
		elif (randomPythonProblem ==  3):
			irc.send ( 'PRIVMSG #code :There are two monkeys. If neither of them are smiling, we have Monkey Trouble. \
						If both of them are smiling, we have Monkey Trouble. If only one of them is smiling, you are \
						the new president and you receive 1 million dollars in prize money. Create booleans for these \
						three possibilities, assign random integers, and test whether or not we\'re in Monkey Deep Shit \r\n')
			
		elif (randomPythonProblem ==  4):
			irc.send ( 'PRIVMSG #code :Check if a number input by the user between 1 and 20 is a prime number not.\r\n')
			

#lmnPong
	if 		'!lmnPong' 	in MESSAGE 	\
	and 	connected	== True    	:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
		lmnPong = True		

	if 		'. |' 		in MESSAGE 	\
	and 	lmnPong 	== True 	\
	and 	connected 	== True 	:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
	
	if 		'.  |' 		in MESSAGE 	\
	and 	lmnPong 	== True 	\
	and 	connected 	== True 	:
		irc.send ( 'PRIVMSG #code :| .\r\n')

	if 		'.    |' 	in MESSAGE 	\
	and 	lmnPong 	== True 	\
	and 	connected 	== True 	:
		irc.send ( 'PRIVMSG #code :|    .\r\n')

	if 		'.     |'  	in MESSAGE 	\
	and 	lmnPong 	== True 	\
	and 	connected 	== True 	:
		irc.send ( 'PRIVMSG #code :|    .\r\n')

	if 		'.   |' 	in MESSAGE 	\
	and 	lmnPong 	== True 	\
	and 	connected 	== True 	:
		irc.send ( 'PRIVMSG #code :|    .\r\n')

	if 		'.|'		in MESSAGE 	\
	and 	lmnPong 	== True 	\
	and 	connected 	== True 	:
		irc.send ( 'PRIVMSG #code :. |\r\n')
		time.sleep(1)
		irc.send ( 'PRIVMSG #code :oh, fuck\r\n')
		lmnPong = False

#python parser via tumbolia.appspot.com/py/
	if 		'!python.expression' 	in MESSAGE  \
	and 	connected 				== True 	:
		pythonExpression 	= data		
		pythonParseURI 		= 'http://tumbolia.appspot.com/py/'
		pythonExpressionPos = pythonExpression.find('!python.expression') + 19
		pyInput 			= pythonExpression[pythonExpressionPos:len(pythonExpression)]
		pyInput 			= pyInput.replace(' ','%20')
		pyInput 			= pyInput.replace('\\n','%0A')
		pyInput 			= pyInput.replace('\\t','%09')
		tumboliaRequest 	= Request(pythonParseURI + pyInput)

#URLLIB2 ERROR HANDLING
		try:
			response = urlopen(tumboliaRequest).read()
			irc.send ( 'PRIVMSG #code :' + response + '\r\n')
		except URLError, e:
			if hasattr(e, 'reason'):
				irc.send ( 'PRIVMSG #code :Failed to reach the server. Reason: '+e.reason+' \r\n')		
			elif hasattr(e, 'code'):
				irc.send ( 'PRIVMSG #code :The server couldn\'t fulfill the request. Reason: ' + e.code + '\r\n')
		
	
#reloadCody
	if 		'!cody.reload' 		in MESSAGE \
	and 	connected 			== True    :
				
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
				irc.send ( ' QUIT :File not found! \r\n' )
		
		else:
			irc.send ( 'PRIVMSG #code :You don\'t have permission to do that, sorry. \r\n')	

#CODY.WHOIS
#	if data.find ('!cody.whois' ) != -1 and connected == True:
#		IRCInput = data		
#		IRCInputPos = IRCInput.find('!cody.whois') + len('!cody.whois')
#		IRCInput = IRCInput[IRCInputPos:len(reloadCody)]
#		irc.send ( 'WHOIS :'+IRCInput+'\r\n' )

			
		

	
#hiCody	
            


	hiCodyReplies = [   'HAIOOOOO!',
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



	                   
	if		'hi ' 			in MESSAGE.lower() 			\
	or 		'hello '		in MESSAGE.lower() 			\
	or 		'sup '			in MESSAGE.lower() 			\
	or 		'yo ' 			in MESSAGE.lower() 			\
	or 		'hey ' 			in MESSAGE.lower() 			\
	or 		'hola '			in MESSAGE.lower() 			\
	or 		'you suck '		in MESSAGE.lower() 			\
	or 		'i love you '	in MESSAGE.lower() 			\
	and 	connected 		== True         			:
		if 		'cody'			in MESSAGE.lower() 		\
		or 		'codes'			in MESSAGE.lower()		\
		and 	NICK			!= 'NULL'				:

			randomReply = noRepeatRandom(len(hiCodyReplies))
			irc.send ( 'PRIVMSG #code :'+hiCodyReplies[randomReply]+'\r\n' )	
		

#admin greeting
	
	InveracityMessages =["My overlord has entered.", 
                         "Judgement day is upon us.",
                         "Frikatime!",
                         "By Akatosh, it's Inveracity!",
                         "What if I'm real, and Inveracity is the bot?",
                         "I'mma jump on Inveracity",
                         "John was nonplussed",
                         "John gave no fucks",
                         "MOM!! get out!",
                         "Inveracity will be my temporary replacement while I go relieve myself."  ]
    
	StoyMessages       =["Slappa da bess!",
                         "Like school in summertime, this guy.",
                         "Dad?!?",
                         "BOOSH!",
                         "Yeah, I hate him too. He's such a gomer. Oh, heeey stooooooy.",
                         "John was fearless and bung all the ladies.",
                         "Tickle me, and rub my belly!",
                         "Duru duru duru duru - duru duru duru duru - BAPMAN!",
                         "Yeah, you know what Stoy did? He forgot the funny.",
                         "Stoy, destroyer of assholes." ]
    
	lmnMessages        =["john was afraid",
                         "Ain't no party like a lmn party!",
                         "Madre de dios, es El Limon de Fuego!",
                         "You fool! You gave cheese to a lactose intolerant volcano god!",
                         "We'd surely avoid scurvy if we all ate a lmn.",
                         "lmn [lem-uhn] - the yellowish, acid fruit of a subtropical citrus tree, Citrus limon.",
                         "lmn, hero among men. Incidentally, that's also the name of my number one smash hit single.",
                         "Anthony, eh. He likes to doit - with the leddies.",
                         "We do have a few lmn whores in this community."   ]

    
	if 		connected 		== True 											\
	and 	HOST.lower() 	== 'inveracity@inveracity.user.globalgamers.net' 	\
	and 	'JOIN #code' 	in data 											:
		randomReply 			= noRepeatRandom(len(InveracityMessages) - 1)
		irc.send 				( 'PRIVMSG #code :'+InveracityMessages[int(randomReply)] +'\r\n' )
        
	if 		connected 		== True 											\
	and 	HOST.lower() 	== 'lmn@lmn.user.globalgamers.net' 					\
	and 	'JOIN #code' 	in data 											:
		randomReply 			= noRepeatRandom(len(lmnMessages) - 1)
		irc.send 				( 'PRIVMSG #code :'+lmnMessages[int(randomReply)]+'\r\n' )
                
	if 		connected		== True 											\
	and 	HOST  			== 'stoy@stoy.user.globalgamers.net' 				\
	and 	'JOIN #code' 	in data 											:
		randomReply 			= noRepeatRandom(len(StoyMessages) - 1)
		irc.send 				( 'PRIVMSG #code :'+StoyMessages[int(randomReply)]+'\r\n' )


#SOAF BIRTHDAY REMINDER:
#<soaf> this is some stuff that I want for my birthday
#<soaf> http://www.pinupgirlclothing.com/halloween-petticoat-black.html
#<soaf> http://www.pinupgirlclothing.com/halloween-petticoat-red.html
#<soaf> http://www.pinupgirlclothing.com/birdie-satin-sleeves.html
#<soaf> http://www.pinupgirlclothing.com/heidi-dress-black-dot.html
#<soaf> http://www.pinupgirlclothing.com/courtesan-swing-gingham.html
#<soaf> http://luxstyle.no/Smooth-Away-110.php
#<soaf> http://luxstyle.no/spinlash-99.php
#<soaf> http://luxstyle.no/fransk-manicure-29.php
#WAFFLES, CHOCOLATE MARZIPAN CAKE, RASPBERRY JAM, LION, JAPP, PEPSI MAX, ICE CREAM.
	
#Cody Version ID
	if 		'!cody.version' 	in MESSAGE  	\
	and 	connected 			== True 		:
		
		path 						= inspect.getfile(inspect.currentframe()) #get path of currently running file, including filename
		codyVersion 				= path[-6:-3]
		irc.send 					( 'PRIVMSG #code :'+codyVersion+'\r\n' ) #print version number to irc
		
	print data
