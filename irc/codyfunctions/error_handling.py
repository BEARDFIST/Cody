import os, datetime, time

def writeError(errorMessage):
	logpath = '/var/log/cody'

	timestamp = time.time()
	timenow   = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

	if os.path.exists(logpath):
		with open(logpath,'a') as log: #append
			log.write(timenow +" : "+ errorMessage+'\r\n')
		log.close

	else:
		with open(logpath,'w') as log: #append
			log.write(timenow +" : "+ errorMessage+'\r\n')
		log.close