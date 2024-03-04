import time
import RPi.GPIO as GPIO


print("Setup") #informs user setup has begun

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT) #sets GPIO pin 25 as an output
pin = GPIO.PWM(25,50) #set pin 25 as a PWM output, with a frequency of 50 Hz
pin.start(0) #sets the starting duty cycle of the PWM signal to 0%
time.sleep(1)

print("Begin") #informs user the main function of the program is beginning


try:
    while (True):
        pin.ChangeDutyCycle(0) #change the duty cycle to 0%
        time.sleep(1)
        pin.ChangeDutyCycle(20) #change the duty cycle to 20%
        time.sleep(1)
        pin.ChangeDutyCycle(40) #change the duty cycle to 40%
        time.sleep(1)
        pin.ChangeDutyCycle(60) #change the duty cycle to 60%
        time.sleep(1)
        pin.ChangeDutyCycle(80) #change the duty cycle to 80%
        time.sleep(1)
        pin.ChangeDutyCycle(100) #change the duty cycle to 100%
        time.sleep(1)
except KeyboardInterrupt:
    pass



pin.stop()
GPIO.cleanup()

print("Done")
