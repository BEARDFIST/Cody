#!/usr/bin/python

import socket, time, os, sys, stat, inspect, random 
from urllib2 import Request, urlopen, URLError 
from codyModules import triggerCheck, noRepeatRandom, dataParse 

NICK 						= 		'NULL'
HOSTNAME 					= 		'NULL'
MSG_TYPE 					= 		'NULL'
CHANNEL 					= 		'NULL'
MESSAGE 					= 		'NULL'

connected 					=		False
lmnPong 					= 		False
network 					= 		'irc.globalgamers.net'
port 						= 		6667
irc 						= 		socket.socket ( socket.AF_INET, socket.SOCK_STREAM )

#CONNECTING
irc.connect	( ( network, port ) )
print irc.recv ( 4096 )
irc.send ( 'NICK Cody\r\n' )
irc.send ( 'USER Cody Cody Cody :Python IRC\r\n' )
while True:
	data = irc.recv ( 4096 )
	if data.find ( 'PING' ) != -1:
		irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )									
	
#AUTH and then JOIN 3 seconds later
	if data.find ( 'Looking for GameRadius?' ) != -1:
		irc.send ( 'PRIVMSG nickserv@services.globalgamers.net :auth cody Manner1sm \r\n' )
		irc.send ( 'JOIN #code\r\n' )
		time.sleep(5)
		connected = True
		data = ''

#Parsing console (from linux) chat data	
	if(connected == True and ('Inveracity' in data or 'lmn' in data or 'Stoy' in data) and data[0] == ':'):
		parsedMessage 	= dataParse(data)
		NICK 			= parsedMessage[0]
		HOSTNAME 		= parsedMessage[1]
		MSG_TYPE 		= parsedMessage[2]
		CHANNEL 		= parsedMessage[3]
		MESSAGE 		= parsedMessage[4]
	
#QUIT
	if data.find ( '!cody quit' ) != -1 or data.find ( '!cody fuck off' ) != -1 or data.find ( '!cody beat it' ) != -1 or data.find ( '!cody gtfo' ) != -1 and connected == True:
		bangPos 		= data.find('!')
		reloaderNick 	= data[1:bangPos]
		
		if(NICK == 'lmn' or NICK == 'Inveracity' or NICK == 'Stoy'):
			irc.send ( 'PRIVMSG #code :Fine, whatever\r\n' )
			irc.send ( 'QUIT :I never liked you guys anyway\r\n' )

#!python.problem
	if '!python.problem' in data.lower() and connected == True:
		randomPythonProblem = noRepeatRandom(4)
				
		if (randomPythonProblem == 0):
			irc.send ( 'PRIVMSG #code :Make a guessing game. The computer picks a random number between 1 and 2. The purpose of the game is to guess the number that the computer has picked in as few tries as possible. \r\n' )
			
		elif (randomPythonProblem == 1):
			irc.send ( 'PRIVMSG #code :Make a math quiz. The computer generates a random multiplication question (n1 = randint(1, 10) - n2 = randint(1, 10) -- input("What is %d times %d? " % (n1, n2)), and checks whether ) != -1 or data.find ( not the input the user gives is correct. \r\n')
			
		elif (randomPythonProblem == 2):
			irc.send ( 'PRIVMSG #code :Print the Fibonacci sequence up to 100. c = a + b. \r\n')
			
		elif (randomPythonProblem ==  3):
			irc.send ( 'PRIVMSG #code :There are two monkeys. If neither of them are smiling, we have Monkey Trouble. If both of them are smiling, we have Monkey Trouble. If only one of them is smiling, you are the new president and you receive 1 million dollars in prize money. Create booleans for these three possibilities, assign random integers with randint (0, 1), and test whether ) != -1 or data.find ( not we\'re in Monkey Deep Shit \r\n')
			
		elif (randomPythonProblem ==  4):
			irc.send ( 'PRIVMSG #code :Check if a number input by the user between 1 and 20 is a prime number ) != -1 or data.find ( not.\r\n')
			

#lmnPong
	if data.find ( '!lmnPong' ) != -1 and connected == True:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
		lmnPong = True		
	if data.find ( '. |' ) 		!= -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
	if data.find ( '.  |' ) 	!= -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :| .\r\n')
	if data.find ( '.    |' ) 	!= -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :|    .\r\n')
	if data.find ( '.     |' ) 	!= -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :|    .\r\n')
	if data.find ( '.   |' ) 	!= -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :|    .\r\n')
	if data.find ( '.|' ) 		!= -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :. |\r\n')
		irc.send ( 'PRIVMSG #code :oh, fuck\r\n')
		lmnPong = False

#python parser via tumbolia.appspot.com/py/
	if data.find ( '!python.expression') != -1 and connected == True:
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
	if data.find ('!cody.reload' ) != -1 and connected == True:
				
		if(NICK == 'lmn' or NICK == 'Inveracity' or NICK == 'Stoy'):
			reloadCody = data		
			reloadCodyPos = reloadCody.find('!cody.reload') + 13 				#plus 13? I need this explained again.
			reloadCody = reloadCody[reloadCodyPos:len(reloadCody) - 2]
			folderPath = '/root/Dropbox/Cody/'
			
			if os.path.isfile(folderPath + reloadCody):
				irc.send ( 'QUIT :reloading myself\r\n' )
				os.chmod(folderPath + reloadCody, stat.S_IRWXU)
				exec(open(folderPath + reloadCody))
		
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



	                   
	if	MESSAGE.lower().find ('hi' ) != -1 			\
	or 	MESSAGE.lower().find ('hello') != -1 		\
	or 	MESSAGE.lower().find ('sup')	!= -1 		\
	or 	MESSAGE.lower().find ('yo' ) != -1 			\
	or 	MESSAGE.lower().find ('hey' ) != -1 		\
	or 	MESSAGE.lower().find ('hola') != -1 		\
	or 	MESSAGE.lower().find ('you suck' ) != -1 	\
	or 	MESSAGE.lower().find ('i love you') != -1   \
	and connected == True         					:
		if MESSAGE.lower().find('cody') != -1 		\
		or MESSAGE.lower().find('codes') != -1:

			randomReply = noRepeatRandom(len(hiCodyReplies))
			irc.send ( 'PRIVMSG #code :'+hiCodyReplies[randomReply]+'\r\n' )	
		



	#if connected == True and 'hi' or 'hello' or 'sup'	or 'yo' or 'hey' or 'hola'	or 'you suck' or 'i love you' and 'cody' in data:
	
	
		
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


    
	if connected == True and NICK == 'Inveracity' and 'JOIN #code' in data:
		randomReply = noRepeatRandom(len(hiCodyReplies))
		irc.send ( 'PRIVMSG #code :'+InveracityMessages[int(randomReply)] +'\r\n' )
        
	if connected == True and NICK == 'lmn' and 'JOIN #code' in data:
		randomReply = noRepeatRandom(len(hiCodyReplies))
		irc.send ( 'PRIVMSG #code :'+lmnMessages[int(randomReply)]+'\r\n' )
                
	if connected == True and NICK == 'Stoy' and 'JOIN #code' in data :
		randomReply = noRepeatRandom(len(hiCodyReplies))
		irc.send ( 'PRIVMSG #code :'+StoyMessages[int(randomReply)]+'\r\n' )


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
	if data.find ( '!cody.version' ) != -1 and connected == True:
		
		path 		= inspect.getfile(inspect.currentframe()) #get path of currently running file, including filename
		codyVersion = path[-6:-3]
		irc.send ( 'PRIVMSG #code :'+codyVersion+'\r\n' ) #print version number to irc
		
	print data
	time.sleep(1)
