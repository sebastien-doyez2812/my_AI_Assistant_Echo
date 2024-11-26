import mysql.connector
import speech_recognition as sr
import re
import mysql
import random
import pyttsx3
import speech_recognition as sr
import webbrowser
import webbrowser
from datetime import datetime
import json
import requests
import wikipediaapi
from datetime import datetime
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

# For the Database:
jarvis_database = mysql.connector.connect(
    host="LocalHost",
    user="root",
    password="",
    database="jarvis_db"
)
jarvis_cursor = jarvis_database.cursor()

def process_command(command, data, answer, id_user):
    """
    DEFS:
    ------
    List of fonctionnalities:
    _ historique
    _ salutation
    _ presentation
    _ veille
    _ Heure
    _ météo
    _ localisation
    _ youtube
    _ recherche
    _ recherche rapide
    _ musique
    _ evenement ( event of the day + add a event )
    
    fonctionnalities with AI:
    _ check the clothes and check the weather
    ARGS:
    -----
    command: string, what JARVIS heard.
    data, answer: data from JSON
    id_user: for now, not really usefull

    """

    sentence = ""
    # Basic interaction:
    add_request(command, id_user)

    if any(keyword in command for keyword in data["historique"]):
        word_to_find = None
        # contenant le mot ___ ou contenant ____
        try_to_find1 = re.search("contenant le mot (.+)", command)
        if try_to_find1 != None:
            word_to_find = try_to_find1.group(1)
        else:
            try_to_find2 = re.search("contenant (.+)", command)
            if try_to_find2 != None:
                word_to_find = try_to_find2.group(1)
        
        if word_to_find != None:
            
            print(f"on doit trouver: {word_to_find}")
            day, hour, minute = find_when(word_to_find)
            speak(read_text_from_json(PATH_ANSWER_JSON)["history"]["success"])
            for i in range(len(day)):
                sentence = f" le {day}, a {hour} heure et {minute} minutes."
                #TODO delete 
                #speak(sentence)
        else: 
            print("find_word ERROR: unable to understand the word")
        return sentence
    
    if any(keyword in command for keyword in data["salutation"]):
        sentence = f"Bonjour {USER}, Comment puis je vous aider aujourd'hui"
        #TODO: to delete
        #speak(sentence)
        return sentence
    
    if any(keyword in command for keyword in data["presentation"]):
        # TODO: to delete
        #speak(answer["presentation"])
        return answer["presentation"][0]

    if  any(keyword in command for keyword in data["veille"]):
        #TODO to delete
        #speak(answer["veille"])
        #TODO: faire un mode veille
        return answer["veille"][0]

    # Basic fonctionnalities:
    # What time is it?
    if any(keyword in command for keyword in data["heure"]):
        sentence = get_hour()
        #TODO: to delete
        #speak(sentence)
        return sentence

    # What's the weather?
    if any(keyword in command for keyword in data["meteo"]):
        query = re.search(r"météo pour (.+)", command) or re.search(r"météo à (.+)", command)
        if query == None:
            sentence = get_weather()
        else:
            print(query)
            sentence = get_weather_at(query.group(1))
        
        # TODO: to delete
        #speak(sentence)
        return sentence

    # Where are we?
    if any(keyword in command for keyword in data["localisation"]):
        city, region = get_localisation()
        sentence = f"Nous sommes a {city}, {region}"
        
        # TODO: to delete
        #speak(sentence)
        return sentence
    
    # Search on the web
    if any(keyword in command for keyword in data["youtube"]):
        query = re.search(r"recherche sur Youtube (.+)", command)
        if query != None:
            youtube(query.group(1))
        return "Ouverture de Youtube"

    if any(keyword in command for keyword in data["recherche rapide"]):
        print("recherche rapide")
        sentence = do_fast_research(command)
        return sentence 
    
    if any(keyword in command for keyword in data["recherche"]):
        query = re.search(r"cherche (.+)", command) 
        search(query.group(1))
        return sentence
    
    # Functions with the database:
    if any(keyword in command for keyword in data["musique"]):
        play_music()
        return "Lancement d'une de vos musiques favorites."
    if any(keyword in command for keyword in data["event"]):
        if "ajoute" in command:
            add_event()
            return "événement ajouté"
        if "ai-je" in command:
            # TODO: a améliorer dans le futur:
            # mettre dans le json
            if "aujourd'hui" in command:
                today = datetime.now()
                get_event("day", today.strftime("%d") , today.strftime("%m"))
                return
            if "description" in command:
                speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["name"])
                name = listen()
                get_event("name", name)
                return


    #######################################
    ##       AI Functionnalities         ##
    #######################################

    if any(keyword in command for keyword in data["AI"]["weather"]):
        get_weather()

    

    

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




