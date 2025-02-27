import serial

# setup serial port and baud rate.

# comment various gcode commands used and their meaning

# Define veriables

tolerance = .5

revToDist = 1 # motor command converted to distance covered

dist = 0 # distance covered by motor

accelGain = 1 # acceleration gain in dist per loop
accel = 0

def toolHeadControler (NSDistance):

    while NSDistance-tolerance > dist and NSDistance+tolerance < dist:

        # send movement commands
        if dist < NSDistance and (NSDistance-dist) > accel*2:
            accel += accelGain
            serial.write accel # thing
        elif (NSDistance-dist) < accel*2:
            accel -= accelGain
            serial.write accel # thing
        else:
            serial.write accel

        # read encoder
        encRead =
        dist += revToDist*encRead
