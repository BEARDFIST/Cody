#codyModules.py


#MakeFile(file_name): makes a file.

def MakeFile(file_name):

	temp_path = "/root/Dropbox/Cody/resources/" + file_name
	filevar = open(temp_path, 'w')
	filevar.write('')
	filevar.close()
 
#Randomizer

def noRepeatRandom(maxLength, dbName):
	
	import random
	import os
	
	fillNeeded = False
		
	#IF THE FILE DOESN'T EXIST, WE CREATE IT AND READ IT
	if os.path.isfile("/root/Dropbox/Cody/resources/"+dbName+".db") == True:
		readSalt 		= open("/root/Dropbox/Cody/resources/"+dbName+".db", "r")
		readAntiSalt 	= open("/root/Dropbox/Cody/resources/anti"+dbName+".db", "r")
		salt 				= readSalt.read().splitlines()
		antiSalt 			= readAntiSalt.read().splitlines()	

		#CHECK IF MAXLENGTH HAS INCREASED OR DECREASED SINCE FILES WERE CREATED
		if maxLength != ( len(salt) + len(antiSalt) ) :
			MakeFile(dbName+".db")
			MakeFile("anti"+dbName+".db")
			fillNeeded		= True

	#ELSE - READ THE FILES INTO STRING
	else: 
		MakeFile(dbName+".db")
		MakeFile("anti"+dbName+".db")
		fillNeeded		= True

	#IF WE JUST CREATED THE FILES, WE NEED TO FILL UP SOME SALT
	if fillNeeded == True :
	
		writeSalt 			= open("/root/Dropbox/Cody/resources/"+dbName+".db", "w")
		writeAntiSalt 		= open("/root/Dropbox/Cody/resources/anti"+dbName+".db", "w")
		saltArray 			= range(maxLength)
		i 					= 0
		

		while i < len(saltArray):
			print>>writeSalt, saltArray[i]
			i += 1

		writeSalt.close()
		writeAntiSalt.close()
		
		readSalt 		= open("/root/Dropbox/Cody/resources/"+dbName+".db", "r")
		readAntiSalt 	= open("/root/Dropbox/Cody/resources/anti"+dbName+".db", "r")
		salt 				= readSalt.read().splitlines()
		antiSalt 			= readAntiSalt.read().splitlines()	


	#CHECK IF SALT IS STILL EMPTY. IF EMPTY, SWITCH IT WITH ANTISALT.
	if len(salt) 	== 0 :
		salt 		= antiSalt[:] 
		antiSalt[:] = []  
	
	#append the lists with a random choice from salt and return the number
	
	chosenOne = random.choice(salt) # choose another random
	antiSalt.append(chosenOne)
	salt.remove(chosenOne)		

	#WRITE LISTS TO FILES
	writeSalt 		= open("/root/Dropbox/Cody/resources/"+dbName+".db", "w")
	writeAntiSalt 	= open("/root/Dropbox/Cody/resources/anti"+dbName+".db", "w")

	i = 0
	while i < len(salt):
		print>>writeSalt, salt[i]
		i += 1

	i = 0
	while i < len(antiSalt):
		print>>writeAntiSalt, antiSalt[i]
		i += 1

	writeSalt.close()
	writeAntiSalt.close()
	return int(chosenOne)


#data parser
def dataParse(data):
	if data[0] == ':':
		#first let's fetch the NICK
		parseMsg = data[1:]
		bangPos  = parseMsg.find('!')
		NICK	 = parseMsg[:bangPos]  
	
		#next, we'll fetch the hostname
		parseMsg = parseMsg[bangPos + 1:]
		spacePos = parseMsg.find(' ')
		HOSTNAME = parseMsg[:spacePos]
	
		#now we'll fetch MSG_TYPE
		parseMsg = parseMsg[spacePos + 1:]
		spacePos = parseMsg.find(' ')
		MSG_TYPE = parseMsg[:spacePos]
	
		#we fetch CHANNEL
		parseMsg = parseMsg[spacePos + 1:]
		spacePos = parseMsg.find(' ')
		CHANNEL  = parseMsg[:spacePos]
	
		#now we'll fetch MESSAGE
		parseMsg = parseMsg[spacePos + 2:] # +2 to skip the colon
		MESSAGE  = parseMsg[:]

		#then return everything
		return [NICK, HOSTNAME, MSG_TYPE, CHANNEL, MESSAGE]
	
	else:
		#DO NOT PARSE
		return ['NULL','NULL','NULL','NULL','NULL']



#addFeature
def addFeature(feat, NICK):
	#OPEN FILES FOR READ AND READ THEM INTO LOCAL 
	readFeatures	 		= open("/root/Dropbox/Cody/userFeedback/featureRequests.txt", "r")
	Features 				= readFeatures.read().splitlines()
	startLine 				= len(Features) / 2
	feat 					= str(startLine) + '. ' + feat[:-2] + ' [' + NICK + ']' + '\r\n'
	
	Features.append(feat)
		
	#WRITE STRINGS TO FILES
	writeFeatures	 		= open("/root/Dropbox/Cody/userFeedback/featureRequests.txt", "w")
	
		
	i = 0
	while i < len(Features):
			
		if Features[i] != '':
			print>>writeFeatures, Features[i]
			print>>writeFeatures, ''
			i += 1

		else:
			i += 1

	writeFeatures.close()



#addBug
def addBug(feat, NICK):
	#OPEN FILES FOR READ AND READ THEM INTO LOCAL
	readFeatures= open("/root/Dropbox/Cody/userFeedback/bugReports.txt", "r")
	
		
	Features 				= readFeatures.read().splitlines()
	startLine 				= len(Features) / 2
	feat 					= str(startLine) + '. ' + feat[:-2] + ' [' + NICK + ']' + '\r\n'
	Features.append(feat)
		
	#WRITE STRINGS TO FILES
	writeFeatures = open("/root/Dropbox/Cody/userFeedback/bugReports.txt", "w")
			
		
	i = 0
	while i < len(Features):
			
		if Features[i] != '':
			print>>writeFeatures, Features[i]
			print>>writeFeatures, ''
			i += 1

		else:
			i += 1

	writeFeatures.close()


#!cody.uptime
def codyUptime(total_seconds):
  
    #Defining time variables:
    MINUTE  =   60
    HOUR    =   MINUTE  * 60
    DAY     =   HOUR    * 24
 
    #Calculate seconds into days, hours and minutes:
    days    = int(  total_seconds / DAY  )          
    hours   = int( (total_seconds % DAY  ) / HOUR   )
    minutes = int( (total_seconds % HOUR ) / MINUTE )
 
    # UPTIME = "X days, X hours, X minutes)
    uptimeString = ""

    if days > 0:
        uptimeString += str(days) + " " + (days == 1 and "day" or "days" ) + ", "

    if len(uptimeString) > 0 or hours > 0:
        uptimeString += str(hours) + " " + (hours == 1 and "hour" or "hours" ) + ", "

    uptimeString += str(minutes) + " " + (minutes == 1 and "minute" or "minutes" ) + ". "
        
    return uptimeString;

