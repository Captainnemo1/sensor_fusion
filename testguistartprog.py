import os
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
#import test_plot.py


class ProgramRunnerGUI:
	def __init__(self, master):
		self.master = master
		master.title("Sensor Fusion")
		master.configure(bg="black")
		master.geometry("800x600")
		
		# Set the path to your specific program
		self.program_path = "/home/velabs/RPLidar_LUPIN/test_plot.py"
		
		self.label = tk.Label(master, text=f"Running: {os.path.basename(self.program_path)}")
		self.label.pack()
		#self.master.attributes('-fullscreen', True)  # Open the GUI in fullscreen mode

		self.start_button = tk.Button(self.master, text="Start", bg="red", fg="white", font=("Arial", 24), command=self.run_program)
		self.start_button.pack(pady=10)
		
		self.lidar_status_label = tk.Label(master, text="Lidar Status", fg="white", bg="black", anchor=tk.W, font=("Arial", 20), pady=10)
		self.lidar_status_label.pack()
		
		self.red_button_color_lidar = tk.StringVar()
		self.red_button_color_lidar.set("red")
		self.red_button_lidar = tk.Button(self.master, command=self.show_red_lidar, padx=20, bg=self.red_button_color_lidar.get())
		self.red_button_lidar.pack(pady=10)
		
		self.ultrasonic_status_label = tk.Label(master, text="Ultrasonic Status", fg="white", bg="black", anchor=tk.W, font=("Arial", 20), pady=10)
		self.ultrasonic_status_label.pack()       
		
		self.red_button_color_ultrasonic = tk.StringVar()
		self.red_button_color_ultrasonic.set("red")
		self.red_button_ultrasonic = tk.Button(self.master, command=self.show_red_ultrasonic, padx=20, bg=self.red_button_color_ultrasonic.get())
		self.red_button_ultrasonic.pack(pady=10)
		
		self.average_distance_var = tk.StringVar()
		self.average_distance_label = tk.Label(master, textvariable=self.average_distance_var, bg="black", fg="white", font=("Arial", 24), pady=10)
		self.average_distance_label.pack()
		
		self.output_text = scrolledtext.ScrolledText(master, width=40, height=10)
		self.output_text.pack(pady=10)
        
		self.stop_button = tk.Button(master, text="Stop",  bg="red", fg="white", font=("Arial", 24), command=self.stop)
		self.stop_button.pack(pady=10)
		self.process = None  # Variable to store the subprocess object
		self.update_output()  # Start the periodic update


	
	def draw_lights(self, red_color_lidar, red_color_ultrasonic):
		# Clear previous drawings
		self.red_button_lidar.config(bg=red_color_lidar)
		self.red_button_ultrasonic.config(bg=red_color_ultrasonic)
	
	def show_red_lidar(self):
		self.draw_lights("red", "red")
	
	def show_red_ultrasonic(self):
		self.draw_lights("red", "red")
		
	def show_green(self):
		self.draw_lights("green", "green")
	
	def run_program(self):
		try:
			self.process = subprocess.Popen([self.program_path], cwd=os.path.dirname(self.program_path),
			stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
			
			self.start_button.config(state=tk.DISABLED)
			self.stop_button.config(state=tk.NORMAL)
			
			while self.process.poll() is None:  # While the process is running
				output = self.process.stdout.readline()
				
				if output:
					self.lidar_status_label.config(text="Lidar Status: Running")
					self.ultrasonic_status_label.config(text="Ultrasonic Status: Running")
					self.output_text.insert(tk.END, output)
					self.output_text.yview(tk.END)
					self.master.update()
					
					# Process has finished
					output, error = self.process.communicate()
					self.output_text.insert(tk.END, f"\nFinal Output:\n{output}")
					self.output_text.insert(tk.END, f"\nFinal Error:\n{error}")
					
					self.start_button.config(state=tk.NORMAL)
					self.stop_button.config(state=tk.DISABLED)
		
		except FileNotFoundError:
			messagebox.showerror("Error", f"Program not found: {self.program_path}")
		except Exception as e:
			messagebox.showerror("Error", f"An error occurred: {str(e)}")
	
	def stop(self):
		if self.process:
			self.process.terminate()
			self.output_text.insert(tk.END, "\nProgram stopped by user.\n")
			self.start_button.config(state=tk.NORMAL)
			self.stop_button.config(state=tk.DISABLED)
	
	def update_output(self):
		if self.process:
			output = self.process.stdout.readline()
			if output:
				self.output_text.insert(tk.END, output)
				self.output_text.yview(tk.END)
			self.master.after(100, self.update_output)  # Schedule the next update after 100 milliseconds

if __name__ == "__main__":
    root = tk.Tk()
    app = ProgramRunnerGUI(root)
    root.mainloop()
