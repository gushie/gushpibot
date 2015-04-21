import curses
from component import Component, EventHandler

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
