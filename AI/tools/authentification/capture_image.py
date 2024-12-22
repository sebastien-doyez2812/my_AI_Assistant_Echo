import uuid
import cv2 
import os



ANC_PATH = "AI/tools/authentification/anc"
POS_PATH = "AI/tools/authentification/pos"
cap = cv2.VideoCapture(0)
while cap.isOpened():
  ret, frame = cap.read()
  frame = frame[120:120+250, 200:200+250]
  # Show the image:
  cv2.imshow("Image taken", frame)


  if cv2.waitKey(1) &0XFF == ord('a'):
    imgname = os.path.join(ANC_PATH, '{}.jpg'.format(uuid.uuid1()))
    cv2.imwrite(imgname, frame)
  if cv2.waitKey(1) &0XFF == ord('p'):
    imgname = os.path.join(POS_PATH, '{}.jpg'.format(uuid.uuid1()))
    cv2.imwrite(imgname, frame)
  if cv2.waitKey(1) & 0XFF == ord('q'):
    break

# Realease the webcam:    
cap.release()
#cv2.destroyAllWindows()