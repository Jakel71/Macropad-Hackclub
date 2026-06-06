import board
import digitalio
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

import neopixel


# -----------------------
# KEYBOARD SETUP
# -----------------------
kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

# -----------------------
# RGB LED SETUP (16x SK6812 Mini on A2/GPIO28)
# -----------------------
pixel = neopixel.NeoPixel(board.A2, 16, brightness=0.2, auto_write=False)

# All LEDS are red = not ready
for i in range(16):
    pixel[i] = (255, 0, 0)
pixel.show()

# -----------------------
# MATRIX SETUP (4x4)
# -----------------------
# 
# ROWS (right side, Pins 8-11):
#   Pin 8  = GPIO1/RX    = board.RX  oder board.D1
#   Pin 9  = GPIO2/SCK   = board.SCK oder board.D2  
#   Pin 10 = GPIO4/MISO  = board.MISO oder board.D4
#   Pin 11 = GPIO3/MOSI  = board.MOSI oder board.D3
#
# COLUMNS (left side, Pins 4-7):
#   Pin 7 = GPIO0/TX   = board.TX  oder board.D0
#   Pin 6 = GPIO7/SCL  = board.SCL oder board.D7
#   Pin 5 = GPIO6/SDA  = board.SDA oder board.D6
#   Pin 4 = GPIO29/A3  = board.A3
#
# LEDs are on A2 (Pin 3)

row_pins = [board.RX, board.SCK, board.MISO, board.MOSI]  # Pins 8,9,10,11
col_pins = [board.A3, board.SDA, board.SCL, board.TX]     # Pins 4,5,6,7

# Setup Rows as Output (HIGH = deactivated)
rows = []
for pin in row_pins:
    row = digitalio.DigitalInOut(pin)
    row.direction = digitalio.Direction.OUTPUT
    row.value = True  # HIGH = inaktiv
    rows.append(row)

# Setup Columns as Input with Pull-Up
cols = []
for pin in col_pins:
    col = digitalio.DigitalInOut(pin)
    col.direction = digitalio.Direction.INPUT
    col.pull = digitalio.Pull.UP
    cols.append(col)

# -----------------------
# MACRO FUNKTIONS
# -----------------------
def send_macro(keys, modifiers=[]):
    """Sendet eine Tastenkombination"""
    for mod in modifiers:
        kbd.press(mod)
    time.sleep(0.01)
    
    for key in keys:
        kbd.press(key)
        time.sleep(0.01)
        kbd.release(key)
        time.sleep(0.01)
    
    for mod in modifiers:
        kbd.release(mod)

# -----------------------
# KEYMAP DEFINITION
# -----------------------
def key_0():  # Taste 1 // Rickroll
    send_macro([Keycode.R], [Keycode.GUI])  # WIN+R
    time.sleep(0.1)
    layout.write('cmd\n')
    time.sleep(1)
    layout.write('curl ASCII.live&can/zou/hear/me\n')

def key_1():  # Taste 2
    send_macro([Keycode.L], [Keycode.GUI])  # WIN+L // lock screen

def key_2():  # Taste 3
    send_macro([Keycode.F4], [Keycode.ALT])  # ALT+F4 //end current window

def key_3():  # Taste 4
    send_macro([Keycode.D], [Keycode.GUI])  # WIN+D // show desktop

def key_4():  # Taste 5
    send_macro([Keycode.TAB], [Keycode.ALT])  # ALT+TAB // switch window

def key_5():  # Taste 6
    send_macro([Keycode.P], [Keycode.GUI])  # WIN+P // monitor settings

def key_6():  # Taste 7
    send_macro([Keycode.E], [Keycode.GUI])  # WIN+E // open file explorer

def key_7():  # Taste 8
    send_macro([Keycode.LEFT_SHIFT],[Keycode.LEFT_CONTROL], [Keycode.ESCAPE])  # open Taskmanager with STRG+SHIFT+ESC

def key_8():  # Taste 9
    send_macro([Keycode.S], [Keycode.GUI, Keycode.SHIFT])  # WIN+SHIFT+S // Screenshot

def key_9():  # Taste 10
    send_macro([Keycode.I], [Keycode.GUI])  # WIN+I // open settings

def key_10():  # Taste 11
    send_macro([Keycode.K], [Keycode.GUI])  # WIN+K // open connect menu for wireless displays

def key_11():  # Taste 12
    send_macro([Keycode.R], [Keycode.GUI])  # WIN+R // open run dialog

def key_12():  # Taste 13 - Media Play/Pause
    cc.send(ConsumerControlCode.PLAY_PAUSE)

def key_13():  # Taste 14 - Mute
    cc.send(ConsumerControlCode.MUTE)

def key_14():  # Taste 15 - Volume Down
    cc.send(ConsumerControlCode.VOLUME_DECREMENT)

def key_15():  # Taste 16 - Volume Up
    cc.send(ConsumerControlCode.VOLUME_INCREMENT)

# Keymap Array
keymap = [
    [key_0,  key_1,  key_2,  key_3],
    [key_4,  key_5,  key_6,  key_7],
    [key_8,  key_9,  key_10, key_11],
    [key_12, key_13, key_14, key_15]
]

# -----------------------
# LED COLORS
# -----------------------
COLOR_IDLE = (0, 50, 255)      # Blau - Idle
COLOR_PRESSED = (0, 255, 0)    # Grün - Gedrückt

# -----------------------
# DEBOUNCE & STATE
# -----------------------
last_state = [[False for _ in range(4)] for _ in range(4)]
debounce_time = 0.02

# -----------------------
# MAIN LOOP
# -----------------------
print("=== 4x4 Macropad gestartet ===")
print("Rows: RX, SCK, MISO, MOSI (Pins 8-11)")
print("Cols: A3, SDA, SCL, TX (Pins 4,5,6,7)")
print("LEDs: A2 (Pin 3)")

# All LEDS on Blue = ready
for i in range(16):
    pixel[i] = COLOR_IDLE
pixel.show()

while True:
    # Scann Matrix
    for row_idx, row in enumerate(rows):
        # Active Row (LOW = activ)
        row.value = False
        time.sleep(0.005)  # 5ms Debounce
        
        # read Columns
        for col_idx, col in enumerate(cols):
            current_state = not col.value  # inverted for pull-up
            
            # calculate LED Index (left to right)
            led_idx = row_idx * 4 + col_idx
            
            # Check for state change
            if current_state != last_state[row_idx][col_idx]:
                if current_state:  # Taste gedrückt
                    print(f"Taste {led_idx + 1} gedrückt")
                    
                    # LED green
                    pixel[led_idx] = COLOR_PRESSED
                    pixel.show()
                    
                    # do action
                    keymap[row_idx][col_idx]()
                    
                    time.sleep(debounce_time)
                    
                else:  # button no longer pressed
                    # LED back to blue
                    pixel[led_idx] = COLOR_IDLE
                    pixel.show()
                
                last_state[row_idx][col_idx] = current_state
        
        # Deactivate Row (HIGH = inactiv)
        row.value = True
        time.sleep(0.001)  # 1ms Pause between Rows
    
    time.sleep(1)  # 10ms Pause between Scans