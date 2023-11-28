import tkinter as tk

def start_button_clicked():
    # Add your code here to handle the start button click event
    # This is where you would run the code to interact with Lidar/Ultrasonic

    # For now, let's just update the state labels and distance entry for demonstration
    lidar_state_label.config(text="Lidar Active", fg="green")
    ultrasonic_state_label.config(text="Ultrasonic Active", fg="green")

    # Replace the following line with your actual code to get the distance
    distance = 100

    distance_entry.delete(0, tk.END)  # Clear previous distance value
    distance_entry.insert(0, str(distance))  # Insert the updated distance value

# Create the main window
window = tk.Tk()
window.title("Sensor Fusion")
window.geometry("600x400")
window.configure(bg="black")

# Create and place the Start button in the center with increased font size
start_button = tk.Button(window, text="Start", command=start_button_clicked, bg="red", fg="white", font=("Arial", 24))
start_button.pack(pady=10)

# Create and place the Lidar state label with increased font size
lidar_state_label = tk.Label(window, text="Lidar Inactive", fg="red", bg="black", anchor=tk.W, font=("Arial", 24))
lidar_state_label.pack(pady=5, padx=10, anchor=tk.W)

# Create and place the Ultrasonic state label with increased font size
ultrasonic_state_label = tk.Label(window, text="Ultrasonic Inactive", fg="red", bg="black", anchor=tk.W, font=("Arial", 24))
ultrasonic_state_label.pack(pady=5, padx=10, anchor=tk.W)

# Create and place the label for Distance to Obstacle with increased font size
distance_label = tk.Label(window, text="Distance to Obstacle:", fg="white", bg="black", anchor=tk.W, font=("Arial", 24))
distance_label.pack(pady=5, padx=10, anchor=tk.W)

# Create and place the Distance to Obstacle entry with increased font size
distance_entry = tk.Entry(window, width=20, font=("Arial", 24))
distance_entry.insert(0, "0")  # Initial distance value
distance_entry.pack(pady=10, padx=10, anchor=tk.W)

# Run the Tkinter event loop
window.mainloop()

