import os
from subprocess import Popen
# sudo apt-get install alsa-utils espeak mplayer python-pip
# sudo pip install praw pyttsx
import pyttsx
from component import Component

#pocketsphinx for speech recognition
# ? http://cmusphinx.sourceforge.net/wiki/raspberrypi

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
