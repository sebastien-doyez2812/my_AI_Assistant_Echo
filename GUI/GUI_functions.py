import pygame
import requests

#TODO: put WIDTH, HEIGHT in a Json
WIDTH, HEIGHT = 512, 512
PATH_IMAGE = "IMG/"
BLUE = (0, 235, 255)
ORANGE = (100,42,0)
WHITE = (255,255,255)
BLACK = (0,0,0)


def append_n_to_display(sentence):
    """
    DEF:
    ----
    Add '\n' every 6 words

    ARGS:
    -----
    sentence: string, the sentence to add the \n

    RETURNS: 
    --------
    the sentence 
    """
    sentence_displayed = ""
    words = sentence.split()
    for i in range (len(words)):
        sentence_displayed += " " + words[i]
        if i % 5 == 0 and i != 0: 
            sentence_displayed += "\n"
    return sentence_displayed

def display_sentence(sentence_n, font, screen):
    """
    DEF:
    -----
    do the printing on the screen

    ARGS:
    -----
    sentence_n: string, sentence with some \n, output of append_n_to_display
    font and screen: define for pygame
    """
    lines = sentence_n.split('\n')
    space = 5
    for i in range ( len(lines)):
        text_surface = font.render(lines[i], True, BLUE)
        text_rect = text_surface.get_rect(topleft = (600,650 + i *(space + text_surface.get_height())))
        screen.blit(text_surface, text_rect)

def clear_screen(screen):
    """
    DEF:
    -----
    Clear the screen, and plot the initial icon

    ARGS:
    -----

    screen, define by pygame
    """
    screen.fill(BLACK)
    frame_JARVIS_icone = pygame.image.load(PATH_IMAGE + "jarvis.jpg")
    frame_JARVIS_logo = pygame.image.load(PATH_IMAGE + "JARVIS_logo.png")
    meteo(screen)
    connection(screen)
    screen.blit(frame_JARVIS_icone, (600, 90))
    screen.blit(frame_JARVIS_logo, (1400,30))


def connection(screen):
    """
    DEFS:
    ----
    display connection infos on the GUI oof JARVIS

    ARGS:
    -----
    screen, define by pygame
    """
    
    frame_connection_icone = pygame.image.load(PATH_IMAGE + "connected.png")
    screen.blit(frame_connection_icone, (45, 285))
    font = pygame.font.Font(None, 45)
    text_robot = "Robot not connected"
    text_surface_robot = font.render(text_robot, True, BLUE)
    text_rect_robot = text_surface_robot.get_rect(topleft= (180, 350))
    text_wifi = "Wifi OK"
    text_surface_wifi = font.render(text_wifi, True, BLUE)
    text_rect_wifi = text_surface_wifi.get_rect(topleft= (180, 300))
    screen.blit(text_surface_wifi, text_rect_wifi)
    screen.blit(text_surface_robot, text_rect_robot)

def meteo(screen):
    """
    DEFS:
    ----
    display an icone for weather on the GUI oof JARVIS
    display the temperature and the city

    ARGS:
    -----
    screen, define by pygame
    """
    # Search the actual weather:
    #TODO: have access to parameters.json
    api_key_meteo = "e5859cf005fb60a5e50a53233a95b79a"
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
        icon_weather =""
        
        if desc == 'broken clouds' or desc == 'few clouds':
            icon_weather = "sun_cloud.png"
        elif desc == 'clouds' or desc == 'overcast clouds':    
            icon_weather = "clouds.png"
        elif desc == "sun":
            icon_weather = "sun.png"
        elif desc == "snow":
            icon_weather = "snow.png"
        elif desc == "rain":
            icon_weather = "rain.png"
        else:
            icon_weather = "idontknow.png"
    
        frame_weather_icone = pygame.image.load(PATH_IMAGE + icon_weather)
        screen.blit(frame_weather_icone, (30, 50))
        font = pygame.font.Font(None, 60)
        text = str(temp) + "°C"
        text_surface_city = font.render(str(city), True, BLUE)
        text_rect_city = text_surface_city.get_rect(topleft= (180, 110))
        text_surface = font.render(text, True, BLUE)
        text_rect = text_surface.get_rect(topleft= (180, 50))
        screen.blit(text_surface, text_rect)
        screen.blit(text_surface_city, text_rect_city)


#TODO: delete that and find a way to have access to this with functions only
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
