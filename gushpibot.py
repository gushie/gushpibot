#!/usr/bin/python

import sys
import os
import time
import collections
import curses
from subprocess import call, Popen, PIPE
import RPi.GPIO as GPIO
try:
    # sudo apt-get install cwiid-python
    # Python 2 only :(
    import cwiid
    CWIID_AVAILABLE = True
except:
    CWIID_AVAILABLE = False
try:
    # sudo apt-get install git
    # git clone git://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
    import Adafruit_CharLCD
    ADAFRUITLCD_AVAILABLE = True
except:
    ADAFRUITLCD_AVAILABLE = False
try:
    # sudo apt-get install alsa-utils espeak mplayer python-pip
    # sudo pip install praw pyttsx
    import pyttsx
    TTSX_AVAILABLE = True
except:
    TTSX_AVAILABLE = False

#pocketsphinx for speech recognition
# ? http://cmusphinx.sourceforge.net/wiki/raspberrypi

BUTTONS_AVAILABLE = True
WII_AVAILABLE = CWIID_AVAILABLE
LCD_AVAILABLE = ADAFRUITLCD_AVAILABLE
WEBCAM_AVAILABLE = True
ECHO_AVAILABLE = True
SPEECH_AVAILABLE = TTSX_AVAILABLE
AUDIO_AVAILABLE = True

"""
Default GPIO PIN assigments (Model B revision 1)
---------------------------
 0 ECHO SEND
 1
 4 ECHO RETURN
 7 BUTTON MENU
 8 BUTTON SELECT
 9 LCD D4 (LCD pin 11)
10 LCD D5 (LCD pin 12)
11 LCD D7 (LCD pin 14)
14
15
17 MOTOR 1A
18 MOTOR 1B
21 LCD D6 (LCD pin 13)
22 MOTOR 2A
23 MOTOR 2B
24 LCD EN (LCD pin 6)
25 LCD RS (LCD pin 4)
"""

