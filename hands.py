#coding=utf-8
import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

def findHands():
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    indexPos = None
    thumbPos = None

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            for id, lm in enumerate(landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                if id == 8: # index finger
                    cv2.circle(imgRGB, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                    indexPos = (cx, cy)
                elif id == 4: # thumb
                    thumbPos = (cx, cy)

            mpDraw.draw_landmarks(imgRGB, landmarks, mpHands.HAND_CONNECTIONS)

    return imgRGB, indexPos, thumbPos