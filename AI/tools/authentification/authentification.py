import pygame
import cv2
import sys 
import time 
import subprocess

def loading(screen,sentence, font):
    #TODO: define the 154 as the number of images is IMG/loading
    for i in range(154):
        name = f"IMG/loading/frame_{i}.png"
        frame = cv2.imread(name)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_surf = pygame.surfarray.make_surface(frame.swapaxes(0,1))
        screen.blit(frame_surf, (550,120))

        # Write the sentence on the screen
        text_surface = font.render(sentence, True, (255,255,255))
        text_rect = text_surface.get_rect(topleft = (670,420))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
    
def autentification(screen, cap, font):
    """
    DEF:
    ----
    AI verification 
    
    ARGS:
    -----
    screen, define by pygame

    RETURN:
    -------
    None, just a green rectangle around the web cam if 
    the AI recognise the user, red else
    /!\ this function blocks the process while the used is not authenfied!
    """

    # is_user will be True if the AI recognise the user
    is_user = False

    #TODO To delete
    i = 0
    while ( is_user == False ):
        _ , frame = cap.read()
        screen.fill((0,0,0))
        # Prepocess for the AI, and imshow the image on GUI
        frame = preprocess_imshow(frame)

        cv2.imwrite('AI/tools/authentification/img_to_test.jpg', frame)
        # webcam give BGR but opencv need RGB:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0,1))
        screen.blit(frame_surface, (550,120))
        

        pygame.draw.rect(screen, (0,0,255), (530, 100, 552, 552), width= 5)
        text_surface = font.render("Running, please wait......", True, (0,0,255))
        text_rect = text_surface.get_rect(topleft = (620,670))
        screen.blit(text_surface, text_rect)
        ###########################################
        ##        Implementation of AI here      ##
        ###########################################

        pygame.display.flip()

        command = ["conda", "run", "-n",  "tf", "python", "AI/tools/authentification/AI_functions.py"]

        subprocess.run(command, capture_output=True, text=True)
        
        with open("AI/tools/authentification/result_aut.txt", 'r') as file:
            if float(file.readline()) > 0.85:
                is_user = True
            else: 
                screen.fill((0,0,0))    
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0,1))
                screen.blit(frame_surface, (550,120))

                pygame.draw.rect(screen, (255,0,0), (530, 100, 552, 552), width= 5)
                text_surface = font.render("Not verified.", True, (255,0,0))
                text_rect = text_surface.get_rect(topleft = (700,670))
                screen.blit(text_surface, text_rect)
        file.close()
        time.sleep(1)

    # User authentified, just show a frame nd a green rectangle for 2 seconds:
    screen.fill((0,0,0))
    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0,1))

    # Show the image:
    screen.blit(frame_surface, (550,120))

    # Draw a green rectangle:
    pygame.draw.rect(screen, (0,255,0), (530, 100, 552, 552), width= 5)

    # Write a message:
    text_surface = font.render("Authentification OK", True, (0,255,0))
    text_rect = text_surface.get_rect(topleft = (700,670))

    # Show all the data:
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    time.sleep(2)

    return True

def preprocess_AI(frame):
    # Preprocess for the AI
    # TODO: Put that function here or in AI folder????
    frame = frame[120:120+250, 200:200+250]
    frame = cv2.resize(frame, (100,100))
    frame = frame / 255.0
    return frame


def preprocess_imshow(frame):
    """
    DEF:
    ----
    Give us the same frame dimension as the preprocess for the AI.
    Used only for show the image on the GUI
    
    ARGS:
    -----
    frame, the frame we want to do preprocess on

    RETURN:
    -------
    preprocessed frame
    """
    frame = frame[120:120+250, 200:200+250]
    frame = cv2.resize(frame, (512, 512))
    return frame


def start_jarvis(screen, font):
    """
    DEF:
    ----
    the function which start when jarvis start.
    loading screen + authentification...
    ARGS:
    -----
    screen
    font

    RETURN:
    -------
    None, because authentification will block if the user is not authentified.

    
    """

    # Start the webcam:
    cap = cv2.VideoCapture(0)

    # Check if the webcam is open:
    if not cap.isOpened():
        sys.exit()
    
    # Loading screen: give Jarvis 2 seconds to start...
    loading(screen, "JARVIS loading...", font)

    # authentification screen:
    autentification(screen,cap, font)