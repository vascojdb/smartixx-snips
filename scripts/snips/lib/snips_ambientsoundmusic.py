#!/usr/bin/python

# +--------------------------------------------------+
# |      SNIPS AMBIENT SOUND AND MUSIC LIBRARY       |
# +--------------------------------------------------+
#
#   Description:
#     Library for playing ambient sounds and music
#     from a network folder
#    
#   Author:
#     Vasco Baptista <vascojdb@gmail.com>
#
#

import os
import random

class snips_ambientsoundmusic:
	def __init__(self, logger, conf):
		self.logger = logger
		self.confirmationWords = ['Ok!', 'Sure!', 'No problem!', 'Alright!', 'Of course!', 'Fine!']
		self.sounds_path = conf['ambientsoundmusic']['sounds_path'] if 'sounds_path' in conf['ambientsoundmusic'] else None
		self.music_path = conf['ambientsoundmusic']['music_path'] if 'music_path' in conf['ambientsoundmusic'] else None
		self.logger.info('Starting SNIPS Ambient sounds and music instance')

	def playSounds(self, type):
		if type is None:
			# Sound not specified:
			tts = 'Sorry, you need to tell me the type of sounds you want to listen to. You can ask me which types of sounds I can play'
		else:
			# Verify if any file with the type exists:
			if os.system('ls {}/*{}_* 2>/dev/null'.format(self.sounds_path, type.capitalize())) == 0:
				# Found the sound type:
				tts = random.choice(self.confirmationWords) + ' here you go!'
				
				# Make sure all other instances of mpg123 are killed:
				os.system('killall /usr/bin/mpg123 2>/dev/null')
				self.logger.info('Stopping any instances of mpg123')
				
				# Play the sounds after a short delay (to give time for the TTS to speak):
				os.system('(sleep 5 && /usr/bin/mpg123 --scale 8000 -Zq -o alsa {}/*{}_* &)'.format(self.sounds_path, type.capitalize()))
				self.logger.info('Starting instance of mpg123, playing files from: {}, type: {}'.format(self.sounds_path, type.capitalize()))
			else:
				# Did not find the sound type:
				tts = 'Sorry, I did not find any {} sounds. You can ask me which types of sounds I can play'.format(type)
				
		self.logger.debug('Answering: {}'.format(tts))
		return tts
	
	def listSounds(self):
		types = []
		# r=root, d=directories, f = files
		for r, d, f in os.walk(self.sounds_path):
			for file in f:
				if '.mp3' in file:
					# Remove the file extension:
					tmp = file.split('.')[0].split('_')
					# Get only the parts of the files (types) and exclude the numbers:
					for type in tmp:
						if not type.isdigit():
							if not type in types:
								types.append(type)
		# Sort the types (A-Z)
		types.sort()
		# Build the sentence to say:
		tts = 'I can play the following sounds:'
		for i in range(len(types)):
			if i == len(types)-1:
				tts = '{} and {}.'.format(tts, types[i])
			else:
				tts = '{} {},'.format(tts, types[i])
			
		self.logger.debug('Answering: {}'.format(tts))
		return tts

	def playMusic(self, type):
		if type is None:
			# Music not specified:
			tts = 'Sorry, you need to tell me the type of music you want to listen to. You can ask me which types of music I can play'
		else:
			# Verify if any file with the type exists:
			if os.system('ls {}/*{}_* 2>/dev/null'.format(self.music_path, type.capitalize())) == 0:
				# Found the music type:
				tts = random.choice(self.confirmationWords) + ' here you go!'
				
				# Make sure all other instances of mpg123 are killed:
				os.system('killall /usr/bin/mpg123 2>/dev/null')
				self.logger.info('Stopping any instances of mpg123')
				
				# Play the sounds aftre a short delay (to give time for the TTS to speak):
				os.system('(sleep 5 && /usr/bin/mpg123 --scale 8000 -Zq -o alsa {}/*{}_* &)'.format(self.music_path, type.capitalize()))
				self.logger.info('Starting instance of mpg123, playing files from: {}, type: {}'.format(self.music_path, type.capitalize()))
			else:
				# Did not find the music type:
				tts = 'Sorry, I did not find any {} music. You can ask me which types of music I can play'.format(type)
				
		self.logger.debug('Answering: {}'.format(tts))
		return tts
	
	def listMusic(self):
		types = []
		# r=root, d=directories, f = files
		for r, d, f in os.walk(self.music_path):
			for file in f:
				if '.mp3' in file:
					# Remove the file extension:
					tmp = file.split('.')[0].split('_')
					# Get only the parts of the files (types) and exclude the numbers:
					for type in tmp:
						if not type.isdigit():
							if not type in types:
								types.append(type)
		# Sort the types (A-Z)
		types.sort()
		# Build the sentence to say:
		tts = 'I can play the following music:'
		for i in range(len(types)):
			if i == len(types)-1:
				tts = '{} and {}.'.format(tts, types[i])
			else:
				tts = '{} {},'.format(tts, types[i])
			
		self.logger.debug('Answering: {}'.format(tts))
		return tts

	def stop(self):
		os.system('killall /usr/bin/mpg123 2>/dev/null')
		self.logger.info('Stopping any instances of mpg123')
		
		tts = random.choice(self.confirmationWords)
		self.logger.debug('Answering: {}'.format(tts))
		return tts
