import subprocess 
import cv2

cap = cv2.VideoCapture(0)

_, frame = cap.read()
frame = frame[120:120+250, 200:200+250]

cv2.imshow("test", frame)
cv2.waitKey(0)
cv2.imwrite("AI/tools/authentification/img_to_test.jpg", frame)


print("let's go!")
command = ["conda", "run", "-n",  "tf", "python", "AI/tools/authentification/AI_functions.py"]

resultat = subprocess.run(command, capture_output=True, text=True)

with open("file.txt", 'r') as file:
    print(f"la probab est de {float(file.readline())}")
print("fin")
