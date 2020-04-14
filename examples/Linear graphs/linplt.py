import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
import time

# Create figure for plotting
fig, ax = plt.subplots(3)
xs = []
ys2 = []
ys1 = []
ys = []

ser = serial.Serial('COM4', 9600)
time.sleep(2)

# This function is called periodically from FuncAnimation
def animate(i, xs, ys, ys1, ys2):
    # Read temperature (Celsius) from TMP102
    serRead = str(ser.readline())  # read from serial port
    serRead = serRead.split(' | ')  # split the string into parts at '|'
    tmilli = serRead[0].split('|')
    if len(tmilli) == 2:
        tmilli = tmilli[1]
    if len(serRead) == 8:  # Make sure we're reading a complete line
        AcX = serRead[1].split(' = ')
        AcY = serRead[2].split(' = ')
        AcZ = serRead[3].split(' = ')
        Tmp = serRead[4].split(' = ')
        GyX = serRead[5].split(' = ')
        GyY = serRead[6].split(' = ')
        GyZ = serRead[7].split(' = ')
        GyZ = GyZ[1].split('\\')  # remove \\r\\n at end of line
        GyX = int(GyX[1]) / 131
        GyY = int(GyY[1]) / 131
        GyZ = int(GyZ[0]) / 131
        AcX = int(AcX[1]) / 16384
        AcY = int(AcY[1]) / 16384
        AcZ = int(AcZ[1]) / 16384
        # Add x and y to lists
        xs.append(tmilli)
        ys.append(AcX)
        ys1.append(AcY)
        ys2.append(AcZ)

        # Limit x and y lists to 20 items
        xs = xs[-100:]
        ys = ys[-100:]
        ys1 = ys1[-100:]
        ys2 = ys2[-100:]

        # Draw x and y lists
        ax[0].clear()
        ax[0].tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        ax[0].plot(xs, ys)
        ax[0].set(ylabel="X Axis Force")

        ax[1].clear()
        ax[1].tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        ax[1].plot(xs, ys1)
        plt.ylabel('lin force')
        ax[1].set(ylabel="Y Axis Force")

        ax[2].clear()
        ax[2].tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        ax[2].plot(xs, ys2)
        ax[2].set(ylabel="Z Axis Force")



# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys, ys1, ys2), interval=1000)
plt.show()