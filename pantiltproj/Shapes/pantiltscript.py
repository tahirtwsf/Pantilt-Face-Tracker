#Imports
from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from imutils import resize
from imutils import grab_contours
from facetracker import ObjCenter
from PIDcontroller import PID
from Shapedetector import ShapeDetector
import argparse
import signal
import time
import sys
import cv2
import pigpio

# Wanted to warn that this script is over commented, and most of the comments will be pointless to the student, I'm putting them here so that
# those who want to know everything that is going on in the script can find out easily.


# Define the range for the motors and for convenience which GPIO pins are in use (GPIO label, panning servo first.).
servoRange = (-90, 90)
servoPin = (18,4)

# Purpose is to exit the script if necessary, but since this script uses references to multiple different classes, all running
# as processes at once (meaning we are running 4 things at once to track faces) and we need to close all of them at once.

def signal_handler(sig, frame):
    print("[INFO] 'ctrl + c' pressed, stopping.")

    pi.set_servo_pulsewidth(servoPin[0], 0)
    pi.set_servo_pulsewidth(servoPin[1], 0)
    
    #exit the program
    sys.exit()



# Servos work by recieving PWM (pulse width modulation) signals and repositioning according to their dutycycle. So this function can take an integer "servo"
# as the pin number you attached the servo to (declared above), and an angle (determined later). Using the pigpio python library it converts the angle
# to a dutycycle that the servo can then act on.

def move_servo(servo, angle):
    
    try:
        
        pi.set_servo_pulsewidth(servo, 1400 + angle * 10)
        time.sleep(0.2)
        
    except:
        print("Servos not working.")


def obj_center(args, objX, objY, centerX, centerY):
    
    # Uses the signal_handler to stop the program when a keyboard interrupt is made (ctrl + c in terminal)
    signal.signal(signal.SIGINT, signal_handler)

    # Start the video stream and wait for the camera to warm up
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)

    while True:

        image = vs.read()
        image = cv2.flip(image, 0)
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 5)
        thresh = cv2.threshold(blurred, 60, 240, cv2.THRESH_BINARY)[1]
        
        # Uncomment this if you want to switch from detecting dark things to detecting bright things.
        # thresh = cv2.bitwise_not(thresh) 


        # Draw lines on the black and white image anywhere that white is.
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = grab_contours(cnts)
        (H, W) = image.shape[:2]
        centerX.value = W // 2
        centerY.value = H // 2

        for c in cnts:
            
            # find center and detect name of shape using contours
            M = cv2.moments(c)
            sd = ShapeDetector(c)

            # uses M to find the center of the object
            if M["m00"] > 0:
                temp1 = int((M["m10"] / M["m00"]))
                temp2 = int((M["m01"] / M["m00"]))
                
                # "What shape is this?"
                shape = sd.detect()

                # THIS IS AN IMPORTANT LINE. this controls which shape is being looked for.
                if shape == "circle" or shape == "square":
                    objX.value = temp1
                    objY.value = temp2

                    
                cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                cv2.putText(image, shape, (temp1, temp2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)


                objLoc = sd.update(image, (centerX.value, centerY.value)) 
                ((objX.value, objY.value), rect) = objLoc                                                                           

                    
        #show output image
        cv2.imshow('Image',image)

        # uncomment this if the results are confusing, it shows what the program "sees"
        # cv2.imshow('Thresh', thresh) 

        cv2.waitKey(1)


# This function handles what is called the PID controller script, which the student will be tuning,
# The tuning however happens far below this block, which simply passes values to the other script.

def pid_process(output, p, i, d, objCoord, centerCoord):
    # Signal trap
    signal.signal(signal.SIGINT, signal_handler) #Signal

    # Create a PID object (using the PIDcontroller.py script and initialize it with parameters p, i, and d.
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
        panAngle = -1 * pan.value
        tiltAngle = -1 * tlt.value
        
        # If the pan angle is within the range defined at the top of the script, use the convert_angle function to move towards it.
        if in_range(panAngle, servoRange[0], servoRange[1]):
            try:
                move_servo(servoPin[0], panAngle)

            except:
                print ("panning servo out of range.")


        # If the tilt angle is within the range defined at the top of the script, use the convert_angle function to move towards it.
        if in_range(tiltAngle, servoRange[0], servoRange[1]):
            try:
                move_servo(servoPin[1], tiltAngle)
                
            except:
                print("tilting servo out of range.")
 

# Check if this is the main body of execution if so, we get to actually start doing stuff.

if __name__ == "__main__":

    # for args later in processes.
    ap = argparse.ArgumentParser()
    args = vars(ap.parse_args())


    # Start a manager for process-safe variables, this manager allows us to share values between different simultaneous processes, so the process
    # finding the center of a face can pass that value to the PID controller to find error which can pass that value over move the servos in both
    # the panning process and the tilting process.
    
    with Manager() as manager:

        try:

            # This block sets up the GPIO pins to be used as output.
            pi = pigpio.pi()
            pi.set_mode(servoPin[0], pigpio.OUTPUT)
            pi.set_mode(servoPin[1], pigpio.OUTPUT)
            pigpio.exceptions = True
            time.sleep(0.3)
            
        except:
            print("Could not initialize servos.")  # Error message to tell you if something went wrong ons startup.


        
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
        panP = manager.Value("f", 0.07) 
        panI = manager.Value("f", 0.05)
        panD = manager.Value("f", 0.002)

        # PID values for tilting
        tiltP = manager.Value("f", 0.07) 
        tiltI = manager.Value("f", 0.05)
        tiltD = manager.Value("f", 0.002)



        # Declare processes for everything that needs to happen, first passing in the target function to use from above,
        # and passing in the values from the Manager as arguments for the functions. This way the processes can act on them at the same time.
    
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