class Controller(object):
    """
    This class controls the menu and programming and operates the main event loop
    """
    def __init__(self):
        self.components = []
        self.active = True
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def startup(self):
        self.create_display()
        self.create_menu()
        self.create_wheels()
        self.create_program()
        if BUTTONS_AVAILABLE:
            self.create_buttons()
        if WEBCAM_AVAILABLE:
            self.create_webcam()
        if WII_AVAILABLE:
            self.create_wiimote()
        if ECHO_AVAILABLE:
            self.create_echo()
        if SPEECH_AVAILABLE:
            self.create_speech()
        if AUDIO_AVAILABLE:
            self.create_audio()
        self.create_keyboard()
        self.update_menu()
        self.display.display_at(1, 0, "Init complete")

    def add_component(self, text, component):
        self.components.append(component)
        self.display.display_at(1, 0, "Created " + text)

    def create_display(self):
        if LCD_AVAILABLE:
            self.display = LCDDisplay()
        else:
            self.display = ConsoleDisplay()
        self.display.display("GushPiBot...")
        self.display_ip()
        self.add_component("Display", self.display)

    def create_wheels(self):
        self.wheels = Wheels()
        self.add_component("Wheels", self.wheels)

    def create_program(self):
        self.command = 0
        self.program = Program(self.display)
        self.program.add_command("^", "Forward", self.wheels.forwards, self.wheels.stop)
        self.program.add_command("v", "Backward", self.wheels.backwards, self.wheels.stop)
        self.program.add_command("<", "Left", self.wheels.left, self.wheels.stop)
        self.program.add_command(">", "Right", self.wheels.right, self.wheels.stop)
        self.program.add_command("{", "Slow Left", self.wheels.slow_left, self.wheels.stop)
        self.program.add_command("}", "Slow Right", self.wheels.slow_right, self.wheels.stop)
        self.add_component("Program", self.program)

    def create_buttons(self):
        self.buttons = Buttons()
        self.buttons.handlers["MENU"].add(self.menu.next)
        self.buttons.handlers["SELECT"].add(self.menu.select)
        self.add_component("Buttons", self.buttons)

    def create_webcam(self):
        self.webcam = Webcam()
        self.program.add_command("#", "Photo", self.webcam.take_photo)
        self.add_component("Webcam", self.webcam)

    def create_wiimote(self):
        self.wiimote = Wiimote(self.display)
        self.wiimote.handlers["UP"].add(self.wheels.forwards)
        self.wiimote.handlers["DOWN"].add(self.wheels.backwards)
        # Yes, left and right transposed here, something is switched somewhere but haven't found out what yet
        self.wiimote.handlers["LEFT"].add(self.wheels.right)
        self.wiimote.handlers["RIGHT"].add(self.wheels.left)
        self.wiimote.handlers["A"].add(self.wheels.stop)
        try:
            self.wiimote.handlers["B"].add(self.webcam.take_photo)
        except AttributeError:
           pass
        self.wiimote.handlers["HOME"].add(self.menu.select)
        self.wiimote.handlers["MINUS"].add(self.menu.prev)
        self.wiimote.handlers["PLUS"].add(self.menu.next)
        self.wiimote.stop_handler = self.wheels.stop
        self.add_component("Wiimote", self.wiimote)

    def create_speech(self):
        self.speech = Speech()
        self.speech.speak("Hello. I am Gush Pi Bot.")
        self.wheels.speech_handler.add(self.speech.speak)
        self.add_component("Speech", self.speech)

    def create_audio(self):
        self.audio = Audio()
        self.add_component("Audio", self.audio)

    def create_echo(self):
        self.echo = Echo(self.display)
        self.echo.stop_handler.add(self.wheels.stop)
        self.add_component("Echo", self.echo)

    def create_keyboard(self):
        self.keyboard = Keyboard(self.display.stdscr)
        self.keyboard.handlers["UP"].add(self.wheels.forwards)
        self.keyboard.handlers["DOWN"].add(self.wheels.backwards)
        self.keyboard.handlers["LEFT"].add(self.wheels.left)
        self.keyboard.handlers["RIGHT"].add(self.wheels.right)
        self.keyboard.handlers["."].add(self.wheels.stop)
        self.keyboard.handlers["{"].add(self.wheels.slow_left)
        self.keyboard.handlers["}"].add(self.wheels.slow_right)
        self.keyboard.handlers["CTRL+X"].add(self.pi_shutdown)
        self.keyboard.handlers["PAGEDOWN"].add(self.menu.next)
        self.keyboard.handlers["PAGEUP"].add(self.menu.prev)
        self.keyboard.handlers["RETURN"].add(self.menu.select)
        self.keyboard.handlers["ESC"].add(self.exit)
        try:
            self.keyboard.handlers["#"].add(self.webcam.take_photo)
        except AttributeError:
            pass
        self.add_component("Keyboard", self.keyboard)

    def create_menu(self):
        self.display.display("GushPiBot...\nCreating menu")
        self.menu = Menu(self.display)

    def update_menu(self):
        for item in self.components:
            item.update_menu(self.menu)
        menu = self.menu.add_folder("System")
        self.menu.add_function("Exit", self.exit, menu)
        self.menu.add_function("Shutdown RasPi", self.pi_shutdown, menu)
        self.menu.add_function("IP Address", self.display_ip, menu)
        try:
            self.menu.speech = self.speech
        except AttributeError:
            pass

    def run(self, program=None):
        if program:
            self.display.display("GushPiBot...\nRunning...")
            self.program.set(program)
            self.program.view()
            self.program.run()
        else:
            self.display.display("GushPiBot...\nListening...")
            while self.loop_cycle():
                time.sleep(0.1)

    def display_ip(self):
        p = Popen("hostname -I", shell=True, stdout=PIPE)
        output = p.communicate()[0].split("\n")[0]
        self.display.display_at(1, 0, output.ljust(16))

    def exit(self):
        self.display.display("GushPiBot...\nExiting...")
        self.active = False

    def loop_cycle(self):
        for item in self.components:
            item.check()
        return self.active

    def cleanup(self):
        for item in self.components:
            try:
                item.cleanup()
            except:
                pass

    def pi_shutdown(self):
        self.display.display("Pi Shutdown")
        try:
            self.speech.speak("Shutting down Raspberry Pi")
        except AttributeError:
            pass
        call('halt', shell=False)

