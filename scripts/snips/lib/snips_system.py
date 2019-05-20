#!/usr/bin/python

# +--------------------------------------------------+
# |               SNIPS SYSTEM LIBRARY               |
# +--------------------------------------------------+
#
#   Description:
#     Library for changing settings like volume or
#	  TV or device power
#    
#   Author:
#     Vasco Baptista <vascojdb@gmail.com>
#
#

import os
import random
#import commands

class snips_system:
	def __init__(self, logger, conf):
		self.logger = logger
		self.confirmationWords = ['Ok!', 'Sure!', 'No problem!', 'Alright!', 'Of course!', 'Fine!']
		self.logger.info('Starting SNIPS System instance')

	def volumeDown(self, value):
		# Defaults to 10%:
		if value is None:
			value = 10
		# Reduce the volume by the specific percentage value:
		os.system('amixer -M sset "PCM" {}%- &>/dev/null'.format(value))
		self.logger.info('Reducing the volume by {}%'.format(value))
		# Build answer:
		tts = random.choice(self.confirmationWords)		
		self.logger.debug('Answering: {}'.format(tts))
		return tts
		
	def volumeUp(self, value):
		# Defaults to 10%:
		if value is None:
			value = 10
		# Increase the volume by the specific percentage value:
		os.system('amixer -M sset "PCM" {}%+ &>/dev/null'.format(value))
		self.logger.info('Increasing the volume by {}%'.format(value))
		# Build answer:
		tts = random.choice(self.confirmationWords)		
		self.logger.debug('Answering: {}'.format(tts))
		return tts
	
	def volumeSet(self, value):
		# Defaults to 10%:
		if value is None:
			tts = 'Sorry, you need to specify a volume level from 0 to 100 percent.'
		else:
			# Set the volume to a specific percentage value:
			os.system('amixer -M sset "PCM" {}% &>/dev/null'.format(value))
			self.logger.info('Setting the volume to {}%'.format(value))
			# Build answer:
			tts = random.choice(self.confirmationWords)		
		self.logger.debug('Answering: {}'.format(tts))
		return tts
	
	def screenOn(self):
		# Sends the CEC command to turn the screen ON:
		os.system('echo on 0 | cec-client -s -d 1 &>/dev/null')
		self.logger.info('Turning the screen ON'.format(value))
		# Build answer:
		tts = random.choice(self.confirmationWords)		
		self.logger.debug('Answering: {}'.format(tts))
		return tts
	
	def screenOff(self):
		# Sends the CEC command to turn the screen OFF:
		os.system('(sleep 5 && echo standby 0 | cec-client -s -d 1 &)')
		self.logger.info('Turning the screen OFF'.format(value))
		# Build answer:
		tts = random.choice(self.confirmationWords)		
		self.logger.debug('Answering: {}'.format(tts))
		return tts
		
	def systemInfo(self):
		self.logger.info('Getting system information...')

		uptime_tts = 'System is up for {}. '.format(commands.getstatusoutput('uptime -p')[1].replace('up ',''))
		cpu_temp_tts = 'CPU temperature is {} degrees. '.format(commands.getstatusoutput('/opt/vc/bin/vcgencmd measure_temp')[1].replace('temp=','').split('.')[0])
		total_ram = int(commands.getstatusoutput('free -t | grep "Total" | awk \'{print $2}\'')[1])
		used_ram = int(commands.getstatusoutput('free -t | grep "Total" | awk \'{print $3}\'')[1])
		used_ram_tts = 'Used RAM is {} percent. '.format((used_ram*100) / total_ram)
		used_hdd_tts = 'Used disk space is {} percent. '.format(commands.getstatusoutput('df -h | grep "/dev/root" | awk \'{print $5}\'')[1].replace('%',''))
	
		# Build answer:
		tts = uptime_tts + cpu_temp_tts + used_ram_tts + used_hdd_tts
		self.logger.debug('Answering: {}'.format(tts))
		return tts
