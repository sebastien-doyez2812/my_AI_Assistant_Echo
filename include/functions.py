import mysql.connector
import speech_recognition as sr
import re
import mysql
import pyttsx3
import speech_recognition as sr
import webbrowser
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


def process_command(command, data, answer):
    # Basic interaction:
    print(command)
    print(data["meteo"])
    if any(keyword in command for keyword in data["salutation"]):
        speak(f"Bonjour {USER}, Comment puis je vous aider aujourd'hui")
        return 
    
    if any(keyword in command for keyword in data["presentation"]):
        speak(answer["presentation"])
        return

    if  any(keyword in command for keyword in data["veille"]):
        speak(answer["veille"])
        return

    # Basic fonctionnalities:
    # What time is it?
    if any(keyword in command for keyword in data["heure"]):
        get_hour()
        return

    # What's the weather?
    if any(keyword in command for keyword in data["meteo"]):
        query = re.search(r"météo pour (.+)", command) or re.search(r"météo à (.+)", command)
        if query == None:
            get_weather()
        else:
            get_weather_at(query.group(1))
        return

    # Where are we?
    if any(keyword in command for keyword in data["localisation"]):
        city, region = get_localisation()
        speak(f"Nous sommes a {city}, {region}")
        return
    
    # Search on the web
    if any(keyword in command for keyword in data["youtube"]):
        query = re.search(r"recherche sur Youtube (.+)", command)
        if query != None:
            youtube(query.group(1))
        return

    if any(keyword in command for keyword in data["recherche rapide"]):
        print("recherche rapide")
        do_fast_research(command)
        return
    
    if any(keyword in command for keyword in data["recherche"]):
        query = re.search(r"cherche (.+)", command) 
        search(query.group(1))
        return

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
        city, _ = get_localisation()
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key_meteo}&units=metric"
        response = requests.get(url)
        data = response.json()
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
    query = re.search(r"recherche rapide sur (.+)", command) or re.search(r"Qu'est ce qu'un (.+)", command) or re.search(r"Qu'est ce qu'une (.+)", command) or re.search(r"Recherche rapidement (.+)", command)
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
                search(query.group(1))
                speak(f"Voici les résultats pour {query.group(1)}")
    else:
        #TODO: a mettre dans le json
        speak("Je n'ai pas compris votre demande")

def search(query):
    """
    Do a research and open the web browser for a query

    ARGS:
        query: string, what we want to research
    """
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    speak(f"Voici les résultats pour {query} sur Google.")

def get_weather_at(city):
    """
    Give us the weather at a specific place
    
    ARGS:
        city: string
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={read_text_from_json(PATH_PARAMETERS)["api_meteo"][0]}&units=metric"
    try: 
        response = requests.get(url)
        data = response.json()       
        if data["cod"] != "404": #error code
            weather = data["main"]
            temp = weather["temp"]
            desc = data["weather"][0]["description"]
            description = translator.translate(desc, src='en', dest='fr')
            speak(f"La température à {city} est de {temp} degrés Celsius, avec {description.text}")
        else:
            speak(f"Je n'ai pas pu trouver la météo pour {city}")
    except Exception as e:
        speak(f"Je n'ai pas pu récupérer les données météos. Erreur {str(e)}")


def youtube(request):
    """
    Research on Youtube

    ARGS:
        request: string, what we want to research on Youtube
    """
    url = f"https://www.youtube.com/results?search_query={request}"
    webbrowser.open(url)
    speak(f"Voici les résultats pour {request} sur Youtube.")
