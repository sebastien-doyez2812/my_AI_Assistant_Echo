import threading
from include.functions import *
from include.header import *

def process_command(command, data, answer):
    # Basic interaction:
    print(command)
    print(data["meteo"])
    if any(keyword in command for keyword in data["salutation"]):
        speak(f"Bonjour {USER}, Comment puis je vous aider aujourd'hui")
    if any(keyword in command for keyword in data["presentation"]):
        speak(answer["presentation"])
    if  any(keyword in command for keyword in data["veille"]):
        speak(answer["veille"])

    # Basic fonctionnalities:
    if any(keyword in command for keyword in data["heure"]):
        get_hour()
    if any(keyword in command for keyword in data["meteo"]):
        get_weather()
    if any(keyword in command for keyword in data["localisation"]):
        city, region = get_localisation()
        speak(f"Nous sommes a {city}, {region}")
    if any(keyword in command for keyword in data["recherche rapide"]):
        print("recherche rapide")
        do_fast_research(command)




def main():
    data = read_text_from_json(PATH_TEXT_JSON)
    answer = read_text_from_json(PATH_ANSWER_JSON)

    while(True):
        command = listen()

        #TODO : delete the print:
        print(command)

        if command != None:
            process_command(command,data,answer)


main()