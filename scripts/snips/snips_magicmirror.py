#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging.handlers
import io
from hermes_python.hermes import Hermes
if sys.version_info[0] == 2:
	import ConfigParser as configparser
else:
	import configparser

# Libraries:
from lib.snips_airly import snips_airly
from lib.snips_ambientsoundmusic import snips_ambientsoundmusic
from lib.snips_system import snips_system
from lib.snips_timedate import snips_timedate

# Dont change:
conf = None
logger = None

snips_airly_obj = None
snips_ambientsoundmusic_obj = None
snips_system_obj = None
snips_timedate_obj = None

# Configuration file:
CONFIG_INI = "config.ini"


# +----------------------------------+
# |   Create logger and get handler  |
# +----------------------------------+
def getLogger(level):
	LOG_LEVELS = {
		'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL
	}
	new_logger = logging.getLogger(__name__)
	formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(module)s): %(message)s')
	sh = logging.StreamHandler()
	sh.setFormatter(formatter)
	new_logger.addHandler(sh)
	try:
		new_logger.setLevel(LOG_LEVELS[level.lower()])
	except KeyError:
		new_logger.setLevel(LOG_LEVELS['info'])

	return new_logger


# +----------------------------------+
# |    Configuration file parser     |
# +----------------------------------+
class SnipsConfigParser(configparser.SafeConfigParser):
	def to_dict(self):
		return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


# +----------------------------------+
# |      Read configuration file     |
# +----------------------------------+
def read_configuration_file(configuration_file):
	try:
		with io.open(configuration_file, encoding='utf-8') as f:
			conf_parser = SnipsConfigParser()
			conf_parser.readfp(f)
			return conf_parser.to_dict()
	except (IOError, configparser.Error) as e:
		logger.error('Impossible to read configuration file. Error: {}'.format(e.message))
		return dict()

# +----------------------------------+
# |        Load configuration        |
# +----------------------------------+
def load_configuration(conf):
	# Get the MQTT connection parameters:
	if 'mqtt_ip_addr' not in conf['mqtt']:
		conf['mqtt']['mqtt_ip_addr'] = 'localhost'
		logger.info('No MQTT IP address found, using default: {}'.format(conf['mqtt']['mqtt_ip_addr']))
	if 'mqtt_port' not in conf['mqtt']:
		conf['mqtt']['mqtt_port'] = 1883
		logger.info('No MQTT port found, using default: {}'.format(conf['mqtt']['mqtt_port']))
	return conf

# +----------------------------------+
# |        Initialize objects        |
# +----------------------------------+
def initialize_objects():
	global snips_airly_obj
	global snips_ambientsoundmusic_obj
	global snips_system_obj
	global snips_timedate_obj
	# Create objects:
	if conf['airly']['enabled'] == 'true':
		snips_airly_obj = snips_airly(logger, conf)
	if conf['ambientsoundmusic']['enabled'] == 'true':
		snips_ambientsoundmusic_obj = snips_ambientsoundmusic(logger, conf)
	if conf['system']['enabled'] == 'true':
		snips_system_obj = snips_system(logger, conf)
	if conf['datetime']['enabled'] == 'true':
		snips_timedate_obj = snips_timedate(logger, conf)
	return

