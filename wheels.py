import RPi.GPIO as GPIO
from component import Component, EventHandler

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

    def right(self):
        self.send_command([1, 0, 0, 1])
        self.speech_handler.fire("Turning Right")

    def slow_right(self):
        self.send_command([1, 0, 0, 0])
        self.speech_handler.fire("Turning Right Slowly")

    def left(self):
        self.send_command([0, 1, 1, 0])
        self.speech_handler.fire("Turning Left")

    def slow_left(self):
        self.send_command([0, 0, 1, 0])
        self.speech_handler.fire("Turning Left Slowly")
