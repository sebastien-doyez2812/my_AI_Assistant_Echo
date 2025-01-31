import mysql.connector
import speech_recognition as sr
import re
import mysql
import random
import pyttsx3
import speech_recognition as sr
import webbrowser
import webbrowser
from datetime import datetime, date, timedelta
import json
import requests
import wikipediaapi
from datetime import datetime
#from googletrans import Translator
from include.header import *
from pygame import mixer
import unicodedata
from AI.tools.llms import llm as llm
from AI.tools.llms import agent as agent
####################################
##      STANDARD FUNCTIONS        ##
####################################         

# Definition of the vocal engine of Jarvis:
engine = pyttsx3.init()
engine.setProperty('volume', 1.5)
engine.setProperty('rate', 200)


voices = engine.getProperty('voices')
# voice 0: french
# voice 1: english
engine.setProperty('voice', voices[1].id)

# To translate in French:
#translator = Translator()
# Fast research:
user_agent_wikipedia = "JarvisPython/1.0 (https://github.com/sebastien-doyez2812/AI-projects/AI_ChatBot)"
wiki = wikipediaapi.Wikipedia(user_agent_wikipedia, 'en')

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

    month_dic = {
        "Jan": "janvier",
        "Feb" : "février",
        "Mar": "mars",
        "Apr" : "avril",
        "May" : "mai",
        "Jun" : "juin",
        "Jul" :"juillet",
        "Aug" : "aout",
        "Sep" : "septembre",
        "Oct" : "octobre",
        "Nov" : "novembre",
        "Dec" : "décembre"
    }


    sentence = ""
    # Basic interaction:
    add_request(command, id_user)

    if any(keyword in command for keyword in data["salutation"]):
        print("heeeeeeeyyy")
        prompt = read_text_from_json(PATH_PROMPTS)["salutation"].format(USER = USER)
        sentence = f"Hello {USER}, how can I assist you today?"#llm.llm.invoke(prompt)
        return sentence
    
    if any(keyword in command for keyword in data["presentation"]):
        # TODO: to delete
        sentence = llm.llm.invoke(read_text_from_json(PATH_PROMPTS)["presentation"])
        return sentence

    if  any(keyword in command for keyword in data["veille"]):
        #TODO to delete
        sentence = llm.llm.invoke(read_text_from_json(PATH_PROMPTS)["sleep"])
        return sentence
   
    # Basic fonctionnalities:
    # What time is it?
    if any(keyword in command for keyword in data["heure"]):
        # I could use a AI agent, but the local LLM are not very good for that
        hour = get_hour()
        prompt = read_text_from_json(PATH_PROMPTS)["hour"].format(TIME = hour)
        sentence = llm.llm.invoke(prompt)
        return sentence

    # What's the weather?
    if any(keyword in command for keyword in data["meteo"]):
        query = re.search(r"weather for (.+)", command) or re.search(r"weather at (.+)", command)
        if query != None:
            city = query.group(1).strip()
        else:
            city = get_localisation()
        
        print(f"ville = {city}")
        speak(read_text_from_json(PATH_ANSWER_JSON)["weather"]["date"])
        date_listen = listen()
        today = date.today()
        if "today" in date_listen:
            day = today
        elif "tomorrow" in date_listen:
            day = today + timedelta(days=1)
        elif "in" in date_listen:
            print(date_listen)
            match = re.search(r"\d+", date_listen)
            print(match)
            if match:
                day = today + timedelta(days = int(match.group()))
        else: 
            #TODO: To improve!!!!
            # TODO a ajouter dans le JSON
            speak("I did not understand the day...")
            speak(" Give me the day")
            dd = int(listen())
            speak("give me the month")
            mm = int(listen())
            speak( "and the year?")
            aaaa = int(listen())
            day = f"{aaaa}-{mm}-{dd}"
        print(day)
        sentence = get_weather2(remove_accents(city), day)
        return sentence

    # Where are we?
    if any(keyword in command for keyword in data["localisation"]):
        city = get_localisation()
        sentence = f"We are at {city}"
        return sentence
    
    # Search on the web
    if any(keyword in command for keyword in data["youtube"]):
        query = re.search(r"search on YouTube (.+)", command)
        print(query)
        if query != None:            
            youtube(query.group(1))
            return "Opening Youtube, sir!"
        return

    if any(keyword in command for keyword in data["recherche rapide"]):
        print("recherche rapide")
        sentence = llm.llm.invoke(f"Summarize those result in 30 words maximum: {do_fast_research(command)}").replace("*", "")
        return sentence 
    
    if any(keyword in command for keyword in data["recherche"]):
        query = re.search(r"search (.+)", command) 
        sentence = search(query.group(1))
        return sentence
    
    # Functions with the database:
    if any(keyword in command for keyword in data["musique"]):
        query = re.search(r"(.+) online", command)
        if query != None:
            play_music_online()
        else:
            play_music_offline()
        return "I stop the music."
    
    if any(keyword in command for keyword in data["event"]):
        if "add" in command:
            add_event()
            return "Event added!"
        if "Is a event" in command:
            # TODO: a améliorer dans le futur:
            # mettre dans le json
            if "today" in command:
                today = datetime.now()
                get_event("day", today.strftime("%d") , today.strftime("%m"))
                return
            if "description" in command:
                speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["name"])
                name = listen()
                get_event("name", name)
                return


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
            month_day, hour, minute = find_when(word_to_find)
            print(month_day[0:3])
            month = month_dic.get(month_day.split(':')[0])
            day = month_day.split(':')[1]

            speak(read_text_from_json(PATH_ANSWER_JSON)["history"]["success"])
            for i in range(len(day)):
                sentence = f" le {day} {month}, a {hour} heure et {minute} minutes."
        else: 
            print("find_word ERROR: unable to understand the word")
        return sentence

    #######################################
    ##       AI Functionnalities         ##
    #######################################
    if command == None:
        return
    if any(keyword in command for keyword in data["analyse"]):
        res = agent.multi_agent_system.execute_task(command)
        return llm.llm.invoke("Summarize this in less than 25 words: " + res.get("output", "").replace("*", ""))
    else:
        # Use the agent to have a reponse
        return llm.llm.invoke("in 30 words maximum, answer to this: " + command)

    

    

    

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
        command = recognizer.recognize_google(audio, language="en-EN")
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


