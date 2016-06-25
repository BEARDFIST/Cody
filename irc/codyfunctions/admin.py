#!/usr/bin/python
#-*- coding: utf8 -*-

import os, sys, datetime, json, os, py_compile, time, linux_metrics, compileall

from subprocess 	 import Popen, PIPE, STDOUT
from urllib2         import Request, urlopen, URLError
from error_handling  import writeError
from multiprocessing import Process

def codyQuit(self, trigger):
		
	try:
		self.IRC.send ( 'QUIT :terminating..\r\n' )
		# sys.exit(0) would only kill this particular thread, instead calling os._exit will find the process of the main thread and kill it there
		os._exit(1)

	except Exception as e:
		writeError("codyQuit() in admin.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))
	

def codyReload(self, trigger):
	FILE = self.FILE_PATH
	try:
		self.IRC.send ( 'QUIT :terminating..\r\n' )
		#TODO: Parameter to load new cody - stop current, start new cody
		#TODO: do compile check on all modules / also confirm that compileall actually comes back with compiler errors
		#TODO: Change logging path to dropbox folder?
		# call the daemon in a child process independant
		# to avoid killing the thread before it gets a chance to start cody
		def restart_daemon():
			#make sure the parent process has terminated before rebooting cody
			time.sleep(1)
			cmd = ["python", FILE, "restart"]
			pro = Popen(cmd, stdout = PIPE, stderr = PIPE)
			pro.communicate()
			# Terminate child process once complete
			os._exit(1) 

		# kick off the child process
		p = Process(target=restart_daemon)
		p.start()
		# Terminate parent process
		os._exit(1)

	except Exception as e:
		writeError("codyreload in admin.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

	"""
	BODY = self.MSG_BODY
	FILE = self.FILE_NAME #fullpath and file
	PATH = self.FILE_PATH
	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n'):
			try:
				newCody = BODY.split()
				newCody = newCody[1]

			except:
				newCody = 'NULL'
					
		#else if no file is supplied, reload the running version
		else:
			newCody = FILE

		folderPath = PATH

		if os.path.isfile(folderPath + newCody):

			try:
				py_compile.compile(folderPath + newCody, doraise = True)
				compileall.compile_dir(PATH+'/codyfunctions', force=True)

			except py_compile.PyCompileError as e:
				writeError("cody_reload in public.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))
				errorMessage = str(e)
				self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :'+errorMessage+'. \r\n' )

			else:
				args = sys.argv[:]
				args.insert(0, sys.executable)
				os.chmod(folderPath + newCody, stat.S_IRWXU)
				self.IRC.send ( 'QUIT :reloading myself\r\n' )
				os.chdir(folderPath)
				os.execv(sys.executable, args)


		else:
			self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :File not found! \r\n' )

	except Exception as e:
		writeError("codyreload in admin.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))		
	"""
def joinChannel(self, trigger):

	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n') \
		and '#' in self.MSG_BODY :
			self.IRC.send ( 'PRIVMSG '+self.MSG_CHANNEL+' :Joining channel:'+self.MSG_BODY[len('!cody.join'):]+'\r\n')
			self.IRC.send ( 'JOIN '   +self.MSG_BODY[len('!cody.join'):]+'\r\n' )
			
		else:
			self.IRC.send( 'PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.join [#channel]\r\n' )

	except Exception as e:
		writeError("joinChannel() in admin.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def partChannel(self, trigger):

	try:
		if len(self.MSG_BODY) > len('!cody.join\r\n') \
		and '#' in self.MSG_BODY :
			self.IRC.send 	( 'PRIVMSG '+self.MSG_CHANNEL+' :Leaving channel:'+self.MSG_BODY[len('!cody.part'):]+'\r\n')
			self.IRC.send 	( 'PART '+self.MSG_BODY[len('!cody.part'):]+'\r\n' )
		else:
			self.IRC.send 	('PRIVMSG '+self.MSG_CHANNEL+' :Usage: !cody.part [#channel] ' + '\r\n' )

	except Exception as e:
		writeError("join_Channel() in admin.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))


def codyPortscan(self, trigger):

	try:
		if len(self.MSG_BODY) > len(trigger + '\r\n'):
			if "/" not in self.MSG_BODY \
			and "," not in self.MSG_BODY \
			and "-" not in self.MSG_BODY:

				commandinput = self.MSG_BODY.split(' ')
				
				if len(commandinput) == 3:

					ip = str(commandinput[2][:-len('\r\n')])
					port = str(commandinput[1])
					cmd = ["nmap","-PN", "-p", port, ip]

					pro = Popen(cmd, stdout = PIPE, stderr = PIPE)

					output = pro.communicate()

					if output[0]:
						yanked 				= output[0]
						splityank 			= yanked.partition("SERVICE")
						
						print splityank[2]

						if "MAC" in splityank[2]:
							splityankagain 	= splityank[2].partition("MAC")
							result 			= splityankagain[0]
							result 			= result.split()

						else:
							splityankagain 	= splityank[2].partition("Nmap")
							result 			= splityankagain[0]
							
							if result:
								result 		= result.split()

						if len(result) > 0:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :port: "+str(result[0])+" state: "+str(result[1])+"\r\n")

						else:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :no information could be retrieved\r\n")
					else:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :service not available\r\n")
				else:		
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :wrong command, try again\r\n")
			else:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :Illegal character detected\r\n")
		else:
							self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :usage: !cody.portscan <portnumber> <ipaddress>\r\n")

	except Exception as e:
		writeError("codyPortscan() in admin.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))


def codyDiag(self, trigger):
	
	msg_channel = self.MSG_CHANNEL #prevent NULL channel by storing the variable locally // Race Condition
	
	try:
		def cpuUsage():
			cpu_pcts = linux_metrics.cpu_stat.cpu_percents(sample_duration=1)
			output = '%.2f%%' % (100 - cpu_pcts['idle']) 
				
			return output

		def memStats():

			used, total, _, _, _, _ = linux_metrics.mem_stat.mem_stats()
			used   = float(used)
			total  = float(total)
			output = str(round(((used / total) * 100),2))

			return output			

		def disk_usage(path):

			st 		= os.statvfs(path)
			free 	= st.f_bavail  * st.f_frsize
			total 	= st.f_blocks  * st.f_frsize
			used 	= (st.f_blocks - st.f_bfree) * st.f_frsize

			total 	= total / (1024*1024)
			free 	= free  / (1024*1024)
			used 	= used  / (1024*1024)

			disk_stats = [total, used, free]

			return disk_stats

		def sys_uptime():
			cmd 	= ["uptime | cut -d ' ' -f 4"]
			pro 	= Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
			output 	= pro.communicate()

			if 'day' in output:
				output	= str(output[0]).split()

			else:
				output = [0]

			return output
		
		diskStats = disk_usage("/")
		cpuStats  = cpuUsage()
		sysUptime = sys_uptime()
		memStats  = memStats()

		if diskStats and cpuStats:
			orange 		= self.ircmsg_Color + self.ircmsg_Orange +" "
			lcyan 		= self.ircmsg_Color + self.ircmsg_LightCyan +" "
			dgreen 		= self.ircmsg_Color + self.ircmsg_DarkGreen +" "
			reset 		= self.ircmsg_Reset +" "
			self.IRC.send("PRIVMSG "+msg_channel+ " :"+ \
														        "Disk capacity: total " + orange +str(diskStats[0])+ "MB "	 +\
														reset + "used " 				+ orange +str(diskStats[1])+ "MB "	 +\
														reset + "free " 				+ orange +str(diskStats[2])+ "MB "	 +\
														reset + "| CPU Usage: " 		+ orange +str(cpuStats)              +\
														reset + "| Memory Usage: " 		+ orange +str(memStats)    + "% "    +\
														reset + "| System uptime: " 	+ orange +str(sysUptime[0])+ " days "+\
														"\r\n")
		else:
			self.IRC.send("PRIVMSG "+msg_channel+ " :An error occured while processing your request\r\n")

	except Exception as e:
		writeError("codyDiag() in admin.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyNick(self, trigger):

	try: 
		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			inputstring = self.MSG_BODY.split(" ")
			newnick	= " ".join(inputstring[1:]).strip("\r\n")

			self.IRC.send( 'NICK '+newnick+'\r\n' )

		else:
			self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :!cody.nick <new nick>\r\n")

	except Exception as e:
		writeError("codyNick() in admin.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))

def codyGhost(self, trigger):

	try:		
		if len(self.MSG_BODY) > len(trigger + '\r\n'):

			inputstring = self.MSG_BODY.split(" ")
			newnick	= " ".join(inputstring[1:]).strip("\r\n")

			self.IRC.send("PRIVMSG "+self.NICKSERV_ADRESS+' :ghost '+oldnick+'\r\n')

		else:
			self.IRC.send("PRIVMSG "+self.MSG_CHANNEL+ " :!cody.ghost <ghost nick>\r\n")			

	except Exception as e:
		writeError("codyGhost() in admin.py "+str(e)+" line "+str((sys.exc_info()[2]).tb_lineno))