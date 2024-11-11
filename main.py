import threading
from include.functions import *
from include.header import *

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