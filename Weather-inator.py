#!/usr/bin/python3
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from guizero import App
from guizero import Box
from guizero import Picture
from guizero import Text
import json
from pathlib import Path
from pprint import pprint
import requests

home = str(Path.home())

# don't exactly want to publish my apiKey on github
f = open(home + "/apiKey.txt", "r")
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

#Need some way to pic the most serious picture for a day
weatherSeriousness = [800,801,802,803,804,701,711,721,731,741,300,301,302,310,311,312,313,314,321,500,501,502,503,504,511,
    520,521,522,531,200,201,202,210,211,212,221,230,231,232,600,601,602,611,612,613,615,616,620,621,622,781]

def idToFilename(id):
    switcher = {
        800:"day_clear.png",
        801:"day_partial_cloud.png",
        802:"day_partial_cloud.png",
        803:"cloudy.png",
        804:"overcast.png",
        701:"mist.png",
        711:"mist.png",
        721:"fog.png",
        731:"fog.png",
        741:"fog.png",
        300:"angry_clouds.png",
        301:"day_rain.png",
        302:"day_rain.png",
        310:"day_rain.png",
        311:"rain.png",
        312:"rain.png",
        313:"rain.png",
        314:"rain.png",
        321:"rain.png",
        500:"day_rain.png",
        501:"day_rain.png",
        502:"rain.png",
        503:"rain.png",
        504:"rain.png",
        511:"sleet.png",
        520:"day_rain.png",
        521:"day_rain.png",
        522:"rain.png",
        531:"rain.png",
        200:"angry_clouds.png",
        201:"day_rain_thunder.png",
        202:"rain_thunder.png",
        210:"angry_clouds.png",
        211:"thunder.png",
        212:"thunder.png",
        221:"thunder.png",
        230:"day_rain_thunder.png",
        231:"rain_thunder.png",
        232:"rain_thunder.png",
        600:"day_snow.png",
        601:"snow.png",
        602:"snow.png",
        611:"day_sleet.png",
        612:"day_sleet.png",
        613:"sleet.png",
        615:"day_sleet.png",
        616:"sleet.png",
        620:"day_snow.png",
        621:"snow.png",
        622:"snow.png",
        781:"tornado.png"
    }
    return switcher.get(id,"tornado.png")
    


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
        id = forecast["weather"][0]["id"]
    else:
        temperature = 0
        humidity = 0
        id = 781
    return [temperature, humidity, id]

def getCurrentForecast():
    global forecastUrl
    forecast = getForecast(forecastUrl)
    #make sure we got some data
    if forecast["cod"] != "200":
        return False
    timezone = forecast["city"]["timezone"]

    midnightTonight = datetime.combine(datetime.today(), time.min) + timedelta(days=1)
    # set up some variables to figure out our forecast
    midnights = [midnightTonight, midnightTonight + timedelta(days=1), midnightTonight + timedelta(days=2),
        midnightTonight + timedelta(days=3), midnightTonight + timedelta(days=4), midnightTonight + timedelta(days=5)]
    lowTemps = [400, 400, 400, 400, 400, 400, 400]
    highTemps = [0, 0, 0, 0, 0, 0, 0]
    humidities = [0, 0, 0, 0, 0, 0, 0]
    seriousnesses = [0, 0, 0, 0, 0, 0, 0]
    weatherNow = getCurrentWeather()
    lowTemps[0] = highTemps[0] = weatherNow[0]
    humidities[0] = weatherNow[1]
    seriousnesses[0] = weatherSeriousness.index(weatherNow[2])
    #Tornado is the default.  If we get it print the message so we can assign it later
    if seriousnesses[0] == 11:
        print(weatherNow[2])
    
    thisDay = 0
    
    #need to iterate through this and figure out the min / max temperature per day
    for f in forecast['list']:
        thisDt = datetime.fromtimestamp(f['dt'])
        thisTemp = f['main']['temp']
        thisHum = f['main']['humidity']
        thisFor = (f['weather'][0]['id'])
        thisSeriousness = weatherSeriousness.index(thisFor)
        #Tornado is the default.  If we get it print the message so we can assign it later
        if thisSeriousness == 11:
            print(thisFor)        
        
        
        if thisDt >= midnights[thisDay]:
            thisDay += 1
        
        lowTemps[thisDay] = min(thisTemp, lowTemps[thisDay])
        highTemps[thisDay] = max(thisTemp, highTemps[thisDay])
        humidities[thisDay] = max(thisHum, humidities[thisDay])
        seriousnesses[thisDay] = max(thisSeriousness, seriousnesses[thisDay])
 
    return [lowTemps,highTemps,humidities,seriousnesses]    
 
