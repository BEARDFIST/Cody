#!/usr/bin/python
#-*- coding: utf8 -*-
import contextlib
from urllib 		import urlencode
from urllib2        import urlopen



class Public():
	def shorten_url(self, url):
		request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))
		with contextlib.closing(urlopen(request_url)) as response:
			return response.read().decode('utf-8')

