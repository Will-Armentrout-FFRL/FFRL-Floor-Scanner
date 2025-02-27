import time
import serial
from pyfirmata2 import ArduinoMega
import tkinter as tk
import customtkinter
import math

### constants and conversions ###

### general and floor constants ###
floor_length_EW = 86.00 #in feet
floor_width_NS = 44.00 # in feet
scan_height = 9.43 # in inches
break_time = 2 #  in secconds

### N-S specific conversions ###
move_speed = 10.00 # RPSRee
scan_speed = 1.00 # RPS
steps_per_foot = 46150.00
steps_per_inch = steps_per_foot/12
steps_per_revolution = 2500
distance_per_revolution = 6.5
roller_diameter = 2

### E-W specific conversions ###
time_per_revolution = 1.00
distance_per_revolution_EW = 6.908

###NS motor setup###
ser = serial.Serial("COM4", 9600) #replace the com10 with the port that the compumotor is plugged into

###EW motor setup###
port = 'COM8'  # Replace with your arduino's port
# Establish a connection with the Arduino
board = ArduinoMega(port)
# Set up the pin modes
motorPin1 = board.get_pin('d:13:p')
motorPin2 = board.get_pin('d:12:p')

###Set Up Positioning###
current_position_EW = 0
current_position_NS = 0


def simple_E_W_Control(distance, direction): #imput your distance in inches and your direction: 1 (forward) or 0 (backward)

    max = .0018 #max pulse width
    min = .0005 #min pulse width

    balance_left_1 = 1.00 #use to resolve minor variations in spin speed between the two motors
    balance_right_2 = .93

    if direction == 0: # determining direction and speed for each motor NOTE: ONE MOTOR IS WIRED WITH FLIPPED POLARITY TO ACHIEVE OPPISITE DRIVE DIRECTIONS
        DutyCycleR = 1*balance_right_2
        DutyCycleL = 1*balance_left_1
    elif direction == 1:
        DutyCycleR = 70*balance_right_2
        DutyCycleL = 70*balance_left_1

    k = ((max - min) * (DutyCycleR / 100)) + (min)#kinda redundant but there in case you cant swap a motor's polarity
    q = ((max - min) * (DutyCycleL / 100)) + (min)

    timeout = time.time() + time_per_revolution*((distance/distance_per_revolution_EW)) # DEFINE DISTANCE BY TIME AND SPEED

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

#basic north-south relative move control function
def simple_N_S_Control(distance, direction, velocity): #distance is in feet, direction is 1(forward)/0(backwards), and velocity is in RPM
    if direction == 1:
        commands = ["MN", "LD3", "A10", "V"+str(velocity), "D"+str(int(distance)*int(steps_per_foot)), "G"] #simple relative movement command

    elif direction == 0:
        commands = ["MN", "LD3", "A10", "V"+str(velocity), "D"+str(distance*steps_per_foot), "H", "G"] # same command but with the reverse code

    for cmd in commands:
        ser.write((cmd + '\r\n').encode()) #inputs need to be on new lines/returned
        # print(f"Sent command: {cmd}")
        time.sleep(0.05)
#basic east west absolute go to position function
def move_to_position_EW(target_position_EW):#position in feet
    global current_position_EW
    distance_to_move_EW = target_position_EW-current_position_EW
    if distance_to_move_EW > 0:
        bearing = 1
    elif distance_to_move_EW < 0:
        bearing = 0
    elif distance_to_move_EW == 0:
        print("position met :) ")
    simple_E_W_Control(abs(distance_to_move_EW),bearing)
    print(f"moving E-W Motor from {current_position_EW} to {target_position_EW} by {distance_to_move_EW} ")
    current_position_EW = target_position_EW
#basic north-south absolute go to position function
def move_to_position_NS(target_position_NS):
    global current_position_NS
    distance_to_move_NS = target_position_NS-current_position_NS
    if distance_to_move_NS > 0:
        direction = 1
    elif distance_to_move_NS < 0:
        direction = 0
    elif distance_to_move_NS == 0:
        print("position met :) ")
    simple_N_S_Control(abs(distance_to_move_NS),direction,move_speed)
    print(f"moving N-S Motor from {current_position_NS} to {target_position_NS} by {distance_to_move_NS} ")
    current_position_NS = target_position_NS
