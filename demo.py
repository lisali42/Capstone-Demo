#For UBC Capstone final demo 2020
#Team 48

#import json
import threading
import time

import flask
import serial

# How often to update the BNO sensor data (in hertz).
BNO_UPDATE_FREQUENCY_HZ = 10

# Name of the file to store calibration data when the save/load calibration
# button is pressed.  Calibration data is stored in JSON format.
CALIBRATION_FILE = "calibration.json"

# Create flask application.
app = flask.Flask(__name__)

# Global state to keep track of the latest readings from the BNO055 sensor.
# This will be accessed from multiple threads so care needs to be taken to
# protect access with a lock (or else inconsistent/partial results might be read).
# A condition object is used both as a lock for safe access across threads, and
# to notify threads that the BNO state has changed.
bno_data = {}
bno_changed = threading.Condition()

# Background thread to read BNO sensor data.  Will be created right before
# the first request is served (see start_bno_thread below).
bno_thread = None

ser = serial.Serial('COM4', 9600)
time.sleep(2)
while True:
    read = ser.readline()
    print(read)