# Basics fonctionnalities:
def get_hour():
    """
    Speak to say the time

    ARGS:
        None.
    """
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        return f"Il est {current_time}"
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
            sentence = f"Aujourd'hui, à {city}, il fait {temp} degrées, mais le ressenti est de{real_temp} degrées. Le climat est {description_trans.text}"
            return sentence
    except Exception as e:
        print (f"get_weather error: {e}")

def do_fast_research(command):
    """
    Do a fast research on wikipedia, 
    
    ARGS: 
        the command( what JARVIS heard)
    """
    sentence = ""
    query = re.search(r"recherche rapide sur (.+)", command) or re.search(r"Qu'est ce qu'un (.+)", command) or re.search(r"Qu'est ce qu'une (.+)", command) or re.search(r"Recherche rapidement (.+)", command)
    if query != None:
        page = wiki.page(query.group(1))
        if page.exists():
            speak(read_text_from_json(PATH_ANSWER_JSON)["recherche rapide"]["success"][0])
            sentence = (f"{page.summary[0:1000]}")
        else:
            speak(read_text_from_json(PATH_ANSWER_JSON)["recherche rapide"]["failure"][0])
            command = listen()

            if "oui" in command:
                search(query.group(1))
                sentence = f"Voici les résultats pour {query.group(1)}"
    else:
        sentence = read_text_from_json(PATH_ANSWER_JSON)["failure"]
    return sentence

def search(query):
    """
    Do a research and open the web browser for a query

    ARGS:
        query: string, what we want to research
    """
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    sentence = f"Voici les résultats pour {query} sur Google."
    return sentence


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
            sentence = f"La température à {city} est de {temp} degrés Celsius, avec {description.text}"
        else:
            sentence = f"Je n'ai pas pu trouver la météo pour {city}"
            return sentence
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

################################################
# Functions with the use of the database       #
################################################

# Play musics:
def play_music():
    try:
        index = random.randint(0,10)
        jarvis_cursor.execute(f"SELECT link FROM musique WHERE id = {index}")
        url = jarvis_cursor.fetchall()[0][0]
        webbrowser.open(url)
    except Exception as e:
        print (f"play_music ERROR: {e}")

def find_phone(name):
    """
    Give the phone number of somebody in the database

    ARGS:
        name = string, ={papy, papa}
    """
    try:
        jarvis_cursor.execute(f"SELECT phone FROM `repertoire` WHERE name = '{name}'")
        phone_number = jarvis_cursor.fetchall()[0]
        return(phone_number)
    except Exception as e:
        print(f"find_phone ERROR: {e}")


def find_email(name):
    """
    Give the email of somebody in the database

    ARGS:
        name = string, ={papy, papa}
    """
    try:
        jarvis_cursor.execute(f"SELECT email FROM `repertoire` WHERE name = '{name}'")
        phone_number = jarvis_cursor.fetchall()[0]
        return(phone_number)
    except Exception as e:
        print(f"find_email ERROR: {e}")

def add_request(command, id_user):
    """
    Save all the requests for the different user

    ARGS:
        command: string, what the user said
        id_user: int
    """
    try:
        now = datetime.now()
        day = now.strftime("%h:%m")
        hour   = int(now.strftime("%H"))
        minute = int(now.strftime("%M"))
        command = command.replace("'","")
        jarvis_cursor.execute(f"INSERT INTO requests (day, hour, minute, id_user, command) VALUES ('{day}', '{hour}', '{minute}', '{int(id_user)}', '{command}')")
    except Exception as e:
        print(f"add_request ERROR: {e}")

def remove_from_request_history():
    """
    TO IMPROVE:
    delete all the request the 30th of the month

    ARGS: None.
    """
    try:
        if int(datetime.now().strftime("%m")) == 30:
            jarvis_cursor.execute("DELETE FROM 'request")
    except Exception as e:
        print(f"remove_from_request ERROR: {e}")

#TODO: trouver quand une request contenant keyword a été faite:
def find_when(keyword):
    """
    DEFS:
    -----
    find when the request with the keyword inside was prononce.

    ARGS:
    -----
        keyword: string, word inside a request we want to find
    """
    try:
        keyword = "%"+keyword+"%"
        sql_request = f"SELECT day, hour, minute FROM requests WHERE command LIKE '{keyword}'"
        jarvis_cursor.execute(sql_request)
        day, hour, minute = []
        day.append(jarvis_cursor.fetchall()[0][0])
        hour.append(jarvis_cursor.fetchall()[1])
        minute.append(jarvis_cursor.fetchall()[2])
        return (day, hour, minute)
    except Exception as e:
        print(f"find_when ERROR: {e}")

