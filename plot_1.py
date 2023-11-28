#import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import datetime as dt

data = pd.read_csv(r"/home/velabs/RPLidar_LUPIN/out.csv")
time = 0
x = []
y = []
z = []

def animate(i):
    global time
    time = dt.datetime.now().strftime('%S.%d')
    x.append(time)
    y.append(data['Distance'])
    z.append(data['Ultrasonic Distance'])

    plt.cla()
    plt.plot(x,y, 'b-' )
    plt.plot(x,z, 'ro' )

ani = animation.FuncAnimation(plt.gcf(), animate, interval = 1000)
plt.show()