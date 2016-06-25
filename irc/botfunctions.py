#!/usr/bin/python
import contextlib, time, random, urllib, urllib2
from apiclient.discovery import build




class Public():

	def __init__(self, bot):

		self.bot = bot


	def shorten_url(self, msg):
		'''Shortens a URL using the tinyurl API. syntax: ".short <URL_to_shorten>"'''

		#check if URL is fully qualified
		if 'http' not in msg:
			msg = 'http://' + msg

		#request a tinyurl and return it
		request_url = ('http://tinyurl.com/api-create.php?' + urllib.urlencode({'url':msg}))
		with contextlib.closing(urllib2.urlopen(request_url)) as response:
			short = response.read()

		#check if this is a real website or not
		err = '404 - Not Found'
		try:
			if  err not in urllib2.urlopen(short).read():
				return short

			else:
				return err
		except:
			return err

	def uptime(self):
		'''Returns bot uptime.'''

		currentUptime = time.time() - self.bot.START_TIME
		
		#Defining time variables:
		MINUTE  =   60
		HOUR    =   MINUTE  * 60
		DAY     =   HOUR    * 24
	 
		#Calculate seconds into days, hours and minutes:
		days    = int(  currentUptime / DAY  )
		hours   = int( (currentUptime % DAY  ) / HOUR   )
		minutes = int( (currentUptime % HOUR ) / MINUTE )
	 
		# UPTIME = X days, X hours, X minutes
		uptimeString = ""

		if days > 0:
			uptimeString += str(days) + " " + (days == 1 and "day" or "days" ) + ", "

		if len(uptimeString) > 0 or hours > 0:
			uptimeString += str(hours) + " " + (hours == 1 and "hour" or "hours" ) + ", "

		uptimeString += str(minutes) + " " + (minutes == 1 and "minute" or "minutes" ) + ". "

		return 'I\'ve been awake for ' + str(uptimeString) + 'I last woke up ' + self.bot.DATE

	def decide(self, msg):
		'''Returns a random confirmation, denial, or a neutral statement.'''
	
		cody_confirmations = ["that's right!", "sure thing!", "you got it!", "absolutely yes.", 
							  "no doubt.", "definitely.", "yeah, everyone knows that.", "yep!"
							  "I'm sure in some way that's true..", "affirmative!"]

		cody_denials 	   = ["not even a little bit.", "I'm sorry, but no.", "not really."
							  "absolutely not!", "you made that up.", "hahahahaha no.", 
							  "uh, no.", "not at all.", "of course! uh wait, actually no, not really, no."]

		cody_uncertain	   = ["I really don't know.", "maybe? I'm not convinced anyone really knows that.", 
							  "probably, maybe not?", "leave me out of this!", "who knows?",
							  "I don't understand the question and I won't respond to it."]

		return random.choice(cody_confirmations + cody_denials + cody_uncertain)

	def google(self, msg):
		'''Returns number of hits and top hit for google search. syntax: ".g <search query>"'''

  		service = build("customsearch", "v1", developerKey=self.bot.google_api)
		res 	= service.cse().list(q=msg, cx='017862400283580639479:vmpb_0pljne').execute()
		results = res['queries']['request'][0]['totalResults']
		top 	= res['items'][0]['formattedUrl']
		title   = res['items'][0]['title']

		s   = top + ' - '+title+' ('+results+' hits)'


		return s.encode('ascii')

	def python(self, msg):
		'''Evaluates a python expression and returns the result. syntax: ".py <expression>"'''

		python_expression 	= urllib.quote_plus(msg).replace("+", "%20")
		parse_URI	     	= 'http://tumbolia.appspot.com/py/'
		tumbolia_req 	    = urllib2.Request(parse_URI + python_expression)

		try:
			response = urllib2.urlopen(tumbolia_req, timeout=3).read()
			return response
		
		except urllib2.URLError, e:
			if hasattr(e, 'reason'):
				return 'Failed to reach the server. Reason: '+e.reason
			elif hasattr(e, 'code'):
				return 'The server couldn\'t fulfill the request. Reason: ' + e.code

			return str(e)



	def version(self):

		path 			= self.bot.FILE_NAME #get path of currently running file, including filename
		codyVersion 	= path[-6:-3]
		return 'I am currently running version: '+codyVersion