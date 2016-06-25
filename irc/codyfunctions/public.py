#!/usr/bin/python
#-*- coding: utf8 -*-

import time, random, re, datetime, sys, json, contextlib
from urllib 		import urlencode
from urllib2        import Request, urlopen, URLError
from error_handling import writeError
from subprocess 	import Popen, PIPE, STDOUT


#cody functions
def codyResolve(self, trigger):

	try:

		def iptocountry(ip):

			ipsite 		= "http://ipinfo.io/"
			ipaddress 	= ip
			ipquery 	= ipsite+ipaddress+"/json"

			request 	= Request(ipquery)
			result 		= urlopen(request)
			html 		= result.read()

			country 	= json.loads(html)

			countrycode = country["country"]

			with open(self.FILE_DIR+"resources/countrycodes_JSON.db","r") as countryCodeFile:
				countryCodeJSON = countryCodeFile.read()
			countryCodeFile.close()

			countryresult = json.loads(countryCodeJSON)

			for key, value in countryresult.iteritems():
			    if value == countrycode:
			    	return key

		if len(self.MSG_BODY) > len(trigger + '\r\n'):
			commandinput 	= self.MSG_BODY.split(' ')
			nameToResolve 	= str(commandinput[1][:-len('\r\n')])
			cmd 			= ["host", nameToResolve]
			pro 			= Popen(cmd, stdout = PIPE, stderr = PIPE)
			output			= pro.communicate()

			if output[0]:
				resolvedoutput 	= str(output[0]).split(' ')


				if "not" not in str(output):
					#resolving IP to hostname
					if "pointer" in resolvedoutput[3]:
						hostnameoutput = resolvedoutput[3].replace("pointer", resolvedoutput[4])
						country = iptocountry(nameToResolve)

						print "pointer"
						print str(nameToResolve)
						hostnameoutput = hostnameoutput.split()
					
						self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :"+nameToResolve+" resolved to "+str(hostnameoutput[0])+" in Country: "+country+"\r\n")
					
					#resolving hostname to IP	
					else: 
						newResolve = str(resolvedoutput[3]).split()	
						country = iptocountry(newResolve[0])

						self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :"+nameToResolve+" resolved to "+newResolve[0]+" in Country: "+country+"\r\n")

				else:
					self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :could not resolve "+str(nameToResolve)+"\r\n")
			else:
				self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :"+str(nameToResolve)+" returned an empty string, sorry."+"\r\n")
		else:
			self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :usage: !cody.resolve <hostname.com> or <ipaddress>\r\n")

	except Exception as e:
		writeError("codyResolve() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

		

def hiCody(self, trigger):

	try:
		proximityMaximum = 3

		for trigger in self.CODY_REPLY_TRIGGERS:
			if trigger in self.MSG_BODY.lower()\
			and self.MSG_BODY.lower().find(trigger) < self.MSG_BODY.lower().find('cody')\
			and self.MSG_BODY.lower().find(trigger) + len(trigger) + proximityMaximum >= self.MSG_BODY.lower().find('cody'):
			
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :'+random.choice(self.CODY_REPLIES)+'\r\n' )

	except Exception as e:
		writeError("hi_Cody() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyAction(self, trigger):

	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			inputstring = self.MSG_BODY.lower().split(" ")
			to_channel	= inputstring[1]
			action_msg	= " ".join(inputstring[2:]).strip("\r\n")

			print to_channel
			print action_msg

			if "#" in to_channel:
				if len(action_msg) > 1:
					try:
						self.IRC.send("PRIVMSG "+to_channel+ " :"+self.ACTIONSTART+action_msg+self.ACTIONEND+"\r\n")
					except Exception as e:
						print e

				else:
					self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :Usage: !cody.action <#channel> <message>\r\n")
			else:
				self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :Usage: !cody.action <#channel> <message>\r\n")

	except Exception as e:
		writeError("cody_Action() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))



def codyReport(self, trigger):
	bugReportsFile = self.FILE_DIR+"userFeedback/bugReports.txt"
	featureReqFile = self.FILE_DIR+"userFeedback/featureRequests.txt"
	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n'):
		
			codyReport = self.MSG_BODY.split(' ', 1)
			codyReport = codyReport[1]
		
			#OPEN FILES FOR READ AND READ THEM INTO LOCAL
			if 'bug' in trigger:
				readReport = open(bugReportsFile, "r")

			if 'feature' in trigger:
				readReport = open(featureReqFile, "r")
								
			reportData = readReport.read().splitlines()
			startLine  = len(reportData) / 2
			codyReport = str(startLine) + '. ' + codyReport[:-2] + ' [' + self.MSG_NICK + ']' + '\r\n'
			reportData.append(codyReport)
				
			#WRITE STRINGS TO FILES
			if 'bug' in trigger:
				writeReport = open(bugReportsFile, "w")

			if 'feature' in trigger:
				writeReport = open(featureReqFile, "w")

			for element in reportData:

				print>>writeReport, reportData[int(reportData.index(element))]
			

			readReport.close()


			# REPORT THE RESULT TO CHANNEL
			if 'feature' in trigger:
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :Your feature request has been saved and will be reviewed by my developers.\r\n' )
			elif 'bug' in trigger:
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :Your bug has been saved and will be reviewed by my developers.\r\n' )
			else:
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.bug [your bug report]\r\n' )

	except Exception as e:
		writeError("cody_Report() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyConvert(self, trigger):

	try:
		findAmount 			= re.search(r'\d+', self.MSG_BODY)
		findOutputUnit		= re.search(r' in (.+)', self.MSG_BODY.lower())

		#check if any of the regex searches returned None. Calling group() on a variable == None would cause Cody to crash
		if findAmount 	   \
		and findOutputUnit :
		
			#fetch console from MESSAGE to be sent to google
			inputAmount  =  findAmount.group()
			inputUnit 	 =  self.MSG_BODY[findAmount.end() : findOutputUnit.start()]
			outputUnit 	 =  findOutputUnit.group(1)		

			if " " in inputAmount:
				inputAmount = inputAmount.replace(" ","")

			if " " in inputUnit:
				inputUnit = inputUnit.replace(" ","")

			if " " in outputUnit:
				outputUnit = outputUnit.replace(" ","")

			if len(inputUnit) <= 4 \
			and len(outputUnit) <= 4:
				try:
					google			= "https://www.google.com/finance/converter?a="+str(inputAmount)+"&from="+str(inputUnit)+"&to="+str(outputUnit)
					googlereq 		= Request(google)
					googleresult 	= urlopen(googlereq)
					html 			= googleresult.read()
					htmlsplit1 		= html.partition("<span class=bld>")
					outputAmount 	= htmlsplit1[2].partition("</span>")

					if outputAmount[0]:
						self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :'+str(inputAmount)+" "+str(inputUnit)+' = '+str(outputAmount[0])+'\r\n' )

				except Exception as e:
					writeError("cody_Convert() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))
					self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :something went wrong\r\n' )

	except Exception as e:
		writeError("cody_Convert() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyTime(self, trigger):

	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			location 	= self.MSG_BODY[self.MSG_BODY.find('!cody.time ')+len('!cody.time '):-len('\r\n')].title().replace(' ', '_')
			format 		= "%H:%M UTC%z"
			local_time 	= datetime.datetime.now(timezone('UTC'))
			offset 		= ''
			match_found = False
			exceptions  = {'CST':'Central', 'PST':'Pacific', 'MST':'Mountain', 'EST':'Eastern', \
						   'CDT':'UTC-5',   'PDT':'UTC-7',   'MDT':'UTC-6',    'EDT':'UTC-4' }
			zones 		= ['Europe/', 'America/', 'Australia/', 'Pacific/', 'Asia/', 'Africa/', 
						   'US/', 	  'Canada/',  'Atlantic/']



			#MAKE EXCEPTIONS FOR COMMON TIMEZONES WITH WEIRD NAMES
			if location.upper() in exceptions.keys():
				location = exceptions[location.upper()]

			#FIGURE OUT THE CONTINENT BY TRYING THEM ALL
			for zone in zones:

				try:
					converted_time = local_time.astimezone(timezone(zone+location)).strftime(format)
					match_found = True
									
				except:
					continue

				
			if not match_found:
				try:

					#if there's a + in the timezone, remove that stuff before we call pytz. we will be calculating it manually.
					if '+' in location:
						offset = location[location.find('+')+len('+'):]
						offsetType = '+'
						location = location[:location.find('+')].upper()

					elif '-' in location:
						offset = location[location.find('-')+len('-'):]
						offsetType = '-'
						location = location[:location.find('-')].upper()

					else:
						location = location.upper()

					converted_time = local_time.astimezone(timezone(location)).strftime(format)[:-len(' UTC+0100')]
					
					#check if the timezone has an offset (eg: GMT+1)
					if offset:
						
						if '+' in offsetType:
							offset_hours 		= int(converted_time[:len('xx')]) + int(offset)

						elif '-' in offsetType:
							offset_hours 		= int(converted_time[:len('xx')]) - int(offset)

						#check if we've gone over 24 hours
						if offset_hours > 23:
							offset_hours = offset_hours - 24

						#or under 0 hours
						if offset_hours < 0:
							offset_hours = offset_hours + 24
						
						#check if we need to add a 0 to make the number two digits
						if len(str(offset_hours)) < 2:
							offset_hours = '0' + str(offset_hours)

						#add it all together
						converted_time = str(offset_hours) + converted_time[2:]
						location = location + offsetType + str(offset)

				except:
					converted_time = 'not_found'
					location = location.title()

			location = location.replace('_', ' ')

			if 'not_found' not in converted_time:
				self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :The current time in '+location+' is '+converted_time+'\r\n' )

			else: 
				self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :'+str(location)+' was not found. '+'\r\n' )
			
		else:
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.time [location], or !cody.time [timezone]' + '\r\n' )

	except Exception as e:
		writeError("cody_Time() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyName(self, trigger):

	try:
		length 		= random.randint(1,8)
		consonants 	= ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','x','z']
		vowels 		= ['a','e','i','o','u','y']
		word 		= ""
		i 			= 0
		
		while length >= i: 
			intC = random.randint(0,18)
			intV = random.randint(0,5)

			if i%2 != 0:
				word += vowels[intV]

			if i%2 == 0:
				word += consonants[intC]
			i = i+1

		word = word.title()
		
		self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :"+word+"\r\n")

	except Exception as e:
		writeError("cody_Name() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))



def codyImage(self, trigger):

	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			query = self.MSG_BODY.split(None, 1)[1]
	        search = query.split()
	        search = '%20'.join(map(str, search))
	        url = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s&safe=off' % search
	        search_results = urlopen(url)
	        js = json.loads(search_results.read().decode('utf-8'))
	        results = js['responseData']['results']
	        for i in results: rest = i['unescapedUrl']
	        
	        self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + rest + "\r\n") 

	except Exception as e:
		writeError("codyImage() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyGetDefinition(self, trigger):

	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			word 			= self.MSG_BODY.split()[1]

			url_prefix 		= 'http://dictionary.reference.com/browse/'
			page 			= urlopen(url_prefix + word).read()
			wordtype_start 	= page.find('<span class="pg">') + len('<span class="pg">')
			wordtype_end	= page[wordtype_start:].find('</span>') + wordtype_start
			def_start       = page.find('<meta name="description" content="') + len('<meta name="description" content="')
			def_end			= page.find('See more."/>')

			if def_end < 0:
				self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + random.choice(self.CODY_INSULTS) + "\r\n")

			else:

				wordtype 		= page[wordtype_start:wordtype_end].replace(' ', '')
				wordtype 		= wordtype.replace(',', '')
				definition  	= page[def_start:def_end].split(', ')[1]

				self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + wordtype + '; ' + definition + "\r\n")

		else:
			self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :Usage: !cody.dict <word to look up>\r\n")

	except Exception as e:
		writeError("cody_GetDefinition() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyShorten(self, trigger):

	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			query = self.MSG_BODY.split(None, 1)[1]
	        short = shorten_url(query)
	        
	        self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + short + "\r\n") 

	except Exception as e:
		writeError("codyShorten() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyRoulette(self, trigger):

	try:
		gross = ['afterbirth', 'smegma', 'mucus', 'surgery', 'gross', 'hidradinitis suppurativa', 'gore', 'myiasis']
		cute  = ['kitten', 'puppies', 'foal', 'lemur', 'baby giraffe', 'baby elephant', 'baby crocodile', 'baby deer', 'baby hedgehog', 'baby dolphin', 'baby panda', 'cute animal', 'lamb']
		winner = random.choice([gross, cute])
		query  = random.choice(winner)
		search = query.split()
		search = '%20'.join(map(str, search))
		url = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s&safe=off' % search
		search_results = urlopen(url)
		js = json.loads(search_results.read().decode('utf-8'))
		results = js['responseData']['results']
		for i in results: rest = i['unescapedUrl']

		short = shorten_url(rest)
		
		self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + short + " (POTENTIALLY NSFW)\r\n") 

	except Exception as e:
		writeError("codyImage() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyGetSynonyms(self, trigger):

	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			word 			= self.MSG_BODY.split()[1]

			url_prefix		= 'http://thesaurus.com/browse/'
			page 			= urlopen(url_prefix + word).read()

			print 'url = ' + url_prefix + word
			print 'thesaurus results?' + str('no thesaurus results' in page)

			if 'no thesaurus results' in page:
				self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + random.choice(self.CODY_INSULTS) + "\r\n")

			else:

				#locate synonyms
				syns_start 		= page.find('<div class="relevancy-list">') + len('<div class="relevancy-list"> ')
				syns_end		= page[syns_start:].find('<div id="filter-0">') + syns_start

				synonyms_list   = page[syns_start:syns_end].split('<span class="text">')

				result_list 	= []

				for synonym in synonyms_list[1:]:

					result_list.append(synonym[:synonym.find('</span>')])

				return_string   = '\"' + word + '\"' + ' has the following synonyms: '
			 
			 	for result in result_list:

			 		if len(result_list) != 10:

				 		if result_list.index(result) != len(result_list) - 1:

				 			return_string += result + ', '

				 		else:

				 			return_string += result


			 	self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :" + return_string + "\r\n")

		else:
			self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :Usage: !cody.thes <word to look up>\r\n")
			
	except Exception as e:
		writeError("cody_GetSynonyms() in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

