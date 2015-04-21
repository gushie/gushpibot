import RPi.GPIO as GPIO
from component import Component, EventHandler

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
