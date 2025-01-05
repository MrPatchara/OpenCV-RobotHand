import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from cvzone.SerialModule import SerialObject

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1,detectionCon=0.7)
mySerial = SerialObject("COM4", 115200, 1)


while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)
    if hands:
        fingers = detector.fingersUp(hands[0])
        #print(fingers)
        mySerial.sendData(fingers)
    cv2.imshow("Image", img)
    cv2.waitKey(1)