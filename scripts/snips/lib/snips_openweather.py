#!/usr/bin/python

# +--------------------------------------------------+
# |            SNIPS OPENWEATHER LIBRARY             |
# +--------------------------------------------------+
#
#   Description:
#     Library for obtaining weather information from
#     openweather.org
#    
#   Author:
#     Vasco Baptista <vascojdb@gmail.com>
#
#

import requests
import json
import sys

class snips_openweather:
	def __init__(self, logger, conf):
		self.logger = logger
		self.openweather_api_key = conf['openweather']['openweather_api_key'] if 'openweather_api_key' in conf['openweather'] else None
		self.openweather_home_city = conf['openweather']['openweather_home_city'] if 'openweather_home_city' in conf['openweather'] else 204
		self.openweather_work_city = conf['openweather']['openweather_work_city'] if 'openweather_work_city' in conf['openweather'] else 204
		self.logger.info('Starting SNIPS OpenWeather instance')

	def get_weather_now_json(self, location):
		self.logger.debug('Getting today\'s weather for {}'.format(location))
		url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location, self.openweather_api_key)
		r = requests.get(url)
		self.logger.debug('Got weather from OpenWeathermap')
		return json.loads(r.text)

	def getWeatherStateString(self, json_obj):
		# Get the detailed description:
		return json_obj['weather'][0]['description']

		# Alternative way to return simpler words:
		weatherstate = { "Thunderstorm":"storms", "Rain":"raining", "Snow":"snowing", "Clouds":"cloudy" }
		main = json_obj['weather'][0]['main']
		if main in weatherstate.keys():
			return weatherstate[main]
		else:
			return main
		
	def getWeather(self, location = 'home', when = 'today'):
		if location is None:
			location = 'home'
		if location == 'home':
			location = self.openweather_home_city
		if location == 'work':
			location = self.openweather_work_city	
		if when is None:
			when = 'today'
		
		tts = 'I am sorry but an unnexpected error occured. Please try again later.'
		words_today = ['today', 'tonight', 'now', 'currently', 'this evening', 'this afternoon']
		
		if when in words_today:
			# Get weather for today:
			try:
				weather_json = self.get_weather_now_json(location.encode("utf8","ignore"))
			
				location_name = weather_json['name']
				temperature_curr = int(round(weather_json['main']['temp']))
				temperature_max = int(round(weather_json['main']['temp_max']))
				temperature_min = int(round(weather_json['main']['temp_min']))
				pressure = int(round(weather_json['main']['pressure']))
				humidity = int(round(weather_json['main']['humidity']))
				weather_state_str = self.getWeatherStateString(weather_json)
			except:
				self.logger.error('An error occured: {}'.format(sys.exc_info()[0]))
				return tts
			tts = 'Currently in {} it is {} degrees and {}, with a high of {} and a low of {}.'.format(location_name, temperature_curr, weather_state_str, temperature_max, temperature_min)
		else:
			tts = 'I am sorry but I am unable to tell you that weather forecast.'

		self.logger.debug('Answering: {}'.format(tts))
		return tts
