#!/usr/bin/python

import socket
import time

pythonProblemIterator = 1
pythonProblemCoiterator = 2
network = 'irc.globalgamers.net'
port = 6667
irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
irc.connect ( ( network, port ) )
print irc.recv ( 4096 )
irc.send ( 'NICK Cody\r\n' )
irc.send ( 'USER Cody Cody Cody :Python IRC\r\n' )
while True:
	data = irc.recv ( 4096 )
	if data.find ( 'PING' ) != -1:
		irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
	if data.find ( 'Looking for GameRadius?' ) != -1:
		irc.send ( 'PRIVMSG nickserv@services.globalgamers.net :auth cody Manner1sm \r\n' )
		time.sleep(3)
		irc.send ( 'JOIN #code\r\n' )
	if data.find ( '!cody quit' ) != -1:
		irc.send ( 'PRIVMSG #code :Fine, whatever\r\n' )
		irc.send ( 'QUIT :I didn\'t like you guys anyway\r\n' )
	if data.find ( '!python.problem' ) != -1:
		while (pythonProblemIterator < pythonProblemCoiterator):
			if (pythonProblemIterator == 1):
				irc.send ( 'PRIVMSG #code :Make a guessing game. The computer picks a random number between 1 and 2. The purpose of the game is to guess the number that the computer has picked in as few tries as possible. \r\n' )
				pythonProblemIterator += 1
				pythonProblemCoiterator += 1
				break
			elif (pythonProblemIterator == 2):
				irc.send ( 'PRIVMSG #code :Make a math quiz. The computer generates a random multiplication question (n1 = randint(1, 10) - n2 = randint(1, 10) -- input("What is %d times %d? " % (n1, n2)), and checks whether or not the input the user gives is correct. \r\n')
				pythonProblemIterator += 1
				pythonProblemCoiterator += 1
				break
			elif (pythonProblemIterator == 3):
				irc.send ( 'PRIVMSG #code :Print the Fibonacci sequence up to 100. c = a + b. \r\n')
				pythonProblemIterator += 1
				pythonProblemCoiterator += 1
				break
			elif (pythonProblemIterator == 4):
				irc.send ( 'PRIVMSG #code :There are two monkeys. If neither of them are smiling, we have Monkey Trouble. If both of them are smiling, we have Monkey Trouble. If only one of them is smiling, you are the new president and you receive 1 million dollars in prize money. Create booleans for these three possibilities, assign random integers with randint (0, 1), and test whether or not we\'re in Monkey Deep Shit \r\n')
				pythonProblemIterator += 1
				pythonProblemCoiterator += 1
				break
			elif (pythonProblemIterator == 5):
				irc.send ( 'PRIVMSG #code :Check if a number input by the user between 1 and 20 is a prime number or not.\r\n')
				pythonProblemIterator = 1
				pythonProblemCoiterator = 2
				break
	if data.find ( '!lmnPong' ) != -1:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
	if data.find ( '. |' ) != -1:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
	if data.find ( '.  |' ) != -1:
		irc.send ( 'PRIVMSG #code :| .\r\n')
	if data.find ( '.|' ) != -1:
		irc.send ( 'PRIVMSG #code :. |\r\n')
		irc.send ( 'PRIVMSG #code :oh, fuck\r\n')
	if data.find ( 'hi cody' ) != -1:
		irc.send ( 'PRIVMSG #code :HAYOO!\r\n' )
	if data.find ( 'hello cody' ) != -1:
		irc.send ( 'PRIVMSG #code :HAYOO!\r\n' )
	if data.find ( '!cody auth' ) != -1:
		irc.send ( 'PRIVMSG  nickserv@services.globalgamers.net :auth Cody Manner1sm\r\n' ) #for testing purposes
	print data

