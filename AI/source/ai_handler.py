"""
Author: Sebastien Doyez

AI handler for JARVIS
"""

import torch
import torch.nn as nn
import cv2
import numpy as np
import time
from models import *


PATH_MODEL_CLOTHES_CLASS = "AI\source\models\clothes_classification_model.pth"
cloth_model = clothes_network_LeNet5(clothes_network_LeNet5.NUMBER_OF_CLASSES) 


def clothes_classification():
    """
    DEF:
    ----

    ARG:
    ----

    RETURN:
    -------

    """
    # Loading the model and the labels: 
    cloth_model.load_state_dict(torch.load(PATH_MODEL_CLOTHES_CLASS, map_location=torch.device('cpu')))
    cloth_model.eval() 

    # Use the webcam:
    cap = cv2.VideoCapture(0)  
    ret, frame = cap.read()
    if not ret:
        print("[clothes_classification] ERROR: cannot open webcam")
        return

    # Pre process:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    resized = cv2.resize(gray, (32, 32))
    tensor = torch.tensor(resized, dtype=torch.float32).unsqueeze(0).unsqueeze(0) / 255.0 

    # Prediction:
    with torch.no_grad():
        output = cloth_model(tensor)
        pred = torch.argmax(output).item() 

    # Find the right prediction:
    prediction = clothes_network_LeNet5.cloths_labels_map.get(pred)

    print(f"\n\n\n{prediction}\n\n")
    return prediction

clothes_classification()