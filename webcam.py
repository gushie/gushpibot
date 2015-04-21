from subprocess import call
from component import Component

WEBCAM_PHOTO_FILE = "gushpibot_pic.jpg"

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

    def take_photo(self, filename=WEBCAM_PHOTO_FILE):
        call(["fswebcam", "-d", "/dev/video0", "-r", "640x480", "--no-banner", filename])