class Menu(object):

    class MenuItem(object):
        def __init__(self, name, func, folder):
            self.name = name
            self.func = func
            self.folder = folder

        def fire(self):
            if self.func:
                self.func()

    class MenuList(object):
        def __init__(self, parent=None):
            self.options = []
            self.parent = parent

        def add(self, name, func=None, folder=None):
            self.options.append(Menu.MenuItem(name, func, folder))

    def __init__(self, display, speech=None):
        self.root = Menu.MenuList(self)
        self.menu = self.root
        self.display = display
        self.speech = speech
        self.option = 0

    def add_folder(self, name, folder=None):
        if folder is None:
            folder = self.root
        new_folder = Menu.MenuList()
        new_folder.add("Back", folder=folder)
        folder.add(name + "/", folder=new_folder)
        return new_folder

    def add_function(self, name, func, folder=None):
        if folder is None:
            folder = self.root
        folder.add(name, func=func)

    def current_item(self):
        return self.menu.options[self.option]

    def prev(self):
        self.option -= 1
        if self.option < 0:
            self.option = len(self.menu.options) - 1
            self.display.reset()
        self.notify()

    def next(self):
        self.option += 1
        if self.option == len(self.menu.options):
            self.option = 0
            self.display.reset()
        self.notify()

    def notify(self):
        self.display.display_at(0, 0, self.current_item().name.ljust(16))
        if self.speech:
            self.speech.speak(self.current_item().name)

    def select(self):
        if self.current_item().folder:
            self.menu = self.current_item().folder
            self.option = 0
            self.notify()
        else:
            self.current_item().fire()

class Component(object):

    def __init__(self):
        pass

    def cleanup(self):
        pass

    def check(self):
        pass

    def update_menu(self, menu):
        pass

