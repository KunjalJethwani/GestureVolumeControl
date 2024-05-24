# Importing necessary libraries
import cv2
import time
import math
import numpy as np
import mediapipe as mp
import handTrackingModule as htm
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialisation
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

vol = 0
volBar = 400
volPer = 0

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0) # 0 for default camera
cap.set(3, wCam) # setting width of camera frame
cap.set(4, hCam) # setting width of camera frame
pTime = 0

detector = htm.handDetector(detectionCon = 0.7)

while True:
    success, img = cap.read()
    img = detector.findHands(img, draw = False)
    lmList = detector.findPosition(img, draw = False)

    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2] # index 4 gives position of tip of the thumb
        x2, y2 = lmList[8][1], lmList[8][2] # index 8 gives position of tip of the index finger
        cx, cy = (x1+x2)//2, (y1+y2)//2

        # Highlighting the tips of the thumb and finger by drawing to circles, joing them with 
        # a line, and making another circle in the centre
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) # math.hypot(x2-x1, y2-y1)
        print(length)

        # Hand range 50 - 200
        # Volume Range -65 - 0
        # Hand range must be converted to volume range
        vol = np.interp(length, [50, 200], [minVol, maxVol]) # sets volume acc to length of span covered by themb and index finger
        volBar = np.interp(length, [50, 200], [400, 150]) # To align length of inner(vol lvl) bar with the outer bar
        volPer = np.interp(length, [50, 200], [0, 100])
        volume.SetMasterVolumeLevel(vol, None) # sets current volume

        if length <= 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), 3, cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 
                3, (255, 0, 0), 3)
    
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 
                3, (255, 0, 255), 3)
    
    cv2.imshow('Image', img)
    cv2.waitKey(1)