import time
from pyfirmata2 import ArduinoMega

# Define the port where Arduino is connected
port = 'COM8'  # Replace with your port

# Establish a connection with the Arduino
board = ArduinoMega(port)

# Set up the pin modes
motorPin1 = board.get_pin('d:13:p')
motorPin2 = board.get_pin('d:12:p')

######################################################################################################################## Test value
distance = 5
########################################################################################################################

# Take in desired distance and iterate till covered individually for each wheel
def motorControl(distance):

    # establish needed variables
    dist1 = distance
    dist2 = distance

    dutyCycle1 = 50
    dutyCycle2 = 50

    direction1 = 1
    direction2 = 1

    maxSpeed1 = 49 # max duty cycle in either direction

    distConvertion = 1 # convert encoder velocity into realworld foot per loop

    acceleration = 1 # Duty cycle gain per loop

    While abs(dist2) < distance and abs(dist1) < distance:

        # Account for negative travel direction
        if dist1 < 0:
            direction1 = -1
        else:
            direction1 = 1
        if dist2 < 0:
            direction2 = -1
        else:
            direction2 = 1

        # Setup motor incremental acceleration if in terms of duty Cycle. Can replace with PID if needed
        if dutyCycle1 < maxSpeed and dist1 > 2*dutyCycle1*distConvertion:
            dutyCycle1 += acceleration*direction1
        elif dist1 <= 2*dutyCycle1*distConvertion:
            DutyCycle1 -= acceleration*direction1
        if dutyCycle2 < maxSpeed and dist2 > 2*dutyCycle2*distConvertion:
            dutyCycle2 += acceleration*direction2
        elif dist2 <= 2*dutyCycle2*distConvertion:
            DutyCycle2 -= acceleration*direction2

        # Use duty cycle to set pulse length
        max = .0018
        min = .0002
        rev = ((max - min) * (DutyCycle1 / 100)) + (min)

        max = .0018
        min = .0002
        rev = ((max - min) * (DutyCycle2 / 100)) + (min)

        # Run motor 1 for one pulse
        motorPin1.write(1)
        time.sleep(rev)
        motorPin1.write(0)

        # Run motor 2 for one pulse
        motorPin2.write(1)
        time.sleep(rev)
        motorPin2.write(0)

        # send minimum low signal
        time.sleep(.0005)

        # increment distance covered by each wheel. need correct code for reading encoder
        distanceTravled1 = enc.read * distance
        conversion
        distanceTravled2 = enc.read * distance
        conversion
        dist1 = dist1 - distanceTravled1
        dist2 = dist2 - distanceTravled2

motorControl(10)
