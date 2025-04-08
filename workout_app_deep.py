import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

class WorkoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Workout App")
        self.root.geometry("500x400")
        
        # Workout data
        self.workouts = {
            "Chest": ["Push-ups", "Bench Press", "Chest Fly", "Incline Press"],
            "Back": ["Pull-ups", "Rows", "Lat Pulldown", "Deadlifts"],
            "Legs": ["Squats", "Lunges", "Leg Press", "Calf Raises"],
            "Arms": ["Bicep Curls", "Tricep Dips", "Hammer Curls", "Skull Crushers"],
            "Core": ["Plank", "Sit-ups", "Russian Twists", "Leg Raises"]
        }
        
        # Timer variables
        self.timer_running = False
        self.seconds_left = 0
        self.timer_thread = None
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        # Body part selection
        ttk.Label(self.root, text="Select Body Part:").pack(pady=5)
        self.body_part_var = tk.StringVar()
        self.body_part_menu = ttk.Combobox(self.root, textvariable=self.body_part_var, 
                                          values=list(self.workouts.keys()))
        self.body_part_menu.pack(pady=5)
        self.body_part_menu.bind("<<ComboboxSelected>>", self.update_exercises)
        
        # Exercise selection
        ttk.Label(self.root, text="Select Exercise:").pack(pady=5)
        self.exercise_var = tk.StringVar()
        self.exercise_menu = ttk.Combobox(self.root, textvariable=self.exercise_var)
        self.exercise_menu.pack(pady=5)
        
        # Timer controls
        ttk.Label(self.root, text="Set Timer (seconds):").pack(pady=5)
        self.timer_entry = ttk.Entry(self.root)
        self.timer_entry.pack(pady=5)
        
        # Buttons
        self.start_button = ttk.Button(self.root, text="Start Timer", command=self.start_timer)
        self.start_button.pack(pady=5)
        
        self.stop_button = ttk.Button(self.root, text="Stop Timer", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        # Timer display
        self.timer_label = ttk.Label(self.root, text="00:00", font=("Arial", 24))
        self.timer_label.pack(pady=20)
        
        # Workout log
        self.log_text = tk.Text(self.root, height=5, width=50)
        self.log_text.pack(pady=10)
        self.log_text.insert(tk.END, "Workout Log:\n")
        self.log_text.config(state=tk.DISABLED)
    
    def update_exercises(self, event):
        selected_part = self.body_part_var.get()
        if selected_part in self.workouts:
            self.exercise_menu['values'] = self.workouts[selected_part]
    
    def start_timer(self):
        if self.timer_running:
            return
            
        try:
            seconds = int(self.timer_entry.get())
            if seconds <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for seconds")
            return
        
        exercise = self.exercise_var.get()
        if not exercise:
            messagebox.showerror("Error", "Please select an exercise")
            return
        
        self.seconds_left = seconds
        self.timer_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Update log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"Started {exercise} for {seconds} seconds\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self.run_timer)
        self.timer_thread.start()
    
    def stop_timer(self):
        self.timer_running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join()
        
        exercise = self.exercise_var.get()
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"Stopped {exercise}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def run_timer(self):
        while self.seconds_left > 0 and self.timer_running:
            mins, secs = divmod(self.seconds_left, 60)
            timer_text = f"{mins:02d}:{secs:02d}"
            
            # Update GUI from main thread
            self.root.after(0, lambda: self.timer_label.config(text=timer_text))
            
            time.sleep(1)
            self.seconds_left -= 1
        
        if self.seconds_left <= 0 and self.timer_running:
            self.root.after(0, self.timer_complete)
    
    def timer_complete(self):
        self.timer_running = False
        self.timer_label.config(text="00:00")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        exercise = self.exercise_var.get()
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"Completed {exercise}!\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        messagebox.showinfo("Timer Complete", "Great job! Exercise completed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkoutApp(root)
    root.mainloop()