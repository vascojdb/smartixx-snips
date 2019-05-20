#!/usr/bin/python

# +--------------------------------------------------+
# |            SNIPS ONLINE RADIO LIBRARY            |
# +--------------------------------------------------+
#
#   Description:
#     Library for playing online radio streams
#     via mpg123 and a local station file
#    
#   Author:
#     Vasco Baptista <vascojdb@gmail.com>
#
#

import os
import random

class snips_onlineradio:
	def __init__(self, logger, conf):
		self.logger = logger
		self.confirmationWords = ['Ok!', 'Sure!', 'No problem!', 'Alright!', 'Of course!', 'Fine!']
		self.logger.info('Starting SNIPS Online radio instance')

	def radioOn(self, station):
		if station is None:
			# Sound not specified:
			tts = 'Sorry, I did not recognize the radio station to play.'
		else:
			# Find station url here from file:
			# ...
			# ...
			station_url = None
			station_name = None
			
			
			if station_url is None:
				tts = 'Sorry, I did not find any stations with that name'
			else:
				# Found the sound type:
				tts = random.choice(self.confirmationWords) + ' Playing radio {}, here you go!'.format(station_name)
				
				# Make sure all other instances of mpg123 are killed:
				os.system('killall /usr/bin/mpg123 2>/dev/null')
				self.logger.debug('Stopping any instances of mpg123')
				
				# Play the stream after a short delay (to give time for the TTS to speak):
				os.system('(sleep 5 && /usr/bin/mpg123 --scale 8000 -q -o alsa {} &)'.format(station_url))
				self.logger.info('Playing radio "{}" from url: {}'.format(station_name, station_url))

		self.logger.debug('Answering: {}'.format(tts))
		return tts

	def stop(self):
		os.system('killall /usr/bin/mpg123 2>/dev/null')
		self.logger.info('Stopping any instances of mpg123')
		
		tts = random.choice(self.confirmationWords)
		self.logger.debug('Answering: {}'.format(tts))
		return tts