class EventHandler(object):
    def __init__(self):
        self.handlers = []

    def add(self, func):
        self.handlers.append(func)

    def remove(self, func):
        self.handlers.remove(func)

    def fire(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

class Keyboard(Component):
    """
    This class accepts keyboard input
    """
    class KeyboardHandler(EventHandler):

        def __init__(self, key_id):
            EventHandler.__init__(self)
            self.key_id = key_id

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.handlers = {}
        self.handlers["UP"] = Keyboard.KeyboardHandler(curses.KEY_UP)
        self.handlers["DOWN"] = Keyboard.KeyboardHandler(curses.KEY_DOWN)
        self.handlers["LEFT"] = Keyboard.KeyboardHandler(curses.KEY_LEFT)
        self.handlers["RIGHT"] = Keyboard.KeyboardHandler(curses.KEY_RIGHT)
        self.handlers["."] = Keyboard.KeyboardHandler(ord("."))
        self.handlers["{"] = Keyboard.KeyboardHandler(ord("{"))
        self.handlers["}"] = Keyboard.KeyboardHandler(ord("}"))
        self.handlers["#"] = Keyboard.KeyboardHandler(ord("#"))
        self.handlers["CTRL+X"] = Keyboard.KeyboardHandler(24)
        self.handlers["PAGEDOWN"] = Keyboard.KeyboardHandler(curses.KEY_PPAGE)
        self.handlers["PAGEUP"] = Keyboard.KeyboardHandler(curses.KEY_NPAGE)
        self.handlers["RETURN"] = Keyboard.KeyboardHandler(10)
        self.handlers["ESC"] = Keyboard.KeyboardHandler(27)

    def check(self):
        pressed_key = self.stdscr.getch()
        if pressed_key == curses.ERR:
            return
        for key in self.handlers:
            if pressed_key == self.handlers[key].key_id:
                self.handlers[key].fire()

class Command(object):
    """
    This class stores a single command
    """
    def __init__(self, shortcut, name, start_func, finish_func):
        self.shortcut = shortcut
        self.name = name
        self.start_func = start_func
        self.finish_func = finish_func

class Program(Component):
    """
    This class stores the instructions to run the program
    """
    def __init__(self, display):
        self.instructions = []
        self.commands = {}
        self.active = False
        self.display = display

    def set(self, program):
        for inst in program:
            self.add_instruction(inst)

    def cleanup(self):
        self.stop()

    def clear(self):
        self.instructions = []

    def add_command(self, shortcut, name, start_func, finish_func=None):
        self.commands[shortcut] = Command(shortcut, name, start_func, finish_func)

    def add_instruction(self, instruction):
        if instruction in self.commands.keys():
            self.instructions.append(instruction)

    def delete_instruction(self, step=-1):
        del self.instructions[step]

    def update_menu(self, menu):
        folder = menu.add_folder("Program")
        menu.add_function("View Program", self.view, folder)
        for command in self.commands:
            menu.add_function("Add " + self.commands[command].name,
                    lambda c=command: self.add_instruction(self.commands[c].shortcut), folder)
        menu.add_function("Delete Step", self.delete_instruction, folder)
        menu.add_function("Run Program", self.run, folder)
        menu.add_function("Stop Program", self.stop, folder)
        menu.add_function("Clear Program", self.clear, folder)

    def stop(self):
        self.active = False

    def run(self):
        self.active = True
        for instruction in self.instructions:
            if not self.active:
                return
            self.commands[instruction].start_func()
            time.sleep(1)
            if self.commands[instruction].finish_func:
                self.commands[instruction].finish_func()

    def view(self):
        self.display.display_at(1, 0, str(self).ljust(16))

    def __str__(self):
        curr_count = 0
        string = ""
        for instruction in self.instructions:
            if string and instruction == string[-1]:
                curr_count += 1
            else:
                if curr_count > 1:
                    string += str(curr_count)
                string += instruction
                curr_count = 1
        if curr_count > 1:
            string += str(curr_count)
        return string

class Wheels(Component):
    """
    This class controls the motors and makes the 'Bot move
    """
    def __init__(self, pin_1a=17, pin_1b=18, pin_2a=22, pin_2b=23):
        self.pins = [pin_1a, pin_1b, pin_2a, pin_2b]
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        self.speech_handler = EventHandler()

    def cleanup(self):
        self.stop()
        for pin in self.pins:
            GPIO.cleanup(pin)

    def send_command(self, command):
        for i in range(4):
            GPIO.output(self.pins[i], command[i])

    def stop(self):
        self.send_command([0, 0, 0, 0])
        self.speech_handler.fire("Stopping")

    def forwards(self):
        self.send_command([1, 0, 1, 0])
        self.speech_handler.fire("Going Forwards")

    def backwards(self):
        self.send_command([0, 1, 0, 1])
        self.speech_handler.fire("Going Backwards")

    def left(self):
        self.send_command([1, 0, 0, 1])
        self.speech_handler.fire("Turning Left")

    def slow_left(self):
        self.send_command([1, 0, 0, 0])
        self.speech_handler.fire("Turning Left Slowly")

    def right(self):
        self.send_command([0, 1, 1, 0])
        self.speech_handler.fire("Turning Right")

    def slow_right(self):
        self.send_command([0, 0, 1, 0])
        self.speech_handler.fire("Turning Right Slowly")

class ConsoleDisplay(Component):
    """
    This class shows output to the console if an LCD is not available
    """
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        self.stdscr.nodelay(True)

    def cleanup(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.noecho()
        curses.endwin()

    def reset(self):
        self.cleanup()
        self.__init__()

    def display(self, text):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, text)
        self.stdscr.refresh()

    def display_at(self, row, col, text):
        self.stdscr.addstr(row, col, text)
        self.stdscr.refresh()

class LCDDisplay(ConsoleDisplay):
    """
    This class looks after the 16x2 LCD display
    """
    def __init__(self, pin_rs=25, pin_en=24, data_pins=[9, 10, 21, 11]):
        ConsoleDisplay.__init__(self)
        self.lcd = Adafruit_CharLCD.Adafruit_CharLCD(pin_rs, pin_en, data_pins)
        self.lcd.begin(16, 2)

    def cleanup(self):
        ConsoleDisplay.cleanup(self)
        self.lcd.clear()
        GPIO.cleanup(self.lcd.pin_rs)
        GPIO.cleanup(self.lcd.pin_e)
        for pin in self.lcd.pins_db:
            GPIO.cleanup(pin)

    def display(self, text):
        ConsoleDisplay.display(self, text)
        self.lcd.clear()
        self.lcd.message(text)

    def display_at(self, row, col, text):
        ConsoleDisplay.display_at(self, row, col, text)
        self.lcd.setCursor(col, row)
        self.lcd.message(text)

    def scrollLeft(self):
        self.lcd.ScrollLeft()

    def scrollRight(self):
        self.lcd.scrollDisplayRight()

class Buttons(Component):
    """
    This class awaits the press of one of the two buttons
    """
    class ButtonHandler(EventHandler):
        def __init__(self, pin):
            EventHandler.__init__(self)
            self.PIN = pin
            GPIO.setup(self.PIN, GPIO.IN)

        def cleanup(self):
            GPIO.cleanup(self.PIN)

        def check(self):
            if GPIO.input(self.PIN):
                self.fire()

    def __init__(self, menu_pin=7, select_pin=8):
        self.handlers = {}
        self.handlers['MENU'] = Buttons.ButtonHandler(menu_pin)
        self.handlers['SELECT'] = Buttons.ButtonHandler(select_pin)

    def cleanup(self):
        for handler in self.handlers:
            self.handlers[handler].cleanup()

    def check(self):
        for handler in self.handlers:
            self.handlers[handler].check()

class Wiimote(Component):
    """
    This class listens out for activity on the Wii Controller, and acts accordingly
    """
    class ButtonHandler(EventHandler):

        def __init__(self, button_id):
            EventHandler.__init__(self)
            self.button_id = button_id

    def __init__(self, display=None):
        self.wiim = None
        self.display = display
        self.handlers = {}
        self.handlers["1"] = Wiimote.ButtonHandler(cwiid.BTN_1)
        self.handlers["2"] = Wiimote.ButtonHandler(cwiid.BTN_2)
        self.handlers["A"] = Wiimote.ButtonHandler(cwiid.BTN_A)
        self.handlers["B"] = Wiimote.ButtonHandler(cwiid.BTN_B)
        self.handlers["UP"] = Wiimote.ButtonHandler(cwiid.BTN_UP)
        self.handlers["DOWN"] = Wiimote.ButtonHandler(cwiid.BTN_DOWN)
        self.handlers["LEFT"] = Wiimote.ButtonHandler(cwiid.BTN_LEFT)
        self.handlers["RIGHT"] = Wiimote.ButtonHandler(cwiid.BTN_RIGHT)
        self.handlers["MINUS"] = Wiimote.ButtonHandler(cwiid.BTN_MINUS)
        self.handlers["PLUS"] = Wiimote.ButtonHandler(cwiid.BTN_PLUS)
        self.handlers["HOME"] = Wiimote.ButtonHandler(cwiid.BTN_HOME)
        self.stop_handler = None

    def cleanup(self):
        if self.wiim:
            self.wiim.close()

    def update_menu(self, menu):
        menu.add_function("Sync Wiimote", self.sync)

    def sync(self):
        self.display.display("Press both 1+2\non Wiimote NOW")
        try:
            self.wiim = cwiid.Wiimote()
        except:
            self.display.display("Wiimote sync\nfailed")
            return
        self.display.display("Wiimote sync\nsucceeded")
        self.wiim.rpt_mode = cwiid.RPT_BTN

    def check(self):
        if not self.wiim:
            return
        if self.stop_handler:
            self.stop_handler()
        for button in self.handlers:
            if self.wiim.state["buttons"] & self.handlers[button].button_id:
                self.handlers[button].fire()

class Echo(Component):
    """
    This class controls the echo sensor, in an attempt to prevent collisions
    """
    def __init__(self, display, send_pin=0, return_pin=4):
        self.display = display
        self.SEND = send_pin
        self.RETURN = return_pin
        self.distance_cm = 0
        self.last_time = time.time()
        GPIO.setup(self.SEND, GPIO.OUT)
        GPIO.setup(self.RETURN, GPIO.IN)
        GPIO.output(self.SEND, 0)
        self.stop_handler = EventHandler()
        self.active = False

    def update_menu(self, menu):
        menu.add_function("Toggle Echo", self.toggle_active)

    def toggle_active(self):
        self.active = not self.active
        if self.active:
            self.display.display("Echo enabled")
        else:
            self.display.display("Echo disabled")

    def check(self):
        if not self.active:
            return
        if time.time() < self.last_time + 0.2:
            return
        self.measure()
        self.last_time = time.time()
        if self.distance_cm < 15:
            self.stop_handler.fire()
        msg = str(int(self.distance_cm)) + "cm"
        if len(msg) <= 6:
            self.display.display_at(1, 11, msg.rjust(6))

    def measure(self):
        init_time = time.time()
        GPIO.output(self.SEND, 1)
        time.sleep(0.00001)
        GPIO.output(self.SEND, 0)
        start = time.time()
        while not GPIO.input(self.RETURN):
            start = time.time()
            if start > init_time + 5:
                return
        stop = time.time()
        while GPIO.input(self.RETURN):
            stop = time.time()
            if stop > init_time + 5:
                return
        self.distance_cm = (stop - start) * 17000

    def cleanup(self):
        GPIO.cleanup(self.SEND)
        GPIO.cleanup(self.RETURN)

class Webcam(Component):
    """
    This class controls the USB webcam
    Requires fswebcam commandline utility
    (I did try pygame, but this seems to get upset in a headless sudo environment)
    """
    def __init__(self):
        pass

    def update_menu(self, menu):
        menu.add_function("Take Photo", self.take_photo)

    def take_photo(self, filename="./gushpibot_pic.jpg"):
        call(["fswebcam", "-d", "/dev/video0", "-r", "640x480", "--no-banner", filename])

class Speech(Component):
    """
    This class allows the robot to speak
    """
    def __init__(self):
        self.engine = pyttsx.init()

    def cleanup(self):
        self.engine.stop()

    def update_menu(self, menu):
        menu.add_function("Take Photo", self.take_photo)

    def speak(self, message):
        self.engine.say(message)
        self.engine.runAndWait()

class Audio(Component):
    """
    This class allows the robot to play audio
    """
    def __init__(self):
        self.engine = pyttsx.init()

    def cleanup(self):
        self.engine.stop()

    def update_menu(self, menu):
        folder = menu.add_folder("Audio")
        for file in os.listdir("."):
            if file.endswith(".wav") or file.endswith(".mp3"):
                filename = os.path.splitext(file)[0][0:11]
                menu.add_function("Play " + filename, lambda x=file: self.play(x), folder)

    def play(self, filename):
        Popen(["mplayer", "-really-quiet", "-noconsolecontrols", filename])



if __name__ == "__main__":
    print("GushPiBot starting...")
    gushpibot = Controller()
    try:
        gushpibot.startup()
        if len(sys.argv) > 1:
            gushpibot.run(sys.argv[1])
        else:
            gushpibot.run()
    finally:
        gushpibot.cleanup()
