# Speech Recognition Assistant (Python)
A voice assistant created with Python 3.

## Project Overview
Takes in a data set of input, to automate a response, given a speech input.
A speech recognition application built in Python that converts speech to text and vice-versa for daily-use by building a response from user input.

* Incorporated a phrase detection algorithm and geocoder library to display a specific output for the user.
* Implemented Google Calendar API for date and event retrieval and OpenWeatherMap API for current weather
updates.
* Learned about user authentication and security from implementation of API keys as well as data retrieval from
a json response.

## Setting Up Virtual Environment 
We can setup the virtual environment using venv, and the requirements.txt file.
```sh
$ python3 -m venv voice-env
$ source voice-env/bin/activate
$ pip install -r requirements.txt
$ python main.py
```

## API Key Implementation
Currently using API keys from Google Calendar API and OpenWeatherMap API.
In order to use this implementation, you must change the api_file directory, and use another API key inside a text file accordingly.





