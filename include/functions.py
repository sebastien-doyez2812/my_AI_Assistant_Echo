import mysql.connector
import speech_recognition as sr
import re
import mysql
import pyttsx3
import speech_recognition as sr
from datetime import datetime
import json
import requests
import wikipediaapi
from googletrans import Translator
from include.header import *


####################################
##      STANDARD FUNCTIONS        ##
####################################         

# Definition of the vocal engine of Jarvis:
engine = pyttsx3.init()
engine.setProperty('volume', 1.5)
engine.setProperty('rate', 200)

# To translate in French:
translator = Translator()
# Fast research:
user_agent_wikipedia = "JarvisPython/1.0 (https://github.com/sebastien-doyez2812/AI-projects/AI_ChatBot)"
wiki = wikipediaapi.Wikipedia(user_agent_wikipedia, 'fr')

def speak(sentence):
    """
    speak: make JARVIS say the sentence

    params:
        sentence: string
    """
    engine.say(sentence)
    engine.runAndWait()

def listen():
    """
    return what the speech recognition had heard.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    # To avoid the exception UnknowVeluError, we use a try except
    try:
        command = recognizer.recognize_google(audio, language="fr-FR")
        return command
    except sr.UnknownValueError:
        return None


def read_text_from_json(path):
    """
    Extract the data from a JSON file and return it.

    ARGS:
        path = Path where the JSON file is stored.
    """
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
"""
# For the Database:
jarvis_database = mysql.connector.connect(
    host="LocalHost",
    user="root",
    password="",
    database="jarvis_db"
)
jarvis_cursor = jarvis_database.cursor()
"""

# Basics fonctionnalities:
def get_hour():
    """
    Speak to say the time

    ARGS:
        None.
    """
    try:
        now = datetime.now()
        print(now)
        current_time = now.strftime("%H:%M")
        print(current_time)
        speak(f"Il est {current_time}")
    except Exception as e:
        print(f"get_hour error: {e}")


def get_localisation():
    """
    return the city and the region where we are.
    Usefull for getting the weather.

    ARGS:
        None.
    """
    try:
        response = requests.get("https://ipinfo.io")
        print(response)
        data = response.json()
        city = data["city"]
        region = data["region"]
        return(city, region)
    except Exception as e:
        print(f"get_localisation error: {e}")


def get_weather():
    """
    Speak to say the actual weather

    ARGS:
        none
    """
    try:
        api_key_meteo = read_text_from_json(PATH_PARAMETERS)["api_meteo"][0]
        print(api_key_meteo)
        city, _ = get_localisation()
        print(city)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key_meteo}&units=metric"
        response = requests.get(url)
        data = response.json()
        print(data)
        if data["cod"] != "404":

            # Get the data:
            weather = data["main"]
            temp = weather["temp"]
            real_temp = weather["feels_like"]
            desc = data["weather"][0]["description"]
            
            # To translate:
            description_trans= translator.translate(desc, src='en', dest='fr')
            speak(f"Aujourd'hui, à {city}, il fait {temp} degrées, mais le ressenti est de{real_temp} degrées. Le climat est {description_trans.text}")
    except Exception as e:
        print (f"get_weather error: {e}")

def do_fast_research(command):
    """
    Do a fast research on wikipedia, 
    
    ARGS: 
        the command( what JARVIS heard)
    """
    query = re.search(r"recherche rapide sur (.+)", command) or re.search(r"Qu'est ce qu'un (.+)", command) or re.search(r"Qu'est ce qu'une (.+)", command) or re.search(r"Reherche rapidement (.+)", command)
    print(query)
    if query != None:
        page = wiki.page(query.group(1))
        print(f"{query.group(1)}")
        if page.exists():
            speak(read_text_from_json(PATH_ANSWER_JSON)["recherche rapide"]["success"][0])
            speak(f"{page.summary[:]}")
        else:
            speak(read_text_from_json(PATH_ANSWER_JSON)["recherche rapide"]["failure"][0])
            command = listen()

            if "oui" in command:
                print("oui")
                #TODO
    else:
        #TODO: a mettre dans le json
        speak("Je n'ai pas compris votre demande")