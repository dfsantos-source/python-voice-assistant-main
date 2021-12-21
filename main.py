from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import speech_recognition as sr
import pyttsx3
import pytz
import random
from random import choice
import requests
import json
import geocoder

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
DAY_PRONOUNCE = [
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "nineth", "tenth", "eleventh", "twelveth", "thirtheenth", 
    "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", 
    "nineteenth", "twentyth", "twentyfirst", "twentysecond", "twentythird",
    "twentyfourth", "twentyfifth", "twentysixth", "twentyseventh", "twentyeigth", "twentynineth", "thirtyth", "thirtyfirst"
]
DAY_ABREVS = [
    'mon',
    'tue',
    'wed',
    'thu',
    'fri',
    'sat',
    'sun',
]
DAYS_OF_WEEK = [
    "monday", 
    "tuesday", 
    "wednesday", 
    "thursday", 
    "friday", 
    "saturday", 
    "sunday",
]
MONTHS = [
    "january", 
    "february", 
    "march", 
    "april", 
    "may", 
    "june",
    "july", 
    "august", 
    "september",
    "october", 
    "november", 
    "december"
]
GREETING_STRS_1 = [
    "hello",
    "hi",
    "hey",
    "greetings",
    "what's good",
]
GREETING_STRS_2 = [
    "how are you",
    "how are things",
]   
GREETING_STRS_2_ANSWERS = [
    "just getting by",
    "i'm alright",
    "i'm okay",
]
EVENT_STRS_1 = [
    "upcoming events",
    "what are my upcoming events",
    "when are my upcoming events",
    "show my upcoming events",
]
DATE_STRS_1 = [
    "what is today's date",
    "give me today's date",
    "what's the date today",
    "what is the date today",
    "what's today's date",
    "what is the date today",
]
DATE_STRS_2 = [
    "what day of the week",
    "what day is",
]
EVENT_STRS_3 = [
    "what is on",
    "anything on",
    "plans on",
    "events on",
    "event on",
    "event tomorrow",
    "events tomorrow",
    "events today",
    "event today"
]
NAME_STRS_1 = [
    "what is your name",
    "what's your name",
    "give me your name",
]
WEATHER_STRS_1 = [
    "weather today",
    "weather tomorrow",
    "weather forecast tomorrow",
    "weather forecast today",
    "weather on",
]

# use pytts library for output 
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# using google speech recognition and python speech recognition
# microphone speech converts to text
def get_audio():
    print("Begin speaking..")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source=source,timeout=5,phrase_time_limit=5)
        try:
            print(r.recognize_google(audio))
        except Exception:
            print("EXCEPTION FOUND")
     
    return r.recognize_google(audio)

# starter template quickstart code for Google Calendar API docs
# authenticates and prepares API for calling
def authenticate_google():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

# RETURNS NEXT 10 UPCOMING EVENTS FROM CALENDAR API
def get_events(service):  
    # API parameter requires UTC format 
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    print("-------------")
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return None
    else:
        return events

