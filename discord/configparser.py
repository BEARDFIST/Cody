import json
import inspect
import os
from sys import platform

configfile = os.sep.join(__file__.split(os.sep)[:-1] + ["config.json"])


def parsejson():
	'''
	Convert JSON into dictionary
	Return False if unsuccessful
	'''
	if os.path.isfile(configfile):
		with open(configfile, "r") as cf:
			raw_config = cf.read()
		cf.close()

		if raw_config:
			try:
				config_dictionary = json.loads(raw_config)
			except:
				print("could not parse JSON object, error in formatting")
				return False

			if isinstance(config_dictionary, dict):
				return config_dictionary

	else:
		print("could not find "+str(configfile))
		return False


