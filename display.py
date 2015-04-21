import curses
import RPi.GPIO as GPIO
# sudo apt-get install git
# git clone git://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
import Adafruit_CharLCD
from component import Component

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
