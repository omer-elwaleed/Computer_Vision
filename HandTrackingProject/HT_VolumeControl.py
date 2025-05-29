
import cv2
import mediapipe as mp
import numpy as np
import time
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#################################################################################
wCam, hCam = 640, 480
#################################################################################

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]
#print(f"Volume Range: {min_vol} dB to {max_vol} dB")


vol = 0
vol_bar= 400
percentage = 0
while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) !=0:
        #print(lmList[4],lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)/2, (y1+y2)/2

        cv2.circle(img,(x1,y1), 12, (255, 0, 255), cv2.FILLED)
        cv2.circle(img,(x2,y2), 12, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1,y1),(x2,y2), (255, 0, 255), 3)
        cv2.circle(img,(int(cx),int(cy)), 10, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y2)
        #print(length)

        vol = np.interp(length,[0, 200], [min_vol, max_vol])
        vol_bar = np.interp(length,[0, 200], [400, 150])
        percentage = np.interp(length,[0, 200], [0, 100])
        print(int(length),vol)
        volume.SetMasterVolumeLevel(vol, None)


        if length<30:
            cv2.circle(img,(int(cx),int(cy)), 10, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img, (50,150), (85,400), (255, 0, 0), 3) 
    cv2.rectangle(img, (50,int(vol_bar)), (85,400), (255, 0, 0), cv2.FILLED) 
    cv2.putText(img, f'{int(percentage)}%', (40,440), cv2.FONT_HERSHEY_PLAIN,2, (255, 0, 0), 3)



    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS:{int(fps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break