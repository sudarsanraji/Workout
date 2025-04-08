import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
from datetime import datetime

class WorkoutApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Workout Timer App")
        self.geometry("600x500")
        self.configure(bg="#f0f0f0")
        
        # Data storage
        self.data_file = "workout_history.json"
        self.workout_history = self.load_workout_history()
        
        # Variables
        self.selected_body_parts = []
        self.workout_time = tk.IntVar(value=60)  # Default 60 seconds
        self.timer_running = False
        self.timer_paused = False
        self.remaining_time = 0
        self.current_workout = None
        
        # Create interface
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Workout Timer", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        # Body parts selection
        body_parts_frame = ttk.LabelFrame(main_frame, text="Select Body Parts")
        body_parts_frame.pack(fill="x", pady=10)
        
        body_parts = [
            "Chest", "Back", "Shoulders", "Biceps", "Triceps",
            "Legs", "Abs", "Cardio", "Full Body"
        ]
        
        self.body_part_vars = {}
        for i, part in enumerate(body_parts):
            var = tk.BooleanVar()
            self.body_part_vars[part] = var
            cb = ttk.Checkbutton(body_parts_frame, text=part, variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=5)
        
        # Timer settings
        timer_frame = ttk.LabelFrame(main_frame, text="Timer Settings")
        timer_frame.pack(fill="x", pady=10)
        
        ttk.Label(timer_frame, text="Workout Time (seconds):").grid(row=0, column=0, padx=5, pady=5)
        time_entry = ttk.Entry(timer_frame, textvariable=self.workout_time, width=10)
        time_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Preset buttons
        presets_frame = ttk.Frame(timer_frame)
        presets_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        preset_times = [30, 60, 90, 120, 300]
        for i, preset in enumerate(preset_times):
            ttk.Button(presets_frame, text=f"{preset}s", 
                      command=lambda t=preset: self.workout_time.set(t)).grid(row=0, column=i, padx=3)
        
        # Timer display
        self.timer_display = ttk.Label(main_frame, text="00:00", font=("Arial", 36))
        self.timer_display.pack(pady=10)
        
        # Control buttons
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(pady=10)
        
        self.start_button = ttk.Button(controls_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(controls_frame, text="Pause", command=self.pause_timer, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.reset_button = ttk.Button(controls_frame, text="Reset", command=self.reset_timer, state=tk.DISABLED)
        self.reset_button.grid(row=0, column=2, padx=5)
        
        # History button
        ttk.Button(main_frame, text="View Workout History", command=self.show_history).pack(pady=10)
    
    def start_timer(self):
        # Check if at least one body part is selected
        selected_parts = [part for part, var in self.body_part_vars.items() if var.get()]
        if not selected_parts:
            messagebox.showwarning("Warning", "Please select at least one body part.")
            return
        
        # Get time value
        try:
            seconds = self.workout_time.get()
            if seconds <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Warning", "Please enter a valid time in seconds.")
            return
        
        # If timer was paused, resume it
        if self.timer_paused:
            self.timer_paused = False
            self.pause_button.config(text="Pause")
        else:
            # Start a new timer
            self.selected_body_parts = selected_parts
            self.remaining_time = seconds
            self.current_workout = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "body_parts": self.selected_body_parts,
                "duration": seconds,
                "completed": False
            }
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        
        # Start timer
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        if self.timer_running and not self.timer_paused:
            if self.remaining_time <= 0:
                self.timer_completion()
                return
            
            # Update display
            minutes, seconds = divmod(self.remaining_time, 60)
            self.timer_display.config(text=f"{minutes:02d}:{seconds:02d}")
            
            # Decrement time
            self.remaining_time -= 1
            self.after(1000, self.update_timer)
    
    def pause_timer(self):
        if self.timer_running:
            if self.timer_paused:
                # Resume
                self.timer_paused = False
                self.pause_button.config(text="Pause")
                self.update_timer()
            else:
                # Pause
                self.timer_paused = True
                self.pause_button.config(text="Resume")
    
    def reset_timer(self):
        self.timer_running = False
        self.timer_paused = False
        self.remaining_time = 0
        self.timer_display.config(text="00:00")
        
        # Reset buttons
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.pause_button.config(text="Pause")
    
    def timer_completion(self):
        self.timer_running = False
        self.timer_display.config(text="Done!")
        
        # Save workout data
        if self.current_workout:
            self.current_workout["completed"] = True
            self.workout_history.append(self.current_workout)
            self.save_workout_history()
        
        # Show notification
        messagebox.showinfo("Workout Complete", 
                           f"You've completed your {', '.join(self.selected_body_parts)} workout!")
        
        # Reset UI
        self.reset_timer()
    
    def load_workout_history(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_workout_history(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.workout_history, f)
    
    def show_history(self):
        # Create a new window
        history_window = tk.Toplevel(self)
        history_window.title("Workout History")
        history_window.geometry("500x400")
        
        # Create a scrollable frame
        main_frame = ttk.Frame(history_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add a scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # History header
        ttk.Label(scrollable_frame, text="Workout History", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=3, pady=10)
        
        # Column headers
        ttk.Label(scrollable_frame, text="Date", font=("Arial", 10, "bold")).grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(scrollable_frame, text="Body Parts", font=("Arial", 10, "bold")).grid(
            row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(scrollable_frame, text="Duration", font=("Arial", 10, "bold")).grid(
            row=1, column=2, padx=5, pady=5, sticky="w")
        
        # No workout history
        if not self.workout_history:
            ttk.Label(scrollable_frame, text="No workout history found.").grid(
                row=2, column=0, columnspan=3, pady=20)
            return
        
        # Show workout history
        for i, workout in enumerate(reversed(self.workout_history)):
            row = i + 2  # Offset for headers
            
            ttk.Label(scrollable_frame, text=workout["date"]).grid(
                row=row, column=0, padx=5, pady=3, sticky="w")
            
            ttk.Label(scrollable_frame, text=", ".join(workout["body_parts"])).grid(
                row=row, column=1, padx=5, pady=3, sticky="w")
            
            # Format duration
            minutes, seconds = divmod(workout["duration"], 60)
            duration_text = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"
            ttk.Label(scrollable_frame, text=duration_text).grid(
                row=row, column=2, padx=5, pady=3, sticky="w")

# Run the application
if __name__ == "__main__":
    app = WorkoutApp()
    app.mainloop()
