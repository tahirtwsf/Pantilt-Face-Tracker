import imutils
import cv2

class ObjCenter:

    def __init__(self):
        # load Haar cascade for detector
        #self.detector = cv2.CascadeClassifier(haarpath)
        pass
    # def __init__(self):
        # load Haar cascade for detector
        # self.detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def update(self, frame, frameCenter):
        #convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #detect all faces in the input frame
        rects = self.detector.detectMultiScale(gray, scaleFactor=1.05,
                                               minNeighbors=9, minSize=(30, 30),
                                               flags=cv2.CASCADE_SCALE_IMAGE)
        
        # peri = cv2.arcLength(c)
        # approx = cv2.approxPolyDP(c, 0.04 * peri, True)

        #check to see if a face was found
        if len(rects) > 0:
            #extract the bounding box coords of the face and
            # use the coords to determine the center of the face
            (x, y, w, h) = rects[0]
            faceX = int(x + (w/2.0))
            faceY = int(y + (h/2.0))

            #return the center of (x,y)-coords of the face
            return ((faceX, faceY), rects[0])

        #no faces found so return center of frame:
        return (frameCenter, None)
