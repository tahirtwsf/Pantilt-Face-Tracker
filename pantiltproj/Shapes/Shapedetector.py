import cv2
from imutils import resize


class ShapeDetector:
    def __init__(self, c):
        peri = cv2.arcLength(c, True)
        self.detector = cv2.approxPolyDP(c, 0.04 * peri, True)
        pass
    
    def detect(self):

        shape = "unidentified"
        # peri = cv2.arcLength(c, True)
        # approx = cv2.approxPolyDP(c, 0.04 * peri, True)

        if len(self.detector) == 3:
            shape = ""
            
        elif len(self.detector) == 4:
            # draw the boundary box to find out whether this is square or rectangle
            (x, y, w, h) = cv2.boundingRect(self.detector)
            ar =  w / float(h)

            shape = "" if ar >= 0.90 and ar < 1.05 else "rectangle"
            
        elif len(self.detector) == 5:
            shape = ""

        #elif len(self.detector) > 18:
        #    shape = ""
            
        else:
            (x, y, w, h) = cv2.boundingRect(self.detector)
            ar = w / float(h)
            shape = "circle" if ar >= 0.90 and ar < 1.05 else "elipse"
            
            
        return (shape)


    def update(self, frame, frameCenter):
        #check to see if a face was found
        if len(self.detector) > 0:
            #extract the bounding box coords of the face and
            # use the coords to determine the center of the face
            (x, y, w, h) = cv2.boundingRect(self.detector)
            faceX = int(x + (w/2.0))
            faceY = int(y + (h/2.0))
            
            #return the center of (x,y)-coords of the shape
            return ((faceX, faceY), cv2.boundingRect(self.detector))

        #no shapes found so return center of frame:
        return (frameCenter, None)
        

   
        
    