# +----------------------------------+
# |        Intent subscriber         |
# +----------------------------------+
def intent_received(hermes, intent_message):
	global snips_airly_obj
	global snips_ambientsoundmusic_obj
	global snips_system_obj
	global snips_timedate_obj
	
	sentence = "Sorry, I can't help you with that"

	logger.debug('Received message with intent: {}'.format(intent_message.intent.intent_name))

	# ========== GetSmogLevels ==========
	if intent_message.intent.intent_name == 'vascojdb:GetSmogLevels':
		if conf['airly']['enabled'] == 'true':
			# Location defaults to home if no slots are provided:
			location = 'home'
			# Check if we have another location specified:
			location_slot = intent_message.slots.location.first()
			if location_slot is not None:
				# Update the location with the value on the slot:
				location = location_slot.value
			sentence = snips_airly_obj.saySmogLevel(location, True)
		else:
			logger.debug('Airly service is disabled.')
			
	# ========== PlayAmbientSound ==========
	if intent_message.intent.intent_name == 'vascojdb:PlayAmbientSound':
		if conf['ambientsoundmusic']['enabled'] == 'true':
			# Check if we have a type specified:
			type = None
			type_slot = intent_message.slots.sound_type.first()
			if type_slot is not None:
				type = type_slot.value
			sentence = snips_ambientsoundmusic_obj.playSounds(type)
		else:
			logger.debug('Ambient sounds service is disabled.')
			
	# ========== ListAmbientSounds ==========
	if intent_message.intent.intent_name == 'vascojdb:ListAmbientSounds':
		if conf['ambientsoundmusic']['enabled'] == 'true':
			sentence = snips_ambientsoundmusic_obj.listSounds()
			
	# ========== PlayMusic ==========
	if intent_message.intent.intent_name == 'vascojdb:PlayMusic':
		if conf['ambientsoundmusic']['enabled'] == 'true':
			# Check if we have a type specified:
			type = None
			type_slot = intent_message.slots.music_type.first()
			if type_slot is not None:
				type = type_slot.value
			sentence = snips_ambientsoundmusic_obj.playMusic(type)
		else:
			logger.debug('Ambient sounds service is disabled.')
			
	# ========== ListMusic ==========
	if intent_message.intent.intent_name == 'vascojdb:ListMusics':
		if conf['ambientsoundmusic']['enabled'] == 'true':
			sentence = snips_ambientsoundmusic_obj.listMusic()
	
	# ========== AudioOff ==========
	if intent_message.intent.intent_name == 'vascojdb:AudioOff':
		if conf['ambientsoundmusic']['enabled'] == 'true':
			sentence = snips_ambientsoundmusic_obj.stop()

	# ========== VolumeDown ==========
	if intent_message.intent.intent_name == 'vascojdb:VolumeDown':
		if conf['system']['enabled'] == 'true':
			# Check if we have a value specified:
			value = None
			value_slot = intent_message.slots.volume_lower.first()
			if value_slot is not None:
				value = value_slot.value
			sentence = snips_system_obj.volumeDown(value)

	# ========== VolumeUp ==========
	if intent_message.intent.intent_name == 'vascojdb:VolumeUp':
		if conf['system']['enabled'] == 'true':
			# Check if we have a value specified:
			value = None
			value_slot = intent_message.slots.volume_higher.first()
			if value_slot is not None:
				value = value_slot.value
			sentence = snips_system_obj.volumeUp(value)
	
	# ========== VolumeSet ==========
	if intent_message.intent.intent_name == 'vascojdb:VolumeSet':
		if conf['system']['enabled'] == 'true':
			# Check if we have a value specified:
			value = None
			value_slot = intent_message.slots.volume_level.first()
			if value_slot is not None:
				value = value_slot.value
			sentence = snips_system_obj.volumeSet(value)
	
	# ========== ScreenOn ==========
	if intent_message.intent.intent_name == 'vascojdb:ScreenOn':
		if conf['system']['enabled'] == 'true':
			sentence = snips_system_obj.screenOn()
	
	# ========== ScreenOff ==========
	if intent_message.intent.intent_name == 'vascojdb:ScreenOff':
		if conf['system']['enabled'] == 'true':
			sentence = snips_system_obj.screenOff()
			
	# ========== SystemInfo ==========
	if intent_message.intent.intent_name == 'vascojdb:SystemInfo':
		if conf['system']['enabled'] == 'true':
			sentence = snips_system_obj.systemInfo()
			
	# ========== GetDate ==========
	if intent_message.intent.intent_name == 'vascojdb:GetDate':
		if conf['datetime']['enabled'] == 'true':
			sentence = snips_timedate_obj.getDate()
			
	# ========== GetTime ==========
	if intent_message.intent.intent_name == 'vascojdb:GetTime':
		if conf['datetime']['enabled'] == 'true':
			sentence = snips_timedate_obj.getTime()
			
	hermes.publish_end_session(intent_message.session_id, sentence)


# +----------------------------------+
# |               MAIN               |
# +----------------------------------+
if __name__ == "__main__":
	logger = getLogger('DEBUG')
	logger.info('========== STARTING ==========')
	
	logger.info('Reading configuration file')
	conf = load_configuration(read_configuration_file(CONFIG_INI))

	logger.info('Initializing objects')
	initialize_objects()

	MQTT_ADDR = "{}:{}".format(conf['mqtt']['mqtt_ip_addr'], str(conf['mqtt']['mqtt_port']))
	logger.info('Connecting to MQTT at: {}'.format(MQTT_ADDR))
	logger.info('========== READY ==========')
	with Hermes(MQTT_ADDR) as h:
		h.subscribe_intents(intent_received).start()
