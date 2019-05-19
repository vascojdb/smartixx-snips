#!/usr/bin/python

# +--------------------------------------------------+
# |           SNIPS TIME AND DATE LIBRARY            |
# +--------------------------------------------------+
#
#   Description:
#     Library for getting the current date and time
#    
#   Author:
#     Vasco Baptista <vascojdb@gmail.com>
#
#

import datetime

class snips_timedate:
	def __init__(self, logger, conf):
		self.logger = logger
		self.logger.info('Starting SNIPS Time and Date instance')
	
	def getDate(self):
		now = datetime.datetime.now()
		weekday = now.strftime("%A")
		day = now.strftime("%d")
		month = now.strftime("%B")
		year = now.strftime("%Y")
		# Build answer:
		tts = 'Today is {}, {} of {}, {}.'.format(weekday, day, month, year)
		self.logger.debug('Answering: {}'.format(tts))
		return tts
	
	def getTime(self):
		now = datetime.datetime.now()
		hour = now.strftime("%I")
		minute = now.strftime("%M")
		ampm = now.strftime("%p")
		# Build answer:
		tts = 'It is {}:{} {}.'.format(hour, minute, ampm)
		self.logger.debug('Answering: {}'.format(tts))
		return tts
