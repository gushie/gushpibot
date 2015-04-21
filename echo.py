import time
import RPi.GPIO as GPIO
from component import Component, EventHandler

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

