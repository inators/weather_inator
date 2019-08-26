#!/usr/bin/python3
import requests, json
from guizero import App,Box,Picture,Text
from pathlib import Path
from pprint import pprint
from datetime import datetime, date, time, timedelta

home = str(Path.home())

# don't exactly want to publish my apiKey on github
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
	
def getCurrentWeather():
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

def getCurrentForecast():
    global forecastUrl
    forecast = getForecast(forecastUrl)
    #make sure we got some data
    if forecast["cod"] == "200":
        print("hi")
        #pprint.pprint(forecast)
    else:
        return false
    timezone = forecast["city"]["timezone"]
    print(forecast['list'][0])
    forecastList = []
    #need to iterate through this and figure out the min / max temperature per day
    for f in forecast['list']:
        thisDt = datetime.fromtimestamp(f['dt'])
        thisTemp = f['main']['temp']
        thisHum = f['main']['humidity']
        thisFor = (f['weather'][0]['description'])
        forecastList.append([thisDt,thisTemp,thisHum,thisFor])
        
    pprint(forecastList)
    midnight = datetime.combine(datetime.today(), time.min) + timedelta(days=1)
    print(midnight)
        
    
    
    

app = App(title="Weather-inator", layout="grid" )

#boxes
tempBox = Box(app, grid=[0,0,5,1], border=True, width=500, height=250)
day1Box = Box(app, grid=[0,1], border=True, width=100, height=250)
day2Box = Box(app, grid=[1,1], border=True, width=100, height=250)
day3Box = Box(app, grid=[2,1], border=True, width=100, height=250)
day4Box = Box(app, grid=[3,1], border=True, width=100, height=250)
day5Box = Box(app, grid=[4,1], border=True, width=100, height=250)




tempText = Text(tempBox, size=32)
humidBox = Text(tempBox, size=32)
picBox = Picture(tempBox)
day1pic = Picture(day1Box, width=100, height=100)	
day2pic = Picture(day2Box, width=100, height=100)	
day3pic = Picture(day3Box, width=100, height=100)	
day4pic = Picture(day4Box, width=100, height=100)	
day5pic = Picture(day5Box, width=100, height=100)
day1Text = Text(day1Box)
day2Text = Text(day2Box)
day3Text = Text(day3Box)
day4Text = Text(day4Box)
day5Text = Text(day5Box)


def updateWeather():
    global preferred
    weather = getCurrentWeather()

    if preferred == "Fahrenheit":
            ourTemp = kelvinToFahrenheit(weather[0])
            ourTemp = str(round(ourTemp,2)) +u"\u00b0F"
    else:
            ourTemp = kelvinToCelcius(weather[0])
            ourTemp = str(round(ourTemp,2)) +u"\u00b0C"

    tempText.value = "Temperature: " +ourTemp
    humidBox.value = "Humidity: " + str(round(weather[1],2)) + "%"
    picBox.image="pics/"+descToFilename(weather[2])

def updateForecast():
    global preferred
    forecast = getCurrentForecast()

updateWeather()
updateForecast()


app.repeat((10*60*1000),updateWeather) #update every 10 minutes
app.repeat((60*60*1000),updateForecast) #update every hour


app.display()

		
	