def add_event():
    """
    DEF:
    -----
    Help the user to define the event.

    ARGS:
    -----
    None

    Return:
    ------
    None 
    
    """
    #Ask the date:
    speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["when"])
    date = listen()
    if "le" in date or "the" in date:
        _,day, month = date.split()
    else:
        day, month = date.split()

    # At what hour is the event?
    speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["time"]["what time?"])
    match = None
    while match == None:
        hour_and_minute = listen()
        match = re.search(r"(\d+) h (\d+)", hour_and_minute)
        if match:
            hour = match.group(1)
            minute = match.group(2)
        else:
            speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["time"]["fail"])

    # Duration of the event in hours:
    speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["duration"]["what duration"])
    duration = None
    duration = listen()
    while duration == None:
        speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["duration"]["fail"])
        duration = listen()

    # Importance of the event:
    speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["importance"]["what importance"])
    importance = None
    importance = listen()
    while importance not in ["faible", "modéré", "important", "critique"]:
        speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["importance"]["fail"])
        importance = listen()

    # Name of the event:
    speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["name"])
    name = listen()

    # All are string, we need to cast before going in DB:
    try:
        day = int(day)
        minute = int(minute)
        hour = int(hour)
        duration = int(duration)
    except Exception as e:
        print(f"[process: events] Error: {e}")
        return
    add_events_in_database(name, hour, minute, day, month, duration, importance)

def add_events_in_database(name, hour, minute, day, month, duration, importance):
    """
    DEF:
    ----

    Add the event in the Database

    ARGS:
    -----
    name:       string, it's the name of the event
    
    hour:       int
    
    minute:     int
    
    day:        int
    
    month:      string
    
    duration:   int

    importance: int

    RETURN:
    ------
    None
    """
    month_dic = {
        "janvier"     : 1,
        "février"     : 2,
        "mars"        : 3,
        "avril"       : 4,
        "mai"         : 5,
        "juin"        : 6,
        "juillet"     : 7,
        "aout"        : 8,
        "septembre"   : 9,
        "octobre"     : 10,
        "novembre"    : 11,
        "décembre"    : 12
    }
    importance_dic = {
        "faible": 0,
        "modéré":1,
        "important":2,
        "critique":3
    }

    # Test and affectation:
    id_month = month_dic.get(month)
    print(id_month)
    if id_month == None:
        print(f"[add_events_in_database] Error: month not in dictionnary")
        return
    
    importance_id = importance_dic.get(importance)
    if importance_id == None:
        print(f"[add_events_in_database] Error: importance not in dictionnary")
        return
    
    # Test to see if the hour, minute are realistic:
    if hour > 23 or hour <0:
        print(f"[add_events_in_database] Error: hour is between 0 and 23")
        return
    
    if minute > 59 or minute <0:
        print(f"[add_events_in_database] Error: minutes are between 0 and 59")
        return
    
    #TODO: ajouter une boucle de condition pour le nombre
    # de jours dans un mois!!!!

    # Test of the day:
    if day < 0 or day > 31:
        print(f"[add_events_in_database] Error: days are between 0 and 31")
        return
    
    # Get the id for the Event:
    request_for_id = "SELECT COUNT(*) FROM `events` WHERE 1"
    jarvis_cursor.execute(request_for_id)
    id_event = jarvis_cursor.fetchall()[0][0]

    # Insert the event:
    request_insert=(f"INSERT INTO `events`(`hour`, `minute`, `day`, `month`, `duration`, `description`, `importance`, `id`) VALUES ('{hour}','{minute}','{day}','{id_month}','{duration}','{name}','{importance_id}','{id_event}')")
    
    jarvis_cursor.execute(request_insert)


def get_event(param, value1, value2= None):
    """
    DEFS: 
    ----

    Search event in the events database.

    ARGS:
    ----

    param: string, parameter to check
            can be "name", "day"
    value: string or int, value of the parameter

    """
    request = None
    if param == "name":
        request = f"SELECT description, hour, minute, day, month, importance FROM `events` WHERE description = '{value1}'"
    if param == "day":
        request = f"SELECT description, hour, minute, day, month, importance FROM `events` WHERE day = {value1} AND month = {value2}"
    if request:
        jarvis_cursor.execute(request)
        result = jarvis_cursor.fetchall()
        result = result[0]
        if result == []:
            speak(" il n'y a pas d'événements prévu pour ce jour")
        else:
            #TODO: Crée un dictionnaire globale??
            importance_dic_reverse = {
                0 :"faible",
                1: "modéré",
                2: "important",
                3: "critique"
            }

            month_dic_reverse = {
                1: "janvier"   ,
                2: "février"   ,
                3: "mars"      ,
                4: "avril"     ,
                5: "mai"       ,
                6: "juin"      ,
                7: "juillet"   ,
                8: "aout"      ,
                9: "septembre" ,
                10: "octobre"  ,
                11: "novembre" ,
                12: "décembre" 
            }
            sentence = f"Vous avez l'événement {result[0]}, d'importance {importance_dic_reverse.get(result[5])}, prévu le {result[3]} {month_dic_reverse.get(result[4])} a {result[1]} heure {result[2]}"
    return sentence