#For UBC Capstone final demo 2020
#Team 48

import json
import re
import threading
import time

import flask
import serial

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np

from squaternion import euler2quat, quat2euler, Quaternion

# How often to update the BNO sensor data (in hertz).
BNO_UPDATE_FREQUENCY_HZ = 1000


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

#TODO create object for graphs

def read_bno():
    """Function to read the BNO sensor and update the bno_data object with the
    latest BNO orientation, etc. state.  Must be run in its own thread because
    it will never return!"""
    ser = serial.Serial('COM4', 9600)
    time.sleep(2)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    xs = []  # store trials here (n)
    ys = []  # store relative frequency here
    print('starting plot')

    while True:
        serRead = str(ser.readline())          #read from serial port
        serRead = serRead.split(' | ')            #split the string into parts at '|'
        tmilli = serRead[0].split('|')
        if len(tmilli) == 2:
            tmilli = tmilli[1]
        if len(serRead) == 8:                  #Make sure we're reading a complete line
            AcX = serRead[1].split(' = ')
            AcY = serRead[2].split(' = ')
            AcZ = serRead[3].split(' = ')
            Tmp = serRead[4].split(' = ')
            GyX = serRead[5].split(' = ')
            GyY = serRead[6].split(' = ')
            GyZ = serRead[7].split(' = ')
            GyZ = GyZ[1].split('\\')    #remove \\r\\n at end of line
            q = euler2quat(int(GyX[1]) / 131, int(GyY[1]) / 131, int(GyZ[0]) / 131)     #typecast, scale and convert euler angles to quaternion vector
            GyX = int(GyX[1]) / 131
            GyY = int(GyY[1]) / 131
            GyZ = int(GyZ[0]) / 131
            AcX = int(AcX[1]) / 16384
            AcY = int(AcY[1]) / 16384
            AcZ = int(AcZ[1]) / 16384

            xs.append(tmilli)
            ys.append(AcX)
            ax.clear()
            ax.plot(xs, ys, label="Linear force")
            # Format plot
            plt.xticks(rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.30)
            plt.title('IMU Readings')
            plt.ylabel('Linear force')
            plt.legend()
            plt.axis([1, None, 0, 1.1])  # Use for arbitrary number of trials
            # plt.axis([1, 100, 0, 1.1]) #Use for 100 trial demo

            plt.show()

            #print(int(AcX[1]) / 16384, int(AcY[1]) / 16384, int(AcZ[1]) / 16384)
            # Capture the lock on the bno_changed condition so the bno_data shared
            # state can be updated.
            with bno_changed:
                bno_data["euler"] = [GyX, GyY, GyZ]
                bno_data["temp"] = float(Tmp[1])
                bno_data["quaternion"] = [q[1], q[2],q[3], q[0]]
                bno_data["calibration"] = [int(3), int(3), int(3), int(3)]     #"3 indicates fully calibrated; 0 indicates not calibrated" Page 68 BNO055
                # Notify any waiting threads that the BNO state has been updated.
                bno_changed.notifyAll()
                print("notified all")
            # Sleep until the next reading.
        time.sleep(1.0 / BNO_UPDATE_FREQUENCY_HZ)

def bno_sse():
    """Function to handle sending BNO055 sensor data to the client web browser
    using HTML5 server sent events (aka server push).  This is a generator function
    that flask will run in a thread and call to get new data that is pushed to
    the client web page."""
    
    # Loop forever waiting for a new BNO055 sensor reading and sending it to
    # the client.  Since this is a generator function the yield statement is
    # used to return a new result.
    while True:
        # Capture the bno_changed condition lock and then wait for it to notify
        # a new reading is available.
        with bno_changed:
            bno_changed.wait()
            # A new reading is available!  Grab the reading value and then give
            # up the lock.
            heading, roll, pitch = bno_data["euler"]
            temp = bno_data["temp"]
            x, y, z, w = bno_data["quaternion"]
            sys, gyro, accel, mag = bno_data["calibration"]
        # Send the data to the connected client in HTML5 server sent event format.
        data = {
            "heading": heading,
            "roll": roll,
            "pitch": pitch,
            "temp": temp,
            "quatX": x,
            "quatY": y,
            "quatZ": z,
            "quatW": w,
            "calSys": sys,
            "calGyro": gyro,
            "calAccel": accel,
            "calMag": mag,
        }
        return "data: {0}\n\n".format(json.dumps(data))


@app.before_first_request
def start_bno_thread():
    # Start the BNO thread right before the first request is served.  This is
    # necessary because in debug mode flask will start multiple main threads so
    # this is the only spot to put code that can only run once after starting.
    # See this SO question for more context:
    #   http://stackoverflow.com/questions/24617795/starting-thread-while-running-flask-with-debug
    global bno_thread  # pylint: disable=global-statement
    # Kick off BNO055 reading thread.
    bno_thread = threading.Thread(target=read_bno)
    bno_thread.daemon = True  # Don't let the BNO reading thread block exiting.
    bno_thread.start()


@app.route("/bno")
def bno_path():
    # Return SSE response and call bno_sse function to stream sensor data to
    # the webpage.
    return flask.Response(bno_sse(), mimetype="text/event-stream")


@app.route("/save_calibration", methods=["POST"])
def save_calibration():
    # Save calibration data to disk.
    #
    # TODO: implement this
    #
    return "OK"


@app.route("/load_calibration", methods=["POST"])
def load_calibration():
    # Load calibration from disk.
    #
    # TODO: implement this
    #
    return "OK"


@app.route("/")
def root():
    return flask.render_template("index.html")


if __name__ == "__main__":
    # Create a server listening for external connections on the default
    # port 5000.  Enable debug mode for better error messages and live
    # reloading of the server on changes.  Also make the server threaded
    # so multiple connections can be processed at once (very important
    # for using server sent events).
    app.run(host="192.168.0.16", debug=True, threaded=True)
