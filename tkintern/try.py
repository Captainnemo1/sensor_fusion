import tkinter as tk
import subprocess

def start_button_clicked():
    try:
        # Add your command to run the desired program
        command = "your_program_command_here"
        
        # Run the command and capture the output
        output = subprocess.check_output(command, shell=True, text=True)

        # Update the state labels and display the output in the GUI
        lidar_state_label.config(text="Lidar Active", fg="green")
        ultrasonic_state_label.config(text="Ultrasonic Active", fg="green")
        distance_entry.delete(0, tk.END)  # Clear previous distance value
        distance_entry.insert(0, output)  # Insert the output in the entry widget
    except subprocess.CalledProcessError as e:
        # Handle errors, if any
        print(f"Error: {e}")
        lidar_state_label.config(text="Lidar Inactive", fg="red")
        ultrasonic_state_label.config(text="Ultrasonic Inactive", fg="red")
        distance_entry.delete(0, tk.END)
        distance_entry.insert(0, "Error occurred")

# Create the main window
window = tk.Tk()
window.title("Lidar and Ultrasonic GUI")
window.geometry("600x400")
window.configure(bg="black")

# Create and place the Start button in the center with increased font size
start_button = tk.Button(window, text="Start", command=start_button_clicked, bg="red", fg="white", font=("Arial", 14))
start_button.pack(pady=10)

# Create and place the Lidar state label with increased font size
lidar_state_label = tk.Label(window, text="Lidar Inactive", fg="red", bg="black", anchor=tk.W, font=("Arial", 12))
lidar_state_label.pack(pady=5, padx=10, anchor=tk.W)

# Create and place the Ultrasonic state label with increased font size
ultrasonic_state_label = tk.Label(window, text="Ultrasonic Inactive", fg="red", bg="black", anchor=tk.W, font=("Arial", 12))
ultrasonic_state_label.pack(pady=5, padx=10, anchor=tk.W)

# Create and place the label for Distance to Obstacle with increased font size
distance_label = tk.Label(window, text="Distance to Obstacle:", fg="white", bg="black", anchor=tk.W, font=("Arial", 12))
distance_label.pack(pady=5, padx=10, anchor=tk.W)

# Create and place the Distance to Obstacle entry with increased font size
distance_entry = tk.Entry(window, width=40, font=("Arial", 12))
distance_entry.insert(0, "0")  # Initial distance value
distance_entry.pack(pady=10, padx=10, anchor=tk.W)

# Run the Tkinter event loop
window.mainloop()

