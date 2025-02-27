import time
import serial

ser = serial.Serial("COM4", 9600)

steps_per_foot = 4615
steps_per_inch = steps_per_foot/12

def simple_N_S_Control(distance, direction, velocity): #distance is in inches, direction is 1(forward)/0(backwards), and velocity is in mm per second
    if direction == 1:
        commands = ["MC", "LD3", "A10", "V"+str(velocity), "D"+str(int(distance)*int(steps_per_inch)), "G"] #simple relative movement command
    elif direction == 0:
        commands = ["MC", "LD3", "A10", "V"+str(velocity), "D"+str(int(distance)*int(steps_per_inch)), "H", "G"] # same command but with the reverse code
    for cmd in commands:
        ser.write((cmd + '\r\n').encode()) #inputs need to be on new lines/returne
        # print(f"Sent command: {cmd}")
        time.sleep(0.05)

simple_N_S_Control(25000,1,1)

