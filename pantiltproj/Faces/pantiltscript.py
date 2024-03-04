#Imports
from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from facetracker import ObjCenter
from PIDcontroller import PID
import pantilthat as pth
import argparse
import signal
import time
import sys
import cv2
import pigpio


# Define the range for the servos and for convenience which GPIO pins are in use (GPIO label, panning servo first.).
servoRange = (-90, 90)

# Purpose is to exit the script if necessary, but since this script uses references to multiple different classes, and multiple
# processes running at once (meaning we are running 4 things at once to track faces) and we need to close all of them at once. so we
# call this function in each process.

def signal_handler(sig, frame):
    print("[INFO] 'ctrl + c' pressed, stopping.")
    
    #exit the program
    sys.exit()


# Calls the facetracker script to find the center of an object.

def obj_center(args, objX, objY, centerX, centerY):
    
    # Uses the signal_handler to stop the program when a keyboard interrupt is made (ctrl + c in terminal)
    signal.signal(signal.SIGINT, signal_handler)

    # Start the video stream and wait for the camera to warm up
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)

    # Initialize the facetracker to report the center of any face on screen
    obj = ObjCenter(args["cascade"])


    while True:
        
        # Grab the frame from the threaded video stream and flip it vertically (since our camera is by default upside down)
        frame = vs.read()
        frame = cv2.flip(frame,0)

        # Calculate the center of the frame as this is where we will try to keep the face.
        (H, W) = frame.shape[:2]
        centerX.value = W // 2
        centerY.value = H // 2

        # Find the object's location
        objectLoc = obj.update(frame, (centerX.value, centerY.value))
        ((objX.value, objY.value), rect) = objectLoc

        # Draw a box around the location.
        if rect is not None:
            (x, y, w, h) = rect
            cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 2)

        # Display the frame to the screen, will create a window named "Pan-Tilt Tracker".
        cv2.imshow("Pan-Tilt Tracker", frame)
        cv2.waitKey(1)


# This function handles what is called the PID controller script, which the student will be tuning,
# The actual tuning however happens far below this block, which simply passes values to the other script, or in the movement function.

def pid_process(output, p, i, d, objCoord, centerCoord):
    # Signal trap
    signal.signal(signal.SIGINT, signal_handler) #Signal

    # Create a PID object (using the PIDcontroller.py script) and initialize it with parameters p, i, and d.
    p = PID(p.value, i.value, d.value)
    p.initialize()

    while True:
        
        # Find the exact error between face center and center of screen, then update the value of error for all processes.
        error = centerCoord.value - objCoord.value
        output.value = p.update(error)


# A quick function to compare 1 number to a range of numbers.

def in_range(val, start, end):
    return (val >= start and val <= end)


# This is where the servos are actually told to move, using pan and tilt angles determined by error calculations in the PIDcontroller
# and the angle_converter.

def set_servos(pan, tlt):
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        
        # The pan and tilt angles are the reverse of the values generated due to the camera being upside down by default.
        # If the servo in use is able to keep the camera right-side-up just remove the -1 from these lines.
        panAngle = (-1) * pan.value
        tiltAngle = (-1) * tlt.value
        
        
        # If the pan angle is within the range defined at the top of the script, use the convert_angle function to move towards it.
        if in_range(panAngle, servoRange[0], servoRange[1]):
            try:
                pth.pan(panAngle)
                #print(panAngle)
            except:
                print ("Could not move the panning servo.")


        # If the tilt angle is within the range defined at the top of the script, use the convert_angle function to move towards it.
        if in_range(tiltAngle, servoRange[0], servoRange[1]):
            try:
                pth.tilt(tiltAngle)
                #print(tiltAngle)
            except:
                print("Could not move the tilting servo.")
 

# Check if this is the main body of execution if so, we get to actually start doing stuff.

if __name__ == "__main__":

    # This is for running the program from the terminal, allowing us to pass which haarcascade (the package that can actually detect objects)
    # we are using. We pass in "haarcascade_frontalface_default.xml" when running the program as it finds human faces from the front.
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--cascade", type=str, required=True,
                    help="haarcascade_frontalface_default.xml")
    args = vars(ap.parse_args())


    # Start a manager for process-safe variables, this manager allows us to share values between different simultaneous processes, so the process
    # finding the center of a face can pass that value to the PID controller to find error which can pass that value over to move the servos in both
    # the panning process and the tilting process.
    
    with Manager() as manager:


        
        # Set integer values for the object center (x, y)-coords
        centerX = manager.Value("i",0)
        centerY = manager.Value("i", 0)

        # Set integer values for the object's (x, y)-coords
        objX = manager.Value("i", 0)
        objY = manager.Value("i", 0)

        # Pan and tilt values will be managed by independent PIDs
        pan = manager.Value("i", 0)
        tlt = manager.Value("i", 0)

        # PID values for panning
        panP = manager.Value("f", 0.09) 
        panI = manager.Value("f", 0.08)
        panD = manager.Value("f", 0.002)

        # PID values for tilting
        tiltP = manager.Value("f", 0.11) 
        tiltI = manager.Value("f", 0.10)
        tiltD = manager.Value("f", 0.002)



        # Have to deal with four processes now, all at once.
        # objectCenter - find face and how far i it is from center
        # panning      - determines right X coords to pan to
        # tilting      - determines right Y coords to tilt to
        # setServos    - moves the servos


        # Declare processes for everything that needs to happen, first passing in the target function to use from above,
        # and passing in the values from the Manager as arguments for the functions. Now they all know which variables to act on together.
    
        processObjectCenter = Process(target=obj_center, args=(args, objX, objY, centerX, centerY))
        
        processPanning = Process(target=pid_process, args=(pan, panP, panI, panD, objX, centerX))
        
        processTilting = Process(target=pid_process, args=(tlt, tiltP, tiltI, tiltD, objY, centerY))
        
        processSetServos = Process(target=set_servos, args=(pan, tlt))


        # Start all 4 processes, I put each of these in an individual try-except statement so that if an error occurs the student
        # can see exactly what is not working.
        
        try:
            processObjectCenter.start()
            
        except:
            print("Failed to start the Object Center process.")
        
        try:
            processPanning.start()

        except:
            print("Failed to start the panning process.")
            
        try:
            processTilting.start()

        except:
            print("Failed to start the tilting process.")
            
        try:
            processSetServos.start()

        except:
            print("Failed to start the set servos process.")

            

        # Join all 4 processes so they happen together.
        try:
            processObjectCenter.join()

        except:
            print("Could not join Object Center")
            
        try:
            processPanning.join()
            

        except:
            print("Could not join Panning")

        try:
            processTilting.join()

        except:
            print("Could not join Tilting")

        try:
            processSetServos.join()
        
        except:
            print("Could not join Set Servos")

