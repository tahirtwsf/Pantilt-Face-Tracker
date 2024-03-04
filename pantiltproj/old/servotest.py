import RPi.GPIO as GPIO
from time import sleep
import random
from multiprocessing import Manager
from multiprocessing import Process

pan = 7
tilt = 12


#Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(pan, GPIO.OUT)
GPIO.setup(tilt, GPIO.OUT)
p = GPIO.PWM(pan, 50)
t = GPIO.PWM(tilt, 50)

def setAngle(servo, angle):
    assert angle >= 30 and angle <= 150
    pwm = GPIO.PWM(servo, 50)
    pwm.start(8)
    dutyCycle = angle / 12. + 3. # 12. = 12.0 , python realizes it's a float.
    pwm.ChangeDutyCycle(dutyCycle)
    sleep(0.3)
    pwm.stop()


if __name__ == '__main__':
    
    for i in range (30, 160, 15):
        setAngle(pan, i)
        # setAngle(tilt, i)

    for i in range (150, 30, -15):
        setAngle(pan, i)
        # setAngle(tilt, i)

    setAngle(pan, 100)
    setAngle(tilt, 90)
    GPIO.cleanup()






