#!/usr/bin/python
import socket

#declare IRC shit
nickname = "Cerdy"
realname = "Cerdy"
channel  = "#test"
network  = 'irc.globalgamers.net'
port 	 = 6667
irc 	 = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )

#connect to IRC
irc.connect ( ( network, port ) )

#print the stuff that's going on to console
print irc.recv ( 4096 )

#set nickname, realname, and join a channel

irc.send ( 'NICK '+nickname+'\r\n' )
irc.send ( 'USER '+realname+'\r\n' )
irc.send ( 'JOIN '+channel+'\r\n' )

#while True makes the bot run until we stop it
while True:

	#omg we're using data as a variable
	data = irc.recv ( 4096 )

	#identify to nickserv
	if data.find ( 'Welcome to the Global Gamers IRC Network!' ):
		irc.send ( 'PRIVMSG nickserv@services.globalgamers.net :auth cody Manner1sm \r\n' )

	#this is something IRC needs you to do in order to verify that you're a real client. don't ask why.
	if data.find ( 'PING' ) != -1:
		irc.send ( 'PONG ' + data.split()[1] + '\r\n' )

	#this says "if someone says "!cody quit" anywhere in any channel, immediately quit IRC.
	if data.find ( '!cody quit' ) != -1:
		irc.send ( 'PRIVMSG #code :Fine, if you dont want me\r\n' )
		irc.send ( 'QUIT\r\n' )

	#here is a hideous !lmnPong function
	if data.find ( '!lmnPong' ) != -1:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
	if data.find ( '. |' ) != -1:
		irc.send ( 'PRIVMSG #code :|  .\r\n')
	if data.find ( '.  |' ) != -1:
		irc.send ( 'PRIVMSG #code :| .\r\n')
	if data.find ( '.|' ) != -1:
		irc.send ( 'PRIVMSG #code :. |\r\n')
		irc.send ( 'PRIVMSG #code :oh, fuck\r\n')

	#here he responds to hi/hello cody
	if data.find ( 'hi cody' ) != -1:
		irc.send ( 'PRIVMSG #code :HAYOO!\r\n' )
	if data.find ( 'hello cody' ) != -1:
		irc.send ( 'PRIVMSG #code :HAYOO!\r\n' )

	#print whatever is received over IRC to the console. So you can see what's going on.
	print data

