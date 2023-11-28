from tkinter import *

root = Tk()             

root.geometry('500x400') 
root.configure(bg='black')

# Start Button
start_button = Button(root, text='Start', bd='5', bg='red', command=root.destroy)
start_button.pack(side='top', pady=10)

# Lidar Label
lidar_label = Label(root, text="Lidar\n\nUltrasonic\n\ndistance to obstacle", fg='white', bg='black', font=('Helvetica', 12))
lidar_label.pack(side='left', padx=10)

root.mainloop()

