import time
import pigpio

servoPin = (23,24)

pi = pigpio.pi()
pi.set_mode(servoPin[0], pigpio.OUTPUT)
pi.set_mode(servoPin[1], pigpio.OUTPUT)
pigpio.exceptions = True
time.sleep(0.3)


pi.set_servo_pulsewidth(servoPin[0], 0)
pi.set_servo_pulsewidth(servoPin[1], 0)

#pi.close()
