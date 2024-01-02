#coding=utf-8
from tkinter import *
from PIL import Image, ImageTk
import hands
import cv2
import math
import touch
import win32api
import os, sys


bounds = [[80, 80], [545, 400]]
touching = False
activationBuffer = 3
framesHeld = 0
window = None
lastPositions = []
lastIndexPosition = []
lastThumbPosition = []
programActive = False
clicking = False
corner = "none"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def distance(tuple1, tuple2):
    return math.sqrt((tuple1[0] - tuple2[0])**2 + (tuple1[1] - tuple2[1])**2)

def num_to_range(num, inMin, inMax, outMin, outMax):
  return int(outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                  - outMin)))

def lerp(a: float, b: float, t: float) -> float:
    return (1 - t) * a + t * b

def video_stream():
    global bounds
    global touching
    global activationBuffer, framesHeld
    global window
    global lastPositions
    global lastIndexPosition, lastThumbPosition
    global programActive

    img, indexPos, thumbPos = hands.findHands()
    realIndexPos = indexPos
    realThumbPos = thumbPos
    cv2.rectangle(img, bounds[0], bounds[1], (255, 0, 255), 3)
    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im)
    lmain.imgtk = imgtk
    lmain.config(image=imgtk)
    lmain.pack()
    lmain.after(1, lambda: video_stream())
    if indexPos is None or thumbPos is None:
        return (indexPos, thumbPos)
    
    if (not programActive):
        return (indexPos, thumbPos)
    
    if len(lastPositions) >= 2:
        # sumAngles = [0, 0]
        # for i in range(len(lastPositions)):
        #     movementDirection = [(indexPos[0] - lastIndexPosition[i][0], indexPos[1] - lastIndexPosition[i][1]), (thumbPos[0] - lastThumbPosition[i][0], thumbPos[1] - lastThumbPosition[i][1])]
        #     # compute angle from vectors
        #     angle = (math.atan2(movementDirection[0][1], movementDirection[0][0]) * 180 / math.pi, math.atan2(movementDirection[1][1], movementDirection[1][0]) * 180 / math.pi)
        #     sumAngles[0] += angle[0]
        #     sumAngles[1] += angle[1]
        # avgAngle = (sumAngles[0] / len(lastPositions), sumAngles[1] / len(lastPositions))
        # print(abs(avgAngle[0] - avgAngle[1]))
        # if abs(avgAngle[0] - avgAngle[1]) > 150 and math.dist(indexPos, thumbPos) < math.dist(lastIndexPosition[0], lastThumbPosition[0]):
        #     indexPos = lastIndexPosition[-1]
        #     thumbPos = lastThumbPosition[-1]
        if distance(lastIndexPosition[-1], lastThumbPosition[-1]) > distance(indexPos, thumbPos) and distance(lastIndexPosition[-2], lastThumbPosition[-2]) > distance(lastIndexPosition[-1], lastThumbPosition[-1]):
            indexPos = (lerp(lastIndexPosition[-1][0], indexPos[0], 0.1), lerp(lastIndexPosition[-1][1], indexPos[1], 0.1))


    indexMapped = (num_to_range(indexPos[0], bounds[0][0], bounds[1][0], 0, 1920), num_to_range(indexPos[1], bounds[0][1], bounds[1][1], 0, 1080))

    if len(lastPositions) < 3:
        lastPositions.append(indexMapped)
        lastIndexPosition.append(indexPos)
        lastThumbPosition.append(thumbPos)
    else:
        lastPositions.pop(0)
        lastPositions.append(indexMapped)
        lastIndexPosition.pop(0)
        lastIndexPosition.append(indexPos)
        lastThumbPosition.pop(0)
        lastThumbPosition.append(thumbPos)
    
    sumX = 0
    sumY = 0
    for i in range(len(lastPositions)):
        sumX += lastPositions[i][0]
        sumY += lastPositions[i][1]
    
    indexMapped = (sumX // len(lastPositions), sumY // len(lastPositions))

    win32api.SetCursorPos(indexMapped)
    window.geometry("32x32+" + str(indexMapped[0]) + "+" + str(indexMapped[1]))

    if (math.dist(realIndexPos, realThumbPos) < 10):
        
        if not touching:
            framesHeld += 1
            if framesHeld >= activationBuffer:
                touch.makeTouch(indexMapped[0], indexMapped[1], 5)
                touching = True
                framesHeld = 0
        else:
            touch.makeHold(indexMapped[0], indexMapped[1], 5)
    else:
        if touching:
            framesHeld += 1
            if framesHeld >= activationBuffer:
                touch.makeRelease()
                touching = False
                framesHeld = 0

    return (indexPos, thumbPos)

def pollClick(eventorigin):
    global x0,y0, clicking, corner
    x0 = eventorigin.x
    y0 = eventorigin.y
    if clicking:
        if corner == "topLeft":
            bounds[0] = (x0, y0)
        elif corner == "bottomRight":
            bounds[1] = (x0, y0)
        elif corner == "bottomLeft":
            bounds[0] = (x0, bounds[0][1])
            bounds[1] = (bounds[1][0], y0)
        elif corner == "topRight":
            bounds[0] = (bounds[0][0], y0)
            bounds[1] = (x0, bounds[1][1])


def leftClick(eventorigin):
    global clicking
    global x0,y0, corner
    x0 = eventorigin.x
    y0 = eventorigin.y
    print(x0, y0)
    clicking = True
    if distance((x0, y0), bounds[0]) < 5:
        corner = "topLeft"
    elif distance((x0, y0), bounds[1]) < 5:
        corner = "bottomRight"
    elif distance((x0, y0), (bounds[0][0], bounds[1][1])) < 5:
        corner = "bottomLeft"
    elif distance((x0, y0), (bounds[1][0], bounds[0][1])) < 5:
        corner = "topRight"
    else:
        corner = "none"

def leftRelease(eventorigin):
    global clicking, corner
    clicking = False
    cornerq = "none"

def toggleStart():
    global programActive
    programActive = not programActive
    if programActive:
        startButton.config(text="Stop")
        win32api.ShowCursor(False)
        window.deiconify()
    else:
        startButton.config(text="Start")
        win32api.ShowCursor(True)
        window.withdraw()


if __name__ == "__main__":


    root = Tk()

    root.iconify()

    window = Toplevel(root)
    window.attributes('-topmost', True)
    window.geometry("32x32+600+600")
    window.overrideredirect(1)

    window.attributes('-transparentcolor', 'grey')

    pointer = ImageTk.PhotoImage(file=resource_path("pointer.png"))

    label = Label(window, image=pointer, bg="grey", fg="grey")

    label.pack()
    window.withdraw()

    mainWindow = Toplevel(root)
    frame = Frame(mainWindow)
    frame.pack()
    lmain = Label(mainWindow)

    lmain.bind('<ButtonPress-1>', leftClick)
    lmain.bind('<ButtonRelease-1>', leftRelease)
    lmain.bind('<B1-Motion>', pollClick)

    # info text
    info = Label(frame, text="Click and drag the corners of the pink rectangle to set bounds for your monitor.")
    info.pack(side=BOTTOM)

    # add button to start and stop
    startButton = Button(frame, text="Start", command=toggleStart)
    startButton.pack(side=BOTTOM)

    video_stream()
    
    
    root.mainloop()