def updateWeather():
    global tempText, humidBox, picBox
    print("Update weather")
    global preferred
    weather = getCurrentWeather()

    if preferred == "Fahrenheit":
        ourTemp = kelvinToFahrenheit(weather[0])
        ourTemp = str(round(ourTemp, 2)) + u"\u00b0F"
    else:
        ourTemp = kelvinToCelcius(weather[0])
        ourTemp = str(round(ourTemp, 2)) + u"\u00b0C"

    tempText.value = "Temperature: " + ourTemp
    humidBox.value = "Humidity: " + str(round(weather[1], 2)) + "%"
    picBox.image = "pics/" + idToFilename(weather[2])
    

    
def updateForecast():
    global todayTemps, todayPic, todayHum, dayPic, dayText
    print("Update forecast")
    global preferred
    forecast = getCurrentForecast()
    if forecast == False:
        return
    if preferred == "Fahrenheit":
        suffix = u"\u00b0F"
        for x in range(0,6):
            forecast[0][x] = kelvinToFahrenheit(forecast[0][x])
            forecast[1][x] = kelvinToFahrenheit(forecast[1][x])
    else:
        suffix = u"\u00b0C"
        for x in range(0,6):
            forecast[0][x] = kelvinToCelcius(forecast[0][x])
            forecast[1][x] = kelvinToCelcius(forecast[1][x])
    todayTemps.value = "Low "+str(round(forecast[0][0],2))+suffix+"\r"+"High "+str(round(forecast[1][0],2))+suffix
    todayPic.image = "pics/"+idToFilename(weatherSeriousness[(forecast[3][0])])
    todayHum.value = str(round(forecast[2][0],2)) + "%"

    for x in range(0,5):
        dayPic[x].image = "pics/"+idToFilename(weatherSeriousness[(forecast[3][x+1])])
        dayText[x].value = "Low "+str(round(forecast[0][x+1],0))+suffix+"\rHigh "+str(round(forecast[1][x+1],0))+suffix



def main():
    global tempText, humidBox, picBox, todayTemps, todayPic, todayHum, dayPic, dayText
    app = App(title="Weather-inator", layout="grid")

    #boxes
    tempBox = Box(app, grid=[0, 0, 5, 1], border=True, width=500, height=350)





    tempText = Text(tempBox, size=32)
    humidBox = Text(tempBox, size=32)
    picBox = Picture(tempBox)
    todayForecastBox = Box(tempBox, layout="grid")
    todayTemps = Text(todayForecastBox,grid=[0,0])
    todayPic = Picture(todayForecastBox, width=100, height=100, grid=[1,0])
    todayHum = Text(todayForecastBox,grid=[2,0])
    dayBox = []
    dayPic = []
    dayText = []
    for x in range(0,5):
        dayBox.append(Box(app, grid=[x, 1], border=True, width=100, height=150))
        dayPic.append(Picture(dayBox[x], width=100, height=100))
        dayText.append(Text(dayBox[x]))




    updateWeather()
    updateForecast()


    app.repeat((10 * 60 * 1000),updateWeather) #update every 10 minutes
    app.repeat((60*60*1000),updateForecast) #update every hour


    app.display()

		
	
if __name__ == '__main__':
    main()