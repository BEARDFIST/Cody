#!/usr/bin/python
#-*- coding: utf8 -*-

#self.HOME_FUNCTIONS = { 'http':self.getTitle }

from error_handling import writeError
from urllib2 		import urlopen, URLError

def codyGetTitle(self):

	try:
		URLstart = self.MSG_BODY.find("http://")
		URLend   = self.MSG_BODY[URLstart:].find(' ')
		url      = self.MSG_BODY[URLstart:URLend]

		page = '' #empty the variable
		try:
			page  = urlopen(url).read()
			title = page[page.find("<title>")+len("<title>"):page.find('</title>')]
			title = title.strip()
			if len(title) < 50:
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :'+title+'\r\n')
			else:
				print 'title was too big to post'
					
		except Exception as e:
			writeError("get_title() in home.py "+str(e))
			

	except Exception as e:
		writeError("get_title() in home.py "+str(e))