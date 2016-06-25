#!/usr/bin/python

import socket
import time
import urllib, urllib2
import os
import sys
import stat
from random import choice #added by Inveracity

connected = False
network = 'irc.globalgamers.net'
port = 6667
irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )

#CONNECTING
irc.connect ( ( network, port ) )
print irc.recv ( 4096 )
irc.send ( 'NICK Cody_dev\r\n' )
irc.send ( 'USER Cody Cody Cody :Python IRC\r\n' )
while True:
	data = irc.recv ( 4096 )
	lmnPong = False
	if data.find ( 'PING' ) != -1:
		irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )

#AUTH and then JOIN 3 seconds later
	if data.find ( 'Looking for GameRadius?' ) != -1:
		irc.send ( 'PRIVMSG nickserv@services.globalgamers.net :auth cody Manner1sm \r\n' )
		time.sleep(3)
		irc.send ( 'JOIN #code\r\n' )
		connected = True

#QUIT
	if data.find ( '!cody quit' ) != -1 and connected == True:
		irc.send ( 'PRIVMSG #code :Fine, whatever\r\n' )
		irc.send ( 'QUIT :I didn\'t like you guys anyway\r\n' )

#!python.problem
	if data.find ( '!python.problem' ) != -1 or data.find ( '!Python.problem' ) != -1 or data.find ( '!Python.Problem' ) != -1 and connected == True:
		pythonProblemIterator = 1
		pythonProblemCoiterator = 2
		while (pythonProblemIterator < pythonProblemCoiterator):
			if (pythonProblemIterator == 1):
				irc.send ( 'PRIVMSG #code :Make a guessing game. The computer picks a random number between 1 and 2. The purpose of the game is to guess the number that the computer has picked in as few tries as possible. \r\n' )
				pythonProblemIterator += 1
				pythonProblemCoiterator += 1
				break
			elif (pythonProblemIterator == 2):
				irc.send ( 'PRIVMSG #code :Make a math quiz. The computer generates a random multiplication question (n1 = randint(1, 10) - n2 = randint(1, 10) -- input("What is %d times %d? " % (n1, n2)), and checks whether ) != -1 or data.find ( not the input the user gives is correct. \r\n')
				pythonProblemIterator += 1
				pythonProblemCoiterator += 1
				break
			elif (pythonProblemIterator == 3):
				irc.send ( 'PRIVMSG #code :Print the Fibonacci sequence up to 100. c = a + b. \r\n')
				pythonProblemIterator += 1
				pythonProblemCoiterator += 1
				break
			elif (pythonProblemIterator == 4):
				irc.send ( 'PRIVMSG #code :There are two monkeys. If neither of them are smiling, we have Monkey Trouble. If both of them are smiling, we have Monkey Trouble. If only one of them is smiling, you are the new president and you receive 1 million dollars in prize money. Create booleans for these three possibilities, assign random integers with randint (0, 1), and test whether ) != -1 or data.find ( not we\'re in Monkey Deep Shit \r\n')
				pythonProblemIterator += 1
				pythonProblemCoiterator += 1
				break
			elif (pythonProblemIterator == 5):
				irc.send ( 'PRIVMSG #code :Check if a number input by the user between 1 and 20 is a prime number ) != -1 or data.find ( not.\r\n')
				pythonProblemIterator = 1
				pythonProblemCoiterator = 2
				break

#lmnPong
	if data.find ( '!lmnPong' ) != -1 and connected == True:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
		lmnPong = True		
	if data.find ( '. |' ) != -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
	if data.find ( '.  |' ) != -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :| .\r\n')
	if data.find ( '.    |' ) != -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :|    .\r\n')
	if data.find ( '.     |' ) != -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :|    .\r\n')
	if data.find ( '.   |' ) != -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :|    .\r\n')
	if data.find ( '.|' ) != -1 and lmnPong == True and connected == True:
		irc.send ( 'PRIVMSG #code :. |\r\n')
		irc.send ( 'PRIVMSG #code :oh, fuck\r\n')
		lmnPong = False

