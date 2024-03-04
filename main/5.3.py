import time
import RPi.GPIO as GPIO


print("Setup") #informs user setup has begun

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT) #sets GPIO pin 25 as an output
pin = GPIO.PWM(25,50) #set pin 25 as a PWM output, with a frequency of 50 Hz
pin.start(50) #sets the starting duty cycle of the PWM signal to 50%
time.sleep(1)

print("Begin") #informs user the main function of the program is beginning


try:
    while (True):
        pin.ChangeFrequency(200) #change the frequency to 200Hz
        time.sleep(1)
        pin.ChangeFrequency(400) #change the frequency to 400Hz
        time.sleep(1)
        pin.ChangeFrequency(600) #change the frequency to 600Hz
        time.sleep(1)
        pin.ChangeFrequency(800) #change the frequency to 800Hz
        time.sleep(1)
        pin.ChangeFrequency(1000) #change frequency to 1000Hz
        time.sleep(1)
        
except KeyboardInterrupt:
    pass



pin.stop()
GPIO.cleanup()

print("Done")