import board
import time
import busio
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import datetime as dt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
 
# Initialize the I2C interface
i2c = busio.I2C(board.SCL, board.SDA)
 
# Create an ADS1115 object
ads = ADS.ADS1115(i2c)
 
# Define the analog input channel
channel = AnalogIn(ads, ADS.P0)
 
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
x = []
y = []
# Loop to read the analog input continuously
def animate(i, x, y):
    
        
    dist = ((channel.value/1024)*4.88)*2.64
    print("Distance: ", round(dist, 2))
    dist = round(dist, 2)
    y.append(dist)
    x.append(dt.datetime.now().strftime('%S.%d'))
    time.sleep(0.1)
  # Limit x and y lists to 50 items
    x = x[-50:]
    y = y[-50:]

    # Draw x and y lists
    ax.clear()
    ax.plot(x, y)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Distance over Time')
    plt.ylabel('Distance')

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(x, y), interval=500)
plt.show()
