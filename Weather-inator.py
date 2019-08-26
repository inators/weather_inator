#!/usr/bin/python3
import requests, json
from guizero import App,Box,Picture,Text
from pathlib import Path

home = str(Path.home())

f = open(home+"/apiKey.txt","r")
if f.mode == "r":  # file opened
	apiKey = f.read()
else:
	apiKey = ""
	

apiKey = apiKey.strip()
cityName = "Nephi"
baseUrl = "http://api.openweathermap.org/data/2.5/"
weatherUrl = baseUrl + "weather?appid=" + apiKey + "&q=" + cityName
forecastUrl = baseUrl + "forecast?appid=" + apiKey + "&q=" + cityName

preferred = "Fahrenheit"



def descToFilename(desc):
	switcher = {
		"clear sky":"day_clear.png",
		"few clouds":"day_partial_cloud.png",
		"scattered clouds":"cloudy",
		"broken clouds":"angry_clouds.png",
		"shower rain":"day_rain.png",
		"rain":"rain.png",
		"thunderstorm":"thunder.png",
		"snow":"snow.png",
		"mist":"mist.png"
	}
	return switcher.get(desc,"tornado.png")
	


def getForecast(Url):
	response = requests.get(Url)
	forecast = response.json()
	return forecast

# openweather uses kelvin	
def kelvinToFahrenheit(temperature):
	fahrenheit = (temperature - 273.15) * 9 / 5 + 32
	return fahrenheit
	
# openweather uses kelvin
def kelvinToCelcius(temperature):
	celcius = temperature - 273.15
	return celcius
	
def getCurrentForecast():
	global weatherUrl
	forecast = getForecast(weatherUrl)
	#make sure we got some data
	if forecast["cod"] == 200:
		temperature = forecast["main"]["temp"]
		humidity = forecast["main"]["humidity"]
		desc = forecast["weather"][0]["description"]
	else:
		temperature = 0
		humidity = 0
		desc = "None"
	print("Temperature:",temperature,"Hum:",humidity,"Desc:"+desc)
	return [temperature,humidity,desc]

app = App(title="Weather-inator" )

tempBox = Text(app, size=32)
humidBox = Text(app, size=32)
picBox = Picture(app)
	


def updateWeather():
	global preferred
	weather = getCurrentForecast()

	if preferred == "Fahrenheit":
		ourTemp = kelvinToFahrenheit(weather[0])
	else:
		ourTemp = kelvinToCelcius(weather[0])
		
	tempBox.value = round(ourTemp,2)
	humidBox.value = str(round(weather[1],2)) + "%"
	picBox.image="pics/"+descToFilename(weather[2])

updateWeather()

app.repeat((10*60*1000),updateWeather) #update every 10 minutes


app.display()

		
	
