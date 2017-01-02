import yaml
import os

def config():
	configfile = os.sep.join(__file__.split(os.sep)[:-1])+os.sep+'config.yml'
	with open(configfile, 'r') as cf:
		config_raw = cf.read()

	return yaml.safe_load(config_raw)

#print config()['admins']