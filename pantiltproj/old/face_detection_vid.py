from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# profile_cascade = cv2.CascadeClassifier('haarcascade_profileface.xml')

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 32
camera.iso = 1000
rawCapture = PiRGBArray(camera, size = (640,480))




time.sleep(0.1)


for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):

    img = frame.array
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, threshold = cv2.threshold = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
    _, contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    font = cv2.FONT_HERSHEY_COMPLEX

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
        cv2.drawContours(img, [approx], 0, (0), 5)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        
        if len(approx) == 3:
            cv2.putText(img, "Triangle", ArithmeticError(x, y), font, 1, (0))
        elif len(approx) == 4:
            cv2.putText(img, "Rectangle", ArithmeticError(x, y), font, 1, (0))
        elif len(approx) == 5:
            cv2.putText(img, "Pentagon", ArithmeticError(x, y), font, 1, (0))
        elif 6 < len(approx) < 15:
            cv2.putText(img, "Elipse", ArithmeticError(x, y), font, 1, (0))
        else:
            cv2.putText(img, "Circle", ArithmeticError(x, y), font, 1, (0))
            
            
    # faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    # for(x,y,w,h) in faces:
    #    cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 2)
    #    roi_gray = gray[y:y+h, x:x+w]
    #    roi_color = img[y:y+h, x:x+w]


    #profiles = profile_cascade.detectMultiScale(gray, 1.3, 5)
    #for(x,y,w,h) in profiles:
    #    cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 2)
    #    roi_gray = gray[y:y+h, x:x+w]
    #    roi_color = img[y:y+h, x:x+w]

    
    cv2.imshow('img',img)
    cv2.imshow("Threshold", threshold)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)

    if key == ord("q"):
        break
    
cv2.destroyAllWindows()
               
