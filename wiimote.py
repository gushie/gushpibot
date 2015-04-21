# sudo apt-get install python-cwiid
# Python 2 only :(
import cwiid
from component import Component, EventHandler

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
