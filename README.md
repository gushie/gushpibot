# gushpibot
Utility for controlling and programming a Raspberry Pi Ryanteck robot with LCD display, buttons, Wii controller, ultrasonic range sensor, speech and webcam

To run the program: `sudo ./gushpibot.py`

To run a sequence of steps and exit: `sudo ./gushpibot.py "^^^>v<"`
* ^ forwards
* v backwards
* < left (one wheel forwards, one backwards)
* { slow left (one wheel forwards, only)
* > right
* } slow right
* # Take photo

Each step will run for one second and then stop.

Cursor keys to control the motors, and "." to stop.
Page up/Page down to cycle through the menu and Enter to select a menu item.

Support for two electronic buttons are supported, one navigates the menu and one selects the menu item.

To use a Wiimote, it must first be synchronized via the menu. 
Arrows on the Wiimote control direction and (A) stops. Use +/- for navigating menu and Home to select the menu item.

It is developed for a Raspberry Pi Model B Revision 1. For use on a Rev2 or later, PIN numbers will need changing.

LCD is a simple 16x2 display I got for the Adventures in Raspberry Pi book

The range sensor is a cheap HC-SR04

The robot controller is a Ryanteck mmodel: http://www.ryanteck.uk/store/ryanteck-rpi-motor-controller-board

The webcam code is for a USB webcam (rather than the Pi Camera)

The speech outputs through a speaker plugged into the audio jack

A cheap USB bluetooth adapter required to communicate with the Wiimote. There are guides on the web for configuring this.

The LCD support requires Adafruit_CharLCD.py in the same folder as this code
```
sudo apt-get install git
git clone git://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git
```
Webcam support requires the fswebcam utility: 
```
sudo apt-get install fswebcam
```
Wii Controller support requires cwiid. This only works in Python2.
```
sudo apt-get install cwiid-python
```

Speech support requires:
```
sudo apt-get install alsa-utils espeak mplayer python-pip
sudo pip install praw pyttsx
```

Audio file support requires the 'mplayer' utility. 
It will index all *.wav and *.mp3 files in the current folder

#### Default GPIO PIN assigments (Model B revision 1)
0. ECHO SEND
1.
4. ECHO RETURN
7. BUTTON MENU
8. BUTTON SELECT
9. LCD D4 (LCD pin 11)
10. LCD D5 (LCD pin 12)
11. LCD D7 (LCD pin 14)
14.
15.
17. MOTOR 1A
18. MOTOR 1B
21. LCD D6 (LCD pin 13)
22. MOTOR 2A
23. MOTOR 2B
24. LCD EN (LCD pin 6)
25. LCD RS (LCD pin 4)

Use this program at your own risk. I take no responsibility for any damage this may cause to your Raspberry Pi / Robot
