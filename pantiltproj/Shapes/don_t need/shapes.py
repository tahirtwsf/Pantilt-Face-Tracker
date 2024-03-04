from Shapedetector import ShapeDetector
import argparse
import imutils
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 32
camera.iso = 500
rawCapture = PiRGBArray(camera, size = (640,480))

sleep(0.1)


# Terminal arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True, help="path to the input image")
# args = vars(ap.parse_args())



for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):

    # camera._check_camera_open()

    image = frame.array
    resized = imutils.resize(image, width=200)
    ratio = image.shape[0] / float(resized.shape[0])

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 5)
    thresh = cv2.threshold(blurred, 60, 240, cv2.THRESH_BINARY)[1]
    #thresh = cv2.bitwise_not(thresh)

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    sd = ShapeDetector()


    for c in cnts:
        # find center and detect name of shape using contour
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX = int((M["m10"] / M["m00"]) * ratio)
            cY = int((M["m01"] / M["m00"]) * ratio)

            shape = sd.detect(c)[0]

            c = c.astype("float")
            c *= ratio
            c = c.astype("int")
            cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
            cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    #show output image
    cv2.imshow('Image',image)
    cv2.imshow('Thresh', thresh)
    key = cv2.waitKey(1) & 0xFF
    if key & 0xFF == ord('q'):
            break
    rawCapture.truncate(0)

cv2.destroyAllWindows()
