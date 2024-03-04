#How to work with a segment segment display



#Library for the GPIO
import RPi.GPIO as GPIO
#Library to use timing
import time
#Turn any minor warnings off
GPIO.setwarnings(False)
#Setup the RaspPi to use the numbering on the board
GPIO.setmode(GPIO.BCM)



#Constants
timeConstant = 1; #Start delay with 1 second go down until miniscule

#Anode - letters correspond to schematic in datasheet MM74C925
GPIO.setup(11,GPIO.OUT); #d
GPIO.setup(0,GPIO.OUT); #c
GPIO.setup(5,GPIO.OUT); #e
GPIO.setup(6,GPIO.OUT); #b
GPIO.setup(13,GPIO.OUT); #f
GPIO.setup(19,GPIO.OUT); #a
GPIO.setup(26,GPIO.OUT); #g

#Common Cathode (Left to Right)
GPIO.setup(12,GPIO.OUT); #Green - First Digit - A
GPIO.setup(16,GPIO.OUT); #Blue - Second Digit - D
GPIO.setup(20,GPIO.OUT) #Red - Third Digit -B
GPIO.setup(21,GPIO.OUT) #Orange - Fourth Digit - C


#Functions defined for simpler calling
def turnAllOn():
    GPIO.output(11,GPIO.HIGH); 
    GPIO.output(0,GPIO.HIGH); 
    GPIO.output(5,GPIO.HIGH); 
    GPIO.output(6,GPIO.HIGH); 
    GPIO.output(13,GPIO.HIGH); 
    GPIO.output(19,GPIO.HIGH); 
    GPIO.output(26,GPIO.HIGH); 
    GPIO.output(12,GPIO.HIGH); 
    GPIO.output(16,GPIO.HIGH);
    GPIO.output(20,GPIO.HIGH);
    GPIO.output(21,GPIO.HIGH);

def reset():
    GPIO.output(11,GPIO.LOW); 
    GPIO.output(0,GPIO.LOW); 
    GPIO.output(5,GPIO.LOW); 
    GPIO.output(6,GPIO.LOW); 
    GPIO.output(13,GPIO.LOW); 
    GPIO.output(19,GPIO.LOW); 
    GPIO.output(26,GPIO.LOW); 
    GPIO.output(12,GPIO.LOW); 
    GPIO.output(16,GPIO.LOW);
    GPIO.output(20,GPIO.LOW);
    GPIO.output(21,GPIO.LOW);

def gndA():
    GPIO.output(12,GPIO.HIGH);

def gndB():
    GPIO.output(20,GPIO.HIGH);

def gndC():
    GPIO.output(21,GPIO.HIGH);

def gndD():
    GPIO.output(16,GPIO.HIGH);

def value1():
    GPIO.output(6,GPIO.HIGH); 
    GPIO.output(0,GPIO.HIGH); 

def value2():
    GPIO.output(19,GPIO.HIGH); 
    GPIO.output(6,GPIO.HIGH); 
    GPIO.output(26,GPIO.HIGH); 
    GPIO.output(5,GPIO.HIGH); 
    GPIO.output(11,GPIO.HIGH); 

def value3():
    GPIO.output(19,GPIO.HIGH); 
    GPIO.output(6,GPIO.HIGH);
    GPIO.output(26,GPIO.HIGH); 
    GPIO.output(0,GPIO.HIGH); 
    GPIO.output(11,GPIO.HIGH); 

#Use Crtl-C to exit program
try:
    while True:


        #Start with everything turned off
        reset();  
        gndB();
        value1();
        time.sleep(timeConstant);
        
        reset();
        gndC();
        value2();
        time.sleep(timeConstant);
        reset();

        reset();
        gndD();
        value3();
        time.sleep(timeConstant);
        
        if(timeConstant > 5/1000): #Reduce original time to 5ms
            timeConstant = timeConstant/1.5;

except KeyboardInterrupt:
    print ("Program has exited successfully");

except Exception as e:
    print("Unexpected error has occurred");
    print(e);
    
finally:
    #Resets the GPIO
    GPIO.cleanup()