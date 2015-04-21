#!/usr/bin/python

import sys
import time
from subprocess import Popen, PIPE
import RPi.GPIO as GPIO
from buttons import Buttons
from echo import Echo
from keyboard import Keyboard
from menu import Menu
from program import Program
from webcam import Webcam
from webserver import Webserver
from wheels import Wheels
try:
    from wiimote import Wiimote
    WII_AVAILABLE = True
except:
    WII_AVAILABLE = False
try:
    from display import ConsoleDisplay, LCDDisplay
    LCD_AVAILABLE = True
except:
    LCD_AVAILABLE = False
try:
    from audio import Audio, Speech
    AUDIO_AVAILABLE = True
    SPEECH_AVAILABLE = True
except:
    AUDIO_AVAILABLE = False
    SPEECH_AVAILABLE = False

BUTTONS_AVAILABLE = True
WEBCAM_AVAILABLE = True
ECHO_AVAILABLE = True
WEBSERVER_AVAILABLE = True

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

class GushPiBot(object):
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
        if WEBSERVER_AVAILABLE:
            self.create_webserver()
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
        self.wiimote.handlers["LEFT"].add(self.wheels.left)
        self.wiimote.handlers["RIGHT"].add(self.wheels.right)
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

    def create_webserver(self):
        self.webserver = Webserver()
        self.webserver.post_handlers["up"] = self.wheels.forwards
        self.webserver.post_handlers["down"] = self.wheels.backwards
        self.webserver.post_handlers["left"] = self.wheels.left
        self.webserver.post_handlers["right"] = self.wheels.right
        self.webserver.post_handlers["stop"] = self.wheels.stop
        self.webserver.post_handlers["menu_next"] = self.menu.next
        self.webserver.post_handlers["menu_prev"] = self.menu.prev
        self.webserver.post_handlers["menu_select"] = self.menu.select
        self.webserver.post_handlers["menu_text"] = self.menu.text
        try:
            self.webserver.post_handlers["photo"] = self.webcam.take_photo
        except AttributeError:
            pass
        self.webserver.serve()
        self.add_component("Webserver", self.webserver)

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
        p = Popen("hostname -I", shell=True, stdout=PIPE
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

if __name__ == "__main__":
    print("GushPiBot starting...")
    gushpibot = GushPiBot()
    try:
        gushpibot.startup()
        if len(sys.argv) > 1:
            gushpibot.run(sys.argv[1])
        else:
            gushpibot.run()
    finally:
        gushpibot.cleanup()
