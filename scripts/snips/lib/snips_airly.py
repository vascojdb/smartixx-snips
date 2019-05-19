#!/usr/bin/python

# +--------------------------------------------------+
# |               SNIPS AIRLY LIBRARY                |
# +--------------------------------------------------+
#
#   Description:
#     Library for obtaining information about air
#	  quality for Poland via the Airly API
#    
#   Author:
#     Vasco Baptista <vascojdb@gmail.com>
#
#

import requests
import json
import time
from opencage.geocoder import OpenCageGeocode

class snips_airly:
	def __init__(self, logger, conf):
		self.logger = logger
		self.airly_api_key = conf['airly']['airly_api_key'] if 'airly_api_key' in conf['airly'] else None
		self.airly_home_sensor_id = conf['airly']['airly_home_sensor_id'] if 'airly_home_sensor_id' in conf['airly'] else 204
		self.airly_work_sensor_id = conf['airly']['airly_work_sensor_id'] if 'airly_work_sensor_id' in conf['airly'] else 204
		self.airly_city_sensor_id = conf['airly']['airly_city_sensor_id'] if 'airly_city_sensor_id' in conf['airly'] else 204
		self.opencage_api_key = conf['airly']['opencage_api_key'] if 'opencage_api_key' in conf['airly'] else None
		self.popup_message_file = '/var/www/html/mm2/data/message.json'
		self.popup_duration = 20
		self.logger.info('Starting SNIPS Airly instance')


	def getDataFromAirly(self, station_id):
		pm25 = -1
		pm10 = -1
		level = 'unknown'
		description = ''
		advice = ''
		
		if station_id < 0:
			return (pm25, pm10, level, description, advice)
		
		# Gets the JSON from airly from a specific station:
		self.logger.debug('Requesting air quality from Airly for station {}'.format(station_id))
		try:
			headers = {'Accept' : 'application/json', 'apikey' : self.airly_api_key}
			r = requests.get('https://airapi.airly.eu/v2/measurements/installation?installationId={}'.format(station_id), headers=headers)
		except:
			self.logger.error('Requesting air quality from Airly failed...')
			return (pm25, pm10, level, description, advice)
		self.logger.debug('Air quality retrieved...')

		# Extracts the JSON data:
		airly_json = json.loads(r.text)
		if 'current' in airly_json:
			if 'indexes' in airly_json['current']:
				for entry in airly_json['current']['indexes']:
					level = entry['level'].lower().replace("_", " ")
					description = entry['description']
					advice = entry['advice']
		
			if 'standards' in airly_json['current']:
				for entry in airly_json['current']['standards']:
					if entry['pollutant'] == 'PM25':
						pm25 = int(entry['percent'])
					elif entry['pollutant'] == 'PM10':
						pm10 = int(entry['percent'])

		return (pm25, pm10, level, description, advice)


	def getStationIdFromLocation(self, location):
		location = location.lower()
		station_id = -1
		
		if 'home' in location:
			station_id = self.airly_home_sensor_id
		elif 'work' in location:
			station_id = self.airly_work_sensor_id
		elif 'city' in location:
			station_id = self.airly_city_sensor_id
		else:
			# Get coordinates based on the city name (force it to Poland):
			self.logger.debug('Requesting coordinates for location: {}'.format(location))
			geocoder = OpenCageGeocode(self.opencage_api_key)
			geocoder_results = geocoder.geocode(location + ', Poland')
			lat = str(geocoder_results[0]['geometry']['lat'])
			lng = str(geocoder_results[0]['geometry']['lng'])
			
			# Gets the JSON from airly from specific coordinates:
			self.logger.debug('Requesting station ID from coordinates lat={}, lng={}'.format(lat, lng))
			try:
				headers = {'Accept' : 'application/json', 'apikey' : self.airly_api_key}
				link = 'https://airapi.airly.eu/v2/installations/nearest?lat={}&lng={}&maxDistanceKM=5&maxResults=1'.format(lat, lng)
				x = requests.get(link, headers=headers)
				# Extracts the JSON data:
				stationid_json = json.loads(x.text)
				if 'id' in stationid_json[0]:
					station_id = stationid_json[0]['id']
					self.logger.debug('Converted location "{}" into Airly station ID: {}'.format(location, station_id))
			except:
				self.logger.error('Requesting station ID from Airly failed.')
		return station_id
	
	
	def getIconFromPercentage(self, percentage):
		icon = 'fas fa-question'
		if percentage < 80:
		  icon = 'fas fa-smile-o'
		elif percentage < 150:
		  icon = 'fas fa-meh-o' 
		else:
		  icon = 'fas fa-frown-o'
		return icon
	
	
	def createMM2Popup(self, location, pm25, pm10, level, description, advice):
		self.logger.debug('Creating JSON message for MM2 popup service')
		
		# Prepare the output JSON:
		output_json = {}
		output_json['title'] = 'Air quality'
		output_json['description'] = location
		output_json['icon'] = 'fas fa-wind'
		output_json['date'] = int(time.time())
		output_json['msg_id'] = int(time.time()*100)
		output_json['show_time'] = self.popup_duration
		output_json['contents'] = []
		
		content = {}
		content['type'] = 'table'
		content['header'] = {}
		content['header']['a_pollutant'] = 'Pollutant'
		content['header']['b_percentage'] = 'Percentage'
		content['header']['c_level'] = 'Smog level'
		content['header']['d_icon'] = ''
		content['values'] = []
		this_entry = {}
		this_entry['a_pollutant'] = 'PM2.5'
		this_entry['b_percentage'] = '{}%'.format(pm25)
		this_entry['c_level'] = level.capitalize()
		this_entry['d_icon'] = self.getIconFromPercentage(pm25)
		content['values'].append(this_entry)
		this_entry = {}
		this_entry['a_pollutant'] = 'PM10'
		this_entry['b_percentage'] = '{}%'.format(pm10)
		this_entry['c_level'] = level.capitalize()
		this_entry['d_icon'] = self.getIconFromPercentage(pm10)
		content['values'].append(this_entry)
		output_json['contents'].append(content)
		
		content = {}
		content['type'] = 'message'
		content['header'] = {}
		content['header']['a_message'] = description
		content['values'] = []
		this_entry = {}
		this_entry['a_message'] = advice
		content['values'].append(this_entry)
		output_json['contents'].append(content)
		
		generated_json = json.dumps(output_json, sort_keys=True)
		file = open(self.popup_message_file, 'w') 
		file.write(generated_json) 
		file.close()
		self.logger.debug('Saved popup message into: {}'.format(self.popup_message_file))
		

	def saySmogLevel(self, location = 'home', showPopup = True):
		if location is None:
			location = 'home'
		location = location.capitalize()
		
		(pm25, pm10, level, description, advice) = self.getDataFromAirly(self.getStationIdFromLocation(location))
		if pm25 < 0 or pm10 < 0:
			tts = 'I am sorry but an unnexpected error occured. Please try again later.'
		else:
			if showPopup:
				self.createMM2Popup(location, pm25, pm10, level, description, advice)
			# Round the values to 10ths to reduce precision and to be easier to listen to (for example 123 would be 120):
			#pm25 = int(round(pm25/10)*10)
			#pm10 = int(round(pm10/10)*10)
			# Create the answer:
			tts = 'The smog level for {} is {}. {} Currently {}% for PM2.5 and {}% for PM10. {}'.format(location, level, description, pm25, pm10, advice)
			
		self.logger.debug('Answering: {}'.format(tts))
		return tts
