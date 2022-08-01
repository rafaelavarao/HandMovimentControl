import cv2
import time
import numpy as np
import HandTrakingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volrange=volume.GetVolumeRange()
print(volrange)
minvol=volrange[0]
maxvol=volrange[1]
vol=0
volBar=400
volPer=0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])

        ## pointID, x, y = [4, 356, 383]
        # pointID = [4, 356, 383][0]
        # x = [4, 356, 383][1]
        # y = [4, 356, 383][2]

        x1, y1 = lmList[4][1], lmList[4][2] #valores 
        x2, y2 = lmList[8][1], lmList[8][2]
        x3, y3 = lmList[7][1], lmList[7][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        lx,ly=(x1+x2)//2,(y1+y2)//2
        cv2.circle(img, (x1, y1), 10, (255,0,255), cv2.FILLED) #circle thumb
        cv2.circle(img, (x2, y2), 10, (255,0,255), cv2.FILLED) #circle 8(index finger tip)
        cv2.line(img, (x1,y1), (x2, y2), (255,0,255), 3) #line between circles
        cv2.circle(img, (cx, cy), 15, (255,0,255), cv2.FILLED) #middle circle

        lengh = math.hypot(x2-x1, y2-y1)
        print(lengh)

        finger_size = math.hypot(x3-x2, y3-y2)

        #Hand range 50 - 300
        #Volume range -74 - 0

        vMin = 50
        vMax = 300

        vMin = int(finger_size/2)
        vMax = int(6*finger_size)

        vol=np.interp(int(lengh),[vMin,vMax],[minvol,maxvol])
        volBar = np.interp(int(lengh), [vMin,vMax], [400, 150])
        volPer= np.interp(int(lengh), [vMin,vMax], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)

        # vol=np.interp(int(lengh),[50,220],[minvol,maxvol])
        # volBar = np.interp(int(lengh), [50, 220], [400, 150])
        # volPer= np.interp(int(lengh), [50, 220], [0, 100])
        # volume.SetMasterVolumeLevel(vol, None)
        # if lengh<50:
        #     cv2.circle(img, (lx, ly), 10, (0, 255, 0), cv2.FILLED)


    #creating the rectangle that will decrease and increase the value of the volume
    cv2.rectangle(img,(50,150),(85,400),(0,255,0),2)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0),cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (50, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (250, 250, 250), 2)


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f' FPS: {int(fps)}', (10,70), cv2.FONT_HERSHEY_PLAIN, 3,
                (255 ,0 , 0), 3)

    cv2.imshow('image', img)
    key = cv2.waitKey(1) & 0xff

    if key == ord('q'):
        break