def remove_accents(input_str):
    """
    DEF:
    ----
    Remove the é of a Word, useful for French and for the Weather
    """
    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join(c for c in normalized_str if unicodedata.category(c) != 'Mn')



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
        return current_time
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
        #region = data["region"]
        return(city)
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
            description_trans= desc #translator.translate(desc, src='en', dest='fr')
            sentence = f"Aujourd'hui, à {city}, il fait {temp} degrées, mais le ressenti est de {real_temp} degrées. Le climat est {description_trans.text}"
            return sentence
    except Exception as e:
        print (f"get_weather error: {e}")



def get_weather2(city,date):
    """
    DEF:
    ----
    Get the weather for a place, for a date.

    ARGS:
    -----
    city: string, place where we want to know the weather
    date: string: AAAA-MM-DD

    RETURN:
    ------
    sentence JARVIS will say    
    """

    try: 
        # Get the API:
        api_key = read_text_from_json(PATH_PARAMETERS)["adv_api_meteo"][0]
        # Do a request:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=10&aqi=no&alerts=no"
        rep = requests.get(url)
        data = rep.json()

        # if the request is successful:
        if rep.status_code == 200: # 200 => OK
            forecast_days = data['forecast']['forecastday']

            # Find the date we want:
            for day in forecast_days:
                print(f"{day['date']} vs {date}")
                if str(day['date']) == str(date):
                    condition = day['day']['condition']['text']
                    temp_max = day['day']['maxtemp_c']
                    temp_min = day['day']['mintemp_c']
                    print(condition)
                    if str(condition) == "Overcast ":
                        condition = "ciel couvert"
                    #TODO add translation???
                    # TODO: a ameliorer, peut etre mettre le texte dans un JSON???
                    return (f"This is my predictions for {city}, the {date} : {condition}. "
                            f"temperature between {temp_min} °C and {temp_max} °C.")
            return f"Sorry, I did not find predictions for the {date}."
        else:
            return f"Error API : {data['error']['message']}"
    except Exception as e:
        print(e)






def do_fast_research(command):
    """
    Do a fast research on wikipedia, 
    
    ARGS: 
        the command( what JARVIS heard)
    """
    sentence = ""
    query = re.search(r"fast search on (.+)", command) or re.search(r"what is (.+)", command) or re.search(r"who is (.+)", command) or re.search(r"why (.+)", command)
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
                sentence = f"This is the result for {query.group(1)}"
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
    sentence = f"This is what I found for {query} on Google."
    return sentence


def youtube(request):
    """
    Research on Youtube

    ARGS:
        request: string, what we want to research on Youtube
    """
    url = f"https://www.youtube.com/results?search_query={request}"
    webbrowser.open(url)
    speak(f"This is the result for {request} on Youtube.")

################################################
# Functions with the use of the database       #
################################################

# Play musics:
def play_music_online():
    try:
        #TODO: mettre le 2 dans un JSON
        index = random.randint(0,2)
        jarvis_cursor.execute(f"SELECT link FROM musique WHERE id = {index}")
        url = jarvis_cursor.fetchall()[0][0]
        webbrowser.open(url)
    except Exception as e:
        print (f"play_music ERROR: {e}")

def play_song(path_on_pc):
    """
    DEF:
    ---
    Function used in play_music_offline,
    ARGS:
    ----
    path_on_pc: path of a song on the computer
    """
    mixer.music.stop()
    mixer.music.load(path_on_pc)
    mixer.music.play()

