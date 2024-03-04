import imutils
import cv2
from Shapedetector import ShapeDetector

class ShpCenter:

    def __init__(self):
        pass

    def update(self, frame, frameCenter):
        
        resized = imutils.resize(frame, width=200)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 5)
        thresh = cv2.threshold(blurred, 60, 240, cv2.THRESH_BINARY)[1]
        thresh = cv2.bitwise_not(thresh)

        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        sd = ShapeDetector()

        for c in cnts:
            # find center and detect name of shape using contour
            M = cv2.moments(c)
            if M["m00"] > 0:
                centerX.value = int((M["m10"] / M["m00"]) * ratio)
                centerY.value = int((M["m01"] / M["m00"]) * ratio)
    
                shape = sd.detect(c)
    
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                
                try:
                    #objectLoc = obj.update(frame, (centerX.value, centerY.value))
                    #((objX.value, objY.value), rect) = objectLoc
                    objectLoc = c
                except:
                    print("object stuff weird...")

                return (c, thresh[0])
        return(frameCenter, None)
        
