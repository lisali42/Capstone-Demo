# Capstone-Demo
UBC Team 48 capstone project demonstration of a concussion IMU.
A live visualization of rotational positioning of the sensor.

Libaries used
------
Will be using Flask and pyserial library. Installation notes are below
Run the following on your Python terminal

`pip install pyserial`

`pip install flask`

I had some issues with pyserial but I just uninstalled the library and reinstalled it and it worked fine (see below to uninstall).
`pip uninstall pyserial`

RegEx is used to parse the incoming data from the IMU. [See the following for more information.](https://www.w3schools.com/python/python_regex.asp)

The sample code needs a heading(yaw), roll, pitch as well as a [quaternion vector.](https://www.youtube.com/watch?v=zjMuIxRvygQ)

I used the [squaternion library by Kevin Walchko.](https://pypi.org/project/squaternion/)