#basic north-south absolute go to position function, but slower
def scan_to_position_NS(target_position_NS):
    global current_position_NS
    distance_to_move_NS = target_position_NS-current_position_NS
    if distance_to_move_NS > 0:
        heading = 1
    elif distance_to_move_NS <= 0:
        heading = 0
    simple_N_S_Control(abs(distance_to_move_NS),heading,scan_speed)
    print(f"moving N-S Motor from {current_position_NS} to {target_position_NS} by {distance_to_move_NS} ")
    current_position_NS = target_position_NS

### hardcoded scan programs ###
#go to zero zero
def home():
    move_to_position_EW(0)
    move_to_position_NS(0)
#do a single pass across one line of the flat floor
def single_scan():
    print ("Single Pass Selected")
    print ("Executing")
    scan_to_position_NS(floor_width_NS)
#do a single massive scan to be parsed seperateley using a snake pattern
def full_scan():
    print("Full Scan Selected")
    print("Executing")
    scan_pos = []
    indexer = 0.00
    while (floor_length_EW* 12)-indexer>0: # ensures that the index wont drive the gantry off the end of the floor x_X
        scan_pos.append(indexer) #appends current index to the list
        indexer=indexer+scan_height #itterates by scan height

    snake_index = 0 # index to identify even and odd passes and thereby side of floor and subsequent travel direction
    for i in scan_pos:
        if snake_index % 2 == 0: # starting from the left side
            scan_to_position_NS(floor_width_NS) # scan to the right edge of the floor
        elif snake_index % 2 != 0:
            scan_to_position_NS(0)

        time.sleep(break_time+(floor_width_NS*12/(scan_speed*distance_per_revolution)))

        move_to_position_EW(scan_pos[snake_index+1])
        time.sleep(break_time+(scan_height/move_speed))

        snake_index = snake_index+1

    print("Scan Path Completed")

def on_rectangle_click(event, canvas_width, canvas_height, rect_width, rect_height):
    x = int (((event.x / canvas_width) * rect_width))
    y = int((1-(event.y / canvas_height)) * rect_height)

    print(f"Select Target Point: ({x},{y})")
    move_to_position_EW(y)
    move_to_position_NS(x)

def main():

    root = customtkinter.CTk()
    root.title("Motor Control GUI")

    #dimensions for the rectangle

    rect_width = tk.IntVar(value = 100)
    rect_height = tk.IntVar(value = 100)

    def update_canvas():
        #draw rectangle
        canvas.delete("all")
        canvas.create_rectangle(0,0, canvas_width, canvas_height, outline = "black", fill = "black")
        label_info.config(text = f"Rectangle: {rect_width.get()} x {rect_height.get()}")

    #define the aformentioned canvas
    canvas_width = 400
    canvas_height = 400

    canvas = tk.Canvas(root, width = canvas_width, height = canvas_height, bg= "black")
    canvas.pack()

    #draw rectangle
    canvas.create_rectangle(0,0, canvas_width, canvas_height, outline= "black", fill = "black")

    #add user controls
    control_frame = tk.Frame(root)
    control_frame.pack()

    tk.Label(control_frame, text = "width:").pack(side = tk.LEFT)
    tk.Entry(control_frame, textvariable = rect_width, width =20).pack(side = tk.LEFT)

    tk.Label(control_frame, text="height:").pack(side=tk.LEFT)
    tk.Entry(control_frame, textvariable=rect_height, width=20).pack(side=tk.LEFT)

    tk.Button(control_frame, text = "update dimensions", command=update_canvas).pack(side = tk.LEFT)

    label_info = tk.Label(root, text = f"rectangle: {rect_width.get()} x {rect_height.get()}")
    label_info.pack()

    tk.Button(root, text="Home", command=home).pack()

    program_var = tk.StringVar(root)
    program_var.set("select Scan Program")

    programs_frame = tk.Frame(root)
    programs_frame.pack()

    tk.Label(programs_frame, text= "Programs").pack(side = tk.LEFT)
    program_menu = tk.OptionMenu(programs_frame, program_var, "Single Scan", "Full Scan")
    program_menu.pack(side = tk.LEFT)

    def execute_program():
        selected_program = program_var.get()

        if selected_program == "Single Scan":
            single_scan()
        elif selected_program == "Full Scan":
            full_scan()

    tk.Button(programs_frame,text = "run", command = execute_program).pack(side = tk.LEFT)

    canvas.bind("<Button-1>", lambda event: on_rectangle_click(event, canvas_width, canvas_height, rect_width.get(), rect_height.get()))

    root.mainloop()

if __name__ == "__main__":
    main()
