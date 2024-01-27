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
import socket

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
#Want to carry forward the description so I need the list of valid descriptions from openweathermap
weatherSeriousnessDesc = ["Clear Sky","Few clouds","Scattered clouds","Broken clouds","Overcast clouds","Mist","Smoke","Haze",
    "Dust","Fog","Light drizzle","Drizzle","Heavy drizzle","Light drizzle rain","Heavy drizzle rain","Shower rain and drizzle","Heavy shower rain and drizzle",
    "Shower drizzle","Light rain","Moderate rain","Heavy rain","Very heavy rain","Extreme rain","Freezing rain","Light shower rain","Shower rain","Heavy shower rain",
    "Ragged shower rain","Thunderstorm with light rain","Thunderstorm with rain","Thunderstorm with heavy rain","Light thunderstorm","Thunderstorm","Heavy thunderstorm",
    "Ragged thunderstorm","Thunderstorm with light drizzle","Thunderstorm with drizzle","Thunderstorm with heavy drizzle","Light snow","Snow","Heavy snow","Sleet",
    "Light shower sleet","Shower sleet","Light rain and snow","Rain and snow","Light shower snow","Shower snow","Heavy shower snow","Tornado"]

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
    try: 
        response = requests.get(Url)
    except requests.ConnectionError:
        print("Connection Error")
        forecast= {"cod":404}
        return forecast
    
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
        desc = forecast["weather"][0]["description"]
    else:
        temperature = 0
        humidity = 0
        id = 781
        desc = "no report"
    return [temperature, humidity, id, desc]

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
    if seriousnesses[0] == 51:
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
        if thisSeriousness == 51:
            print(thisFor)        
        
        
        if thisDt >= midnights[thisDay]:
            thisDay += 1
        
        lowTemps[thisDay] = min(thisTemp, lowTemps[thisDay])
        highTemps[thisDay] = max(thisTemp, highTemps[thisDay])
        humidities[thisDay] = max(thisHum, humidities[thisDay])
        seriousnesses[thisDay] = max(thisSeriousness, seriousnesses[thisDay])
 
    return [lowTemps,highTemps,humidities,seriousnesses]    
 
def updateWeather():
    global tempText, humidBox, picBox, descBox
    now = datetime.now()    
    print(now.strftime("%Y-%m-%d %H:%M:%S")+" Update weather")
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
    descBox.value = weather[3]
    

    
def updateForecast():
    global todayTemps, todayPic, todayHum, dayPic, dayText, dayDOWText, todayDesc, descText
    now = datetime.now()    
    print(now.strftime("%Y-%m-%d %H:%M:%S")+" Update forecast")
    global preferred, weatherSeriousnessDesc
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
    todayTemps.value = "High "+str(round(forecast[1][0],2))+suffix+"\rLow "+str(round(forecast[0][0],2))+suffix+"\r"
    todayPic.image = "pics/"+idToFilename(weatherSeriousness[(forecast[3][0])])
    todayHum.value = str(round(forecast[2][0],2)) + "% Humidity"
    todayDesc.value = weatherSeriousnessDesc[(forecast[3][0])]
    
    today = date.today()

    for x in range(0,5):
        thisDay = today + timedelta(days=(x+1))
        dayDOWText[x].value = thisDay.strftime("%A")
        dayPic[x].image = "pics/"+idToFilename(weatherSeriousness[(forecast[3][x+1])])
        dayText[x].value = "High "+str(round(forecast[1][x+1],0))+suffix+"\rLow "+str(round(forecast[0][x+1],0))+suffix
        descText[x].value = weatherSeriousnessDesc[(forecast[3][x+1])]



def main():
    global tempText, humidBox, picBox, todayTemps, todayPic, todayHum, dayPic, dayText, dayDOWText, descBox, todayDesc, descText
    app = App(title="Weather-inator", layout="grid", width=500, height=600)

    #boxes
    tempBox = Box(app, grid=[0, 0, 5, 1], border=True, width=500, height=400)





    tempText = Text(tempBox, size=32)
    humidBox = Text(tempBox, size=32)
    picBox = Picture(tempBox)
    descBox = Text(tempBox, size=12)
    todayForecastBox = Box(tempBox, layout="grid")
    todayTemps = Text(todayForecastBox,grid=[0,0])
    todayPic = Picture(todayForecastBox, width=100, height=100, grid=[1,0])
    todayHum = Text(todayForecastBox,grid=[2,0])
    todayDesc = Text(todayForecastBox,grid=[0,3,3,1])
    dayDOWText = []
    dayBox = []
    dayPic = []
    dayText = []
    descText = []
    for x in range(0,5):
        dayBox.append(Box(app, grid=[x, 1], border=True, width=100, height=200))
        dayDOWText.append(Text(dayBox[x]))
        dayPic.append(Picture(dayBox[x], width=100, height=100))
        dayText.append(Text(dayBox[x]))
        descText.append(Text(dayBox[x], size=10))




    updateWeather()
    updateForecast()


    app.repeat((10 * 60 * 1000),updateWeather) #update every 10 minutes
    app.repeat((60*60*1000),updateForecast) #update every hour


    app.display()

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Check for internet connectivity by trying to establish a socket connection.
    :param host: Host to connect to (default is Google's public DNS server).
    :param port: Port to connect to (default is 53, the DNS service port).
    :param timeout: Connection timeout in seconds.
    :return: True if the connection is successful, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.close()
        return True
    except socket.error:
        return False

def wait_for_internet_connection(interval=5):
    """
    Wait for an internet connection, checking periodically.
    :param interval: Time in seconds between checks.
    """
    print("Checking for internet connection...")
    while not check_internet_connection():
        print("No internet connection available. Waiting...")
        time.sleep(interval)
    print("Internet connection established.")
		
	
if __name__ == '__main__':
    wait_for_internet_connection()
    main()
