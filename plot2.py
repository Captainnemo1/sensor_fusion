import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import datetime as dt

data = pd.read_csv(r"/home/velabs/RPLidar_LUPIN/dist.csv")

time = 0
x = []
y = []
z = []

def animate(i):
    
    time = dt.datetime.now().strftime('%S.%d')
    x.append(time)
    
    # Append the new values to the respective lists
    y.append(data['Lidar Distance'].iloc[i])
    z.append(data['Ultrasonic Distance'].iloc[i])

    plt.cla()
    plt.ylim(0,2000)
    # Plot blue line for "Distance" data
    plt.plot(x, y, 'b-', label="Lidar")
    
    # Plot red scatter for "Ultrasonic Distance" data
    plt.plot(x, z, 'r-', label="Ultrasonic")
    
    # Add labels to the axes
    plt.xlabel("Time (s.d)")
    plt.ylabel("Distance")
    
    # Add a legend to differentiate between blue line and red dots
    plt.legend()

#ani = animation.FuncAnimation(plt.gcf(), animate, frames=len(data), interval=1)
#plt.show()
ani = animation.FuncAnimation(plt.gcf(), animate,frames=len(data), interval = 5)
plt.show()
