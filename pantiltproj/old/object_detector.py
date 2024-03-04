import numpy as np
import argparse
import imutils
import time
import cv2
import os



# Arg parse time because we like long terminal commands i guess.
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help = "Path to input video.") # used for VideoCapture()
ap.add_argument("-o", "--output", required = True, help = "path to output directory.")
ap.add_argument("-y", "--yolo", required=True, help = "base path to YOLO directory.")
ap.add_argument("-c", "--confidence", type = float, default = 0.5,
   help = "minimum probability to filter weak detections")
ap.add_argument("-t", "--threshold", type = float, default = 0.3,
   help = "threshold when applying non-maxima suppression.")
args = vars(ap.parse_args())

# load the COCO class labels this model of YOLO was trained on.
labelsPath = os.path.sep.join( [args["yolo"], "coco.names"])
LABELS = open(labelsPath).read().strip().split("\n")

# initialize a list of colours to represent each possible class label
np.random.seed(42)
COLORS = np.random.randint(0. 255, size = ( len(LABELS), 3), dtype = "uint8")

# derive the paths to the YOLO weights and model configuration
weightsPath = os.path.sep.join([args["yolo"], "yolov3.weights"])
configPath = os.path.sep.join([args["yolo"], "yolov3.cfg"])

# load our YOLO object detector trainedo n COCO dataset (80 classes)
print("[INFO] loading YOLO. I know the name is cringey but I can't help that.")
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

# could re-use this block because of how the picamera works..
# image = cv2.imread(args["image"])
# (H, W) = image.shape[:2]

# determine only the output layer names required from YOLO
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]


vs = VideoCapture(args["input"]) # LAME.
writer = None # This could also be wrong due to picamera weirdness.
(W, H) = (None, None)

# try to determine the total number of frames in the video file
try:
   prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
       else cv2.CV_CAP_PROP_FRAME_COUNT
   total = int(vs.get(prop))
   print("[INFO] {} total frames in video".format(total))

# an error occurred while trying to determine the total number of frames in the video file
except:
   print("[INFO] could not determine # of frames in video")
   print("[INFO] no approx. completion time can be provided")
   total = -1


# loop over frames from the video file stream
while True:
   # read the next frame from the file
   (grabbed, frame) = vs.read()

   # if the frame wasn't grabbed then we have reached the end of the stream
   if not grabbed:
       break
  
   # if the frame dimensions are empty grab them
   if W is None or H is None:
       (H, W) = frame.shape[:2]


    # construct a blob from the input frame and then perform a forward pass of the YOLO object detector,
    # giving us our bounding boxes and associated probabilities

    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
        swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    end = time.time()
    # initialize our lists of detected bounding boxes, confidences, and class IDs, respectively

    boxes = []
    confidences = []
    classIDs = []

   # loop over each of the layers
   for output in layerOutputs:
       # loop over detections
       for detection in output:
           # extract the class ID and confidence of object detection
           scores = detection[5:]
           classID = np.argmax(scores)
           confidence = scores[classID]

           # filter out weak predictions using minimum probability
           if confidence > args["confidence"]:
               # scale bounding box coords back relative to size of image keeping in mind that YOLO returns
               # the center of the bounding box followed by the boxes' width and height
               box = detection[0:4] * np.array([W, H, W, H])
               (centerX, centerY, width, height) = box.astype("int")

               # use center coords to derive corners of bounding box
               x = int(centerX - (width / 2))
               y = int(centerY  -(height / 2))

               # update lists
               boxes.append([x, y, int(width), int(height)])
               confidence.append(float(confidence))
               classIDs.append(classID)

   # do the suppression
   idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"], args["threshold"])

   # ensure at least 1 detection
   if len(idxs) > 0:
       # loop over indexes kept
       for i in idxs.flatten():
           # extract box coords
           (x, y) = (boxes[i][0], boxes[i][1])
           (w, h) = (boxes[i][2], boxes[i][3])

           # draw a bounding box rectangle
           color = [int(c) for c in COLORS[classIDs[i]]]
           cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
           text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
           cv2.putText(frame, text, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
  
   if writer is None:
       # initialize video writer
       fourcc = cv2.VideoWriter_fourcc(*"MJPG")
       writer = cv2.VideoWriter(args["output"], fourcc, 30, (frame.shape[1], frame.shape[0]), True)

       # some info on processing single frame
       if total > 0:
           elap = (end - start)
           print("[INFO] single frame took {:.4f} seconds".format(elap))
           print("[INFO] estimated total time to finish: {:.4f}".format(elap * total))
       # write the output frame to disk
       writer.write(frame)
  
#  r e l e a s e     t h e     p o i n t e r s
print("[INFO] cleaning up...")
writer.release()
vs.release()


