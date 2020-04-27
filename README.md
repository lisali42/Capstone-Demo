# Capstone-Demo
UBC Team 48 capstone project demonstration of a concussion IMU.
A live visualization of rotational positioning and linear accelerations of the sensor.

![alt text](https://github.com/lisali42/Capstone-Demo/blob/master/ezgif-2-8c7803fcfd3e.gif)

## Useful links
https://howtomechatronics.com/tutorials/arduino/arduino-and-mpu6050-accelerometer-and-gyroscope-tutorial/

If cannot connect to server try: https://stackoverflow.com/questions/12978466/javascript-eventsource-sse-not-firing-in-browser/13135995#13135995?newreg=0e76543ee42b47029c5a2c60a3d2797f

## Introduction

This webapp uses Python and [Flask](https://www.fullstackpython.com/flask.html) in the backend, and uses [WebGL](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API) and [ChartJS](https://www.chartjs.org/) in the frontend.

On the server side, IMU parameters are received, parsed and then sent to the frontend with [SSE (Server sent event).](https://en.wikipedia.org/wiki/Server-sent_events)

Libaries used
------
Will be using Flask and pyserial library. Installation notes are below
Run the following on your Python terminal

`pip install pyserial`

`pip install flask`

`pip install json`

`pip install werkzeug.serving`

`pip install squaternion`

`pip install flask_cors`

I had some issues with pyserial but I just uninstalled the library and reinstalled it and it worked fine (see below to uninstall).
`pip uninstall pyserial`

## Back End

Most of the front end and back end is from this [tutorial](https://learn.adafruit.com/bno055-absolute-orientation-sensor-with-raspberry-pi-and-beaglebone-black/hardware)

In the python code, we have a thread, `read_bno()`, that continuously reads incomming IMU data from serial and a seperate thread that listens for requests from the client `bno_sse()`.

Depending on what format the IMU sends data, how you parse data may be different. Below is a sample string I was working with.

`'b\'|360 | AcX = -1 | AcY = -1 | AcZ = -1 | Tmp = 36.53 | GyX = -1 | GyY = -1 | GyZ = -1\\r\\n\''`

RegEx is used to parse the incoming data from the IMU. [See the following for more information.](https://www.w3schools.com/python/python_regex.asp)

The sample code needs a heading(yaw), roll, pitch as well as a [quaternion vector.](https://www.youtube.com/watch?v=zjMuIxRvygQ)

I used the [squaternion library by Kevin Walchko.](https://pypi.org/project/squaternion/)

Since we are receiving angular accelerations from the IMU instead of yaw, pitch and roll we need to convert these. Using methods from [this tutorial](https://howtomechatronics.com/tutorials/arduino/arduino-and-mpu6050-accelerometer-and-gyroscope-tutorial/) we have
````python
degx = ((math.atan(float(AcY) / math.sqrt(pow(AcX, 2) + pow(AcZ, 2))) * 180 / math.pi)-.58)*0.04 + (degx + (GyX-6.8) * (int(tmilli)/1000))*.96 # -.58 is to get rid of offset
degy = ((math.atan(-1 * AcX / math.sqrt(pow(AcY, 2) + pow(AcZ, 2))) * 180 / math.pi)+1.58)*0.04 + (degy + (GyY-2.5) * (int(tmilli)/1000))*.96 #+1.58 is to get rid of offset
degz = degz + (GyZ-0.24)*(int(tmilli)/1000) #.24 is to get rid of offset
````
Inbound values including linear acceleration may need some filters to remove the noise but it all depends on how much noise there is from the IMU.

## Front End

Custom 3D models can be added to this web app in the models variable see below
````javascript
var models = [
          {
            name: 'Bunny',
            load: function(model) {
              objMTLLoader.load(
                '{{ url_for('static', filename='bunny.obj') }}',  # change this to name of your 3D model
                '{{ url_for('static', filename='bunny.mtl') }}',  # change this to the name of your 3D model texture file
                function(object) {
                  var geom = object.children[1].geometry;
                  // Rebuild geometry normals because they aren't loaded properly.
                  geom.computeFaceNormals();
                  geom.computeVertexNormals();
                  // Build bunny mesh from geometry and material.
                  model.model = new THREE.Mesh(geom, material);
                  // Move the bunny so it's roughly in the center of the screen.
                  model.model.position.y = -4;
                }
              );
            }
          },
...
````
I used SolidWorks to create and `.stl` and used [MeshLab](http://www.meshlab.net/) to create `.mtl` and `.obj` files