#python parser via tumbolia.appspot.com/py/
	if data.find ( '!python.expression') != -1 and connected == True:
		pythonExpression = data		
		pythonParseURI = 'http://tumbolia.appspot.com/py/'
		pythonExpressionPos = pythonExpression.find('!python.expression') + 19
		pyInput = pythonExpression[pythonExpressionPos:len(pythonExpression)]
		pyInput = pyInput.replace(' ','%20')
		pyInput = pyInput.replace('\\n','%0A')
		pyInput = pyInput.replace('\\t','%09')
		response = urllib2.urlopen(pythonParseURI + pyInput).read()
		irc.send ( 'PRIVMSG #code :' + response + '\r\n')
	
#reloadCody
	if data.find ('!cody.reload' ) != -1 and connected == True:
		reloadCody = data		
		reloadCody = reloadCody.lower()
		reloadCodyPos = reloadCody.find('!cody.reload') + 13
		reloadCody = reloadCody[reloadCodyPos:len(reloadCody) - 2]
		folderPath = '/root/Dropbox/Cody/'
		
		if os.path.isfile(folderPath + reloadCody):
			irc.send ( 'QUIT :reloading myself\r\n' )
			os.chmod(folderPath + reloadCody, stat.S_IRWXU)
			os.system('python ' + folderPath + reloadCody)
		

#hiCody		
	if data.find ( 'hi cody' ) != -1 or data.find ( 'hi, cody' ) != -1 or data.find ( 'Hi cody' ) != -1 or data.find ( 'Hi, cody' ) != -1 or data.find ( 'hi, Cody' ) != -1 or data.find ( 'hi Cody' ) != -1 or data.find ( 'hello cody'  ) != -1 or data.find ( 'hello, cody' ) != -1 or data.find ( 'Hello cody' ) != -1 or data.find ( 'Hello, cody' ) != -1 or data.find ( 'hello Cody' ) != -1 or data.find ( 'Hello, Cody' ) != -1 or data.find ( 'hello, Cody' ) != -1 and connected == True:	
		irc.send ( 'PRIVMSG #code :HAIOOOOO!\r\n' )	

#admin gretting (Added by Inveracity)
	#from random import choice

	#Morning messages
	a = "An overlord has entered."
	b = "hide your wife hide your kids!"
	c = "oh no not this guy."
	d = "hello beautiful!"
	e = "I need a hug, will you hug me?"
	f = "welcome my sunshine."
	g = "smell my fingers."
	h = "wtf, I told you not to come back!"
	i = "yay \\o/ one of my creators has joined!"
	#j = "test"
	#k = "test"
	#l = "test"
	#m = "test"
	#n = "test"
	#o = "test"
	#p = "test"
	#q = "test"
	#r = "test"
	#s = "test"
	#t = "test"
	#u = "test"
	#v = "test"
	#x = "test"
	#y = "test"
	#z = "test"

	#array
	message = [a, b, c, d, e, f, g, h, i]
	#randomizer
	pickedmessage = choice(message)
	#listen for admin logins
	if data.find ( 'JOIN #code' ) != -1 and ( 'Inveracity' ) != -1 and ( 'lmn' ) != -1 and ( 'Stoy' ) != -1 and connected == True:
		if data.find ( 'Cody_dev' ) != -1 or data.find ( 'Cody' ) != -1:
			print "test"
		else:
			irc.send ( 'PRIVMSG #code :'+pickedmessage+'\r\n' )
	
#Cody Version ID
	if data.find ( '!cody.version' ) != -1 and connected == True:
		path = sys.argv[0] #get path of currently running file, including filename

		rm_path_from_file = path.replace( "/root/Dropbox/Cody/" , "" ) #remove path from filename
		rm_cody_from_file = rm_path_from_file.replace( "cody_" , "version: ") #remove cody from filename and insert version
		cody_version_number = rm_cody_from_file.replace ( ".py" , "") #remove file extension
		
		irc.send ( 'PRIVMSG #code :'+cody_version_number+'\r\n' ) #print version number to irc
		
	print data
