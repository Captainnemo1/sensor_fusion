# tkinter_display_values.py
import tkinter as tk
from example import generate_random_values

class RandomValuesApp:
    def __init__(self, master, generator):
        self.master = master
        self.master.title("Random Values Display")

        self.label = tk.Label(self.master, text="Random Values:")
        self.label.pack()

        self.value_var = tk.StringVar()
        self.value_label = tk.Label(self.master, textvariable=self.value_var)
        self.value_label.pack()
        
        self.start_button = tk.Button(self.master, text="Start", command=self.update_values)
        self.start_button.pack()
        
        self.quit_button = tk.Button(self.master, text="Quit", command=self.master.quit)
        self.quit_button.pack()

        self.generator = generator.mnbvc[POT]
                                                
        #self.update_values()

    def update_values(self):
        values = next(self.generator)
        formatted_values = f"Value 1: {values[0]}, Value 2: {values[1]:.4f}, Value 3: {values[2]}"
        self.value_var.set(formatted_values)
        self.master.after(1000, self.update_values)  # Update every 1000 milliseconds (1 second)

if __name__ == "__main__":
    generator_instance = generate_random_values()

    root = tk.Tk()
    app = RandomValuesApp(root, generator_instance)
    root.mainloop()

