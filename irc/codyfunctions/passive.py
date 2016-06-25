#!/usr/bin/python
#-*- coding: utf8 -*-

import os, time, datetime, sys, linux_metrics, feedparser

from error_handling import writeError

def codyGreeting(self):
	
	try:
		if  self.HOME_CHANNEL in self.MSG_CHANNEL\
		and 'JOIN' in self.MSG_TYPE\
		and self.BOT_NICKNAME not in self.MSG_NICK:
			
			try:
				adminNumber = self.ADMIN_NICKS.index(self.MSG_NICK.lower())
				self.IRC.send ('PRIVMSG #code :'+ str(random.choice(self.ADMIN_GREETINGS[adminNumber])) +'\r\n')
			except:
				writeError("cody_Greeting in passive.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

	except Exception as e:
		writeError("codyGreeting in passive.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyFeeds(self, trigger):

	try:
		#TURN OFF FEEDS
		if '!cody.feeds' in trigger \
		and self.POST_CODY_FEEDS:
			self.POST_CODY_FEEDS = False
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :RSS feeds are now turned off.\r\n')

		#TURN ON FEEDS
		elif '!cody.feeds' in trigger \
		and not self.POST_CODY_FEEDS:
			self.POST_CODY_FEEDS = True
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :RSS feeds are now turned on.\r\n')

	    #CHECK FOR NEW DATA 4 TIMES AN HOUR
		elif 'codyFeeds' in trigger \
		and (datetime.datetime.now().minute % 14) == 0 \
		or '!cody.feedme' in trigger:
			
			#FETCH THE FEEDS AND PREPARE DATA FOR POSTING
			feed = feedparser.parse(self.RSS_FEEDS)
						
			
			#SPECIAL EXCEPTION - NYAA.EU
			feedData 	= {}
			checkfile 	= open(self.FILE_DIR+"resources/rssFeeds.db", "r").read()
			newData 	= []

			#FILL A DICTIONARY WITH THE RESULTS OF THE FEEDPARSER.PARSE METHOD
			for item in feed["entries"]:
				feedData[feed["entries"].index(item)]				 = {}
				feedData[feed["entries"].index(item)]['torrentlink'] = feed["entries"][feed["entries"].index(item)]["id"]
				feedData[feed["entries"].index(item)]['title'] 		 = feed["entries"][feed["entries"].index(item)]["title"]
				feedData[feed["entries"].index(item)]['subsFilter']	 = feed["entries"][feed["entries"].index(item)]["tags"][0]["term"]
				feedData[feed["entries"].index(item)]['content']	 = feedData[feed["entries"].index(item)]['title'] + " --> " + feedData[feed["entries"].index(item)]['torrentlink']
			
			#CHECK THE DICTIONARY
			for item in feedData.keys():

				#CREATE A TEMP VARIABLE
				newDataItem = ''

				#THROW OUT NON-ASCII CHARACTERS
				for char in feedData[item]['content']:
					newDataItem = newDataItem + char.encode('ascii', 'ignore')
				
				#CHECK FOR AND THROW OUT RESULTS WITH BAD SUBS OR NON-ENGLISH SUBS
				if feedData[item]['subsFilter'] != "English-translated Anime" \
				or  "horrible" 	in feedData[item]['title'].lower():
					feedData.pop(item)

				#COMPARE DICTIONARY TO FILE, CHECK FOR NEW DATA
				elif newDataItem not in checkfile:
					newData.append(newDataItem)
				
			#WRITE NEW DATA TO FILE IF IT EXISTS
			if newData:
				
				#REMAKE THE FILE IF THE FILE NOW EXCEEDS 500 LINES
				if len(checkfile.splitlines()) > 500:
					with open(self.FILE_DIR+"resources/rssFeeds.db", "w") as feedfile:
						for item in feedData.keys():
							feedfile.write('\n')
							feedfile.write(feedData[item]['content'].encode('utf-8') + '\r\n')

						feedfile.close()

				#IF NOT, JUST APPEND TO IT
				else:
					with open(self.FILE_DIR+"resources/rssFeeds.db", "a") as feedfile:
						for item in newData:
							feedfile.write('\n')
							feedfile.write(newData[newData.index(item)] + '\r\n')

						feedfile.close()
			
			#PRINT NEW DATA TO CHANNEL
			for item in newData:
				
				self.IRC.send('PRIVMSG '+self.RSS_FEED_CHANNELS+' :' + newData[newData.index(item)] + '\r\n' )
				time.sleep(1.5)

	except Exception as e:
		writeError("codyFeeds() in passive.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyMonitor(self, trigger):

	try:
		if (datetime.datetime.now().second == 59) and self.MONITOR_CHECK != datetime.datetime.now().minute:

			used, total, _, _, _, _ = linux_metrics.mem_stat.mem_stats()
			used   = float(used)
			total  = float(total)
			output = round(((used / total) * 100),2)

			if output > 90.0 and self.ALERT_HOUR != datetime.datetime.now().hour:
	
				self.IRC.send("PRIVMSG "+self.HOME_CHANNEL+ " :Inveracity, lmn, guys, I think the server is on fire. Memory load is currently at "+str(output)+"%! Maybe restart it or something. \r\n")
				self.ALERT_HOUR = datetime.datetime.now().hour

			self.MONITOR_CHECK = datetime.datetime.now().minute

	except Exception as e:
		writeError("codyMonitor() in passive.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))


def codyFileUpdates(self, trigger):

	try:
		if '!cody.updates' in trigger\
		and self.POST_CODY_FILE_UPDATES:
			self.POST_CODY_FILE_UPDATES = False
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :File updates are now turned off.\r\n')

		elif '!cody.updates' in trigger\
		and not self.POST_CODY_FILE_UPDATES:
			self.POST_CODY_FILE_UPDATES = True
			self.IRC.send('PRIVMSG '+self.MSG_CHANNEL+' :File updates are now turned on.\r\n')

		elif 'codyFileUpdates' in trigger:

			if (datetime.datetime.now().second % 3) == 0 : 
				
				#fetch current file update time - syntax is 'Sun Apr 21 20:24:36 2013'
				lastUpdatedRealTime = time.ctime(os.path.getmtime(self.FILE_PATH))
				lastUpdatedCody 	= lastUpdatedRealTime.split()
				
				#fetch last recorded update time
				lastRecorded 		= open(self.FILE_DIR+"resources/lastupdated.db", "r")
				lastRecordedCody	= lastRecorded.read().split()
				lastRecorded.close()
				
				#parse recorded time into datetime ints
				if len(lastRecordedCody) == 5:
					lastRecordedYear 	= int(lastRecordedCody[4])
					lastRecordedMonth   = int(time.strptime(lastRecordedCody[1],'%b').tm_mon)
					lastRecordedDay		= int(lastRecordedCody[2])
					lastRecordedTime 	= lastRecordedCody[3].split(':')
					lastRecordedHour	= int(lastRecordedTime[0])
					lastRecordedMinute	= int(lastRecordedTime[1])
					lastRecordedSecond	= int(lastRecordedTime[2])

				#parse current time into datetime ints
				lastUpdatedYear 	= int(lastUpdatedCody[4])
				lastUpdatedMonth    = int(time.strptime(lastUpdatedCody[1],'%b').tm_mon)
				lastUpdatedDay		= int(lastUpdatedCody[2])
				lastUpdatedTime 	= lastUpdatedCody[3].split(':')
				lastUpdatedHour		= int(lastUpdatedTime[0])
				lastUpdatedMinute	= int(lastUpdatedTime[1])
				lastUpdatedSecond	= int(lastUpdatedTime[2])

				#turn them both into datetime objects
				if len(lastRecordedCody) == 5:
					lastRecordedCody = datetime.datetime(lastRecordedYear, lastRecordedMonth, lastRecordedDay, lastRecordedHour, lastRecordedMinute, lastRecordedSecond)

				else: 
					lastRecordedCody = datetime.datetime(2000,1,1)
				
				lastUpdatedCody = datetime.datetime(lastUpdatedYear,  lastUpdatedMonth,  lastUpdatedDay,  lastUpdatedHour, 	lastUpdatedMinute, 	lastUpdatedSecond)

				#check if it has changed
				if lastRecordedCody < lastUpdatedCody :
					if self.POST_CODY_FILE_UPDATES:
						self.IRC.send('PRIVMSG '+self.HOME_CHANNEL+' :'+self.FILE_NAME+' has been updated.\r\n')
					dbWrite = open(self.FILE_DIR+"resources/lastupdated.db", "w")
					dbWrite.write(lastUpdatedRealTime)
					dbWrite.close()

	except Exception as e:
		writeError("codyFileUpdates() in passive.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))