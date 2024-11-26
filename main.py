import pygame
from include.functions import *
from include.header import *
from GUI.GUI_functions import *



def main():
    # Gui init:
    pygame.init()

    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    pygame.display.set_caption("JARVIS")
    font = pygame.font.Font(None, 45)
    clear_screen(screen)

    data = read_text_from_json(PATH_TEXT_JSON)
    answer = read_text_from_json(PATH_ANSWER_JSON)
    
    #TODO: peut etre trouver un meilleur emplacement pour cela:
    remove_from_request_history()

    pygame.display.flip()
    while(True):
        try:
            # Clear the screen:
            clear_screen(screen)
            pygame.display.flip()

            command = listen()
            if command:
                # Get the sentence, display on the GUI
                sentence = process_command(command,data,answer, ID_USER)
                sentence_to_display = append_n_to_display(sentence)
                display_sentence(sentence_to_display, font=font, screen=screen)
                pygame.display.flip()

                speak(sentence)
        except Exception as e:
            print(e)


main()
pygame.quit()