# RETURNS EVENT FROM A SPECIFIED DATE
def get_event(date, service):
    # handling for date, morning->midnight bound handling
    start = datetime.datetime.combine(date, datetime.datetime.min.time())
    start = start.astimezone(pytz.UTC).isoformat()
    end = datetime.datetime.combine(date, datetime.datetime.max.time())
    end = end.astimezone(pytz.UTC).isoformat()  
    
    events_result = service.events().list(calendarId='primary', timeMin=start, timeMax=end,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        return None
    else:
        return events


# RETURNS DATETIME OBJECT FROM VOICE (TEXT)
def get_date(text):
    today = datetime.date.today()
    day = -1
    month = -1
    year = today.year

    if text.count("tomorrow") > 0:
        return today + datetime.timedelta(1) # add a day to datetime

    if text.count("today") > 0:
        return today    
    

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1 # get month in word form ex: Nov
        elif word[0:2].isdigit() and not word.isdigit(): #if day and not year
            day = int(word[0:2]) # get day in int form ex: 22

    if month < today.month:
        year += 1
    
    return datetime.date(month=month, day=day, year=year)


# RETURNS MONTH AND DAY FOR VOICE OUTPUT
# ex: 
# input: "08-21"
# output: "March twenty-first"
def date_to_string(date): #format ex: 08-21
    day = DAY_PRONOUNCE[int(date[3:5])-1] 
    int_month = int(date[0:2]) 
    return MONTHS[int_month-1] + " " + day

def date_to_string_year(date): #format ex: 2000-08-21
    day = DAY_PRONOUNCE[int(date[8:10])-1] 
    int_month = int(date[5:7])-1 
    return f"{MONTHS[int_month]} {day} {date[0:4]}"


# RETURNS STRING WITH HIGH TEMP, LOW TEMP, FORECAST FOR A SPECIFIC DATE
# uses geocoder to pinpoint location, used to find lat and long for API call
# date must be within 7 days of day 
def get_weather(day_value):
    myloc = geocoder.ip('me') # get current location based off ip address
    lat = myloc.lat
    lon = myloc.lng
    part = 'hourly, minutely, current'
    api_file = open("/Users/danesantos/Desktop/api_keys/weather_key.txt" , "r")
    api_key = api_file.read()
    api_file.close()
    base_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units=imperial&exclude={part}&appid={api_key}"
    response = requests.get(base_url)
    rough_data = response.json()
    weather_forecast = rough_data["daily"]
    i = 0
    result = ""

    for elem in weather_forecast:
        if (i == day_value):
            highTemp = elem["temp"]["max"]
            lowTemp = elem["temp"]["min"]
            highTemp = int(f"{highTemp}"[0:2])
            lowTemp = int(f"{lowTemp}"[0:2])
            weather = elem["weather"]
            x = weather[0]
            weather = x["description"]
            result += f"High temp of: {highTemp} degrees, Low temp of: {lowTemp} degrees, Forecast is: {weather}"
        i += 1

    return result


#----------------------------------------------------------------------------------------------------------------

# WAIT FOR USER INPUT
# input("Press Enter then begin speaking..")

# INITIALIZE VARIABLES
service = authenticate_google()
text = get_audio().lower()
text_tokens = text.split()
print('You said: ' + text)
output = ""
phraseFound = False

# RETURN 'HELLO'
for greeting in GREETING_STRS_1:
    if greeting in text_tokens:
        phraseFound = True
        output += ' ' + random.choice(GREETING_STRS_1) + '.'
        break

# RETURN 'HOW ARE YOU'
for greeting in GREETING_STRS_2:
    if greeting in text:
        phraseFound = True
        output += ' ' + random.choice(GREETING_STRS_2_ANSWERS) + '.'
        break

# RETURN ALL EVENTS (SUMMARY , DATE)
for phrase in EVENT_STRS_1:
    if phrase in text:
        phraseFound = True
        events = get_events(service)
        output += ' ' + "you have"
        if events is not None:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                output += ' ' + event['summary'] + ' ' + "on" + ' ' + date_to_string(start[5:10]) + ','
            break
        else:
            output += "No upcoming events"

# RETURN DATE TODAY (MONTH, DAY, YEAR)
for phrase in DATE_STRS_1:
    if phrase in text:
        phraseFound = True
        date = datetime.date.today()
        today = f"{date}"
        output += '' + "today's date is, " + date_to_string_year(today) + ','
        break

# RETURN NAME
for phrase in NAME_STRS_1:
    if phrase in text:
        phraseFound = True
        output += ' ' + "My name is Neo."
        break

# RETURN EVENT FOR A SPECIFIC DATE
# must be said in the form ex: 'on august 21th'
for phrase in EVENT_STRS_3:
    if phrase in text:
        phraseFound = True
        dateInstance = get_date(text)
        events = get_event(dateInstance, service)
        if events is not None:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                output += ' ' + event['summary'] + ' ' + "on" + ' ' + date_to_string(start[5:10]) + ','
            break
        else:
            output += " no events on that date."
            break

# RETURNS WEATHER FOR A SPECIFIC DATE
for phrase in WEATHER_STRS_1:
    if phrase in text:
        phraseFound = True
        today = datetime.datetime.today()
        today = datetime.datetime.combine(today, datetime.datetime.min.time())
        dateInstance = get_date(text) 
        dateInstance = datetime.datetime.combine(dateInstance, datetime.datetime.min.time())

        if not (today + datetime.timedelta(7) >= dateInstance):      
            output += " the date must be within 7 days of today."
        else:
            # get weather date # in terms of 7 day forecast
            diff = dateInstance - today
            result = f"{diff}"
            result = result[:1]
            x = int(result)
            output += get_weather(x)
        
        break


# SPEAK OUTPUT
if phraseFound == True:
    print("Output String: " + output)
    speak(output)
else:
    print("No phrase found.")
    speak("No phrase found.")