def play_music_offline():
    try:
        #TODO mettre le 2 dans un json:

        # Take a random number, and go to the music with this id
        index = 1#random.randint(1,2)
        jarvis_cursor.execute(f"SELECT path FROM musique WHERE id = {index}")
        path = jarvis_cursor.fetchall()[0][0]

        # Creation of a memory for the previous song
        path_mem = path
        play_song(path)
        while True:

            command = listen()
            if command != None:
                if "next" in command.lower() or "change" in command.lower():
                    # Chose another song:
                    speak("I Change the music...")
                    index = 2#random.randint(1,2)
                    jarvis_cursor.execute(f"SELECT path FROM musique WHERE id = {index}")
                    path_mem = path
                    path = jarvis_cursor.fetchall()[0][0]

                    # Play the song
                    
                    play_song(path)
                    
                elif "previous" in command.lower() or "return" in command.lower():
                    speak("This is the previous song...")
                    play_song(path_mem)
                    
                elif "pause" in command.lower():
                    speak("Musique paused")
                    mixer.music.pause()
                    
                elif "continue" in command.lower():
                    speak("Unpause the music.")
                    mixer.music.unpause()
                    
                elif "stop" in command.lower():
                    mixer.music.stop()
                    return "I stopped the music..."
                    
                    
    except Exception as e:
        mixer.music.stop()
        print(e)





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
        #keyword = "%"+keyword+"%"
        sql_request = f"SELECT day, hour, minute FROM requests WHERE command LIKE '{keyword}'"
        print(sql_request)
        jarvis_cursor.execute(sql_request)
        result = jarvis_cursor.fetchall()
        return (result[0][0], result[0][1], result[0][2])
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
    if "today" in date:
        day = datetime.now()
    elif "le" in date or "the" in date:
        match  = re.search(r"the (\d+)th")
        day = match.group(1)
        _,_, month = date.split()
    else:
        day, month = date.split()

    # At what hour is the event?
    speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["time"]["what time?"])
    match = None
    while match == None:
        hour_and_minute = listen()
        print(hour_and_minute)
        match = re.search(r"(\d+):(\d+) a.m.", hour_and_minute) or re.search(r"(\d+):(\d+) p.m.", hour_and_minute)
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

    duration = re.search(r"(\d+) hour", duration)
    # # Importance of the event:
    # speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["importance"]["what importance"])
    # importance = None
    # importance = listen()
    # while importance not in ["faible", "modéré", "important", "critique"]:
    #     speak(read_text_from_json(PATH_ANSWER_JSON)["events"]["importance"]["fail"])
    #     importance = listen()

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
    add_events_in_database(name, hour, minute, day, month, duration)

# TODO: adding a functionality of translation on the GUI
def translate(texte):#, source_lang='en', target_lang='fr'):
    """
    DEF:
    ----
    Translate a text in another language
    
    ARGS:
    -----
    text: string
    source_lang: (otpionnal) 2 chars
    target_lang: (optionnal) 2 chars
    
    RETURN:
    -------
    return a translation of the text
    """
    print(texte)
    #traducteur = Translator()
    #traduction = traducteur.translate(texte, src='en', dest='fr')
    #return traduction.text


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
        "january"     : 1,
        "february"     : 2,
        "march"        : 3,
        "april"       : 4,
        "may"         : 5,
        "june"        : 6,
        "july"     : 7,
        "august"        : 8,
        "september"   : 9,
        "october"     : 10,
        "november"    : 11,
        "december"    : 12
    }
    # importance_dic = {
    #     "faible": 0,
    #     "modéré":1,
    #     "important":2,
    #     "critique":3
    # }

    # Test and affectation:
    id_month = month_dic.get(month)
    if id_month == None:
        print(f"[add_events_in_database] Error: month not in dictionnary")
        return
    
    # importance_id = importance_dic.get(importance)
    # if importance_id == None:
    #     print(f"[add_events_in_database] Error: importance not in dictionnary")
    #     return
    
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
    request_insert=(f"INSERT INTO `events`(`hour`, `minute`, `day`, `month`, `duration`, `description`, `id`) VALUES ('{hour}','{minute}','{day}','{id_month}','{duration}','{name}','{id_event}')")
    
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
        request = f"SELECT description, hour, minute, day, month FROM `events` WHERE description = '{value1}'"
    if param == "day":
        request = f"SELECT description, hour, minute, day, month FROM `events` WHERE day = {value1} AND month = {value2}"
    if request:
        jarvis_cursor.execute(request)
        result = jarvis_cursor.fetchall()
        result = result[0]
        if result == []:
            speak(" No event planned")
        # else:
        #     #TODO: Crée un dictionnaire globale??
        #     importance_dic_reverse = {
        #         0 :"faible",
        #         1: "modéré",
        #         2: "important",
        #         3: "critique"
        #     }

            month_dic_reverse = {
                1: "January"   ,
                2: "February"   ,
                3: "March"      ,
                4: "April"     ,
                5: "May"       ,
                6: "june"      ,
                7: "july"   ,
                8: "august"      ,
                9: "september" ,
                10: "october"  ,
                11: "november" ,
                12: "december" 
            }
            sentence = f"Event {result[0]},  planned the {result[3]} {month_dic_reverse.get(result[4])} at {result[1]} : {result[2]}"
    return sentence