
from pyfirmata2 import ArduinoMega
import time

###EW motor setup###
port = 'COM8'  # Replace with your port
# Establish a connection with the Arduino
board = ArduinoMega(port)
# Set up the pin modes
motorPin1 = board.get_pin('d:13:p')
motorPin2 = board.get_pin('d:12:p')

###Set Up Positioning###
current_position_EW = 0

def simple_E_W_Control(distance, direction): #imput your distance in inches and your direction: 1 (forward) or 0 (backward)

    time_per_revolution = 1.00
    distance_per_revolution = 6.908 #acounts for the 1:5 gear reduction and the 11" tire

    max = .0018 #max pulse width
    min = .0005 #min pulse width

    balance_left_1 = 1.00 #use to resolve minor variations in spin speed between the two motors
    balance_right_2 = .93

    if direction == 0: # determining direction and speed for each motor NOTE: ONE MOTOR IS WIRED WITH FLIPPED POLARITY TO ACHIEVE OPPISITE DRIVE DIRECTIONS
        DutyCycleR = 1
        DutyCycleL = 1
    elif direction == 1:
        DutyCycleR = 70*balance_right_2
        DutyCycleL = 70*balance_left_1

    k = ((max - min) * (DutyCycleR / 100)) + (min)
    q = ((max - min) * (DutyCycleL / 100)) + (min)

    timeout = time.time() + time_per_revolution*((distance/distance_per_revolution)) # DEFINE DISTANCE BY TIME AND SPEED

    while True: # contains manual pwm drive

        motorPin2.write(1)  # motor high pulse edge
        time.sleep(q)  # Delay for predefined pulse width in seconds
        motorPin2.write(0)  # motor low pulse edge
        time.sleep(.0005)  # Delay for 1 second

        motorPin1.write(1)  # motor high pulse edge
        time.sleep(k)  # Delay for predefined pulse width in seconds
        motorPin1.write(0)  # motor low pulse edge
        time.sleep(.005)  # Delay for 1 second

        if time.time()>= timeout: #EXIT CONDITION BASED ON TIME ELAPSED SINCE FUNCTION CALLED
            break


simple_E_W_Control(1000,1)
