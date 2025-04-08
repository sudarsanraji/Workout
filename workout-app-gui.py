import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import json
import os
from datetime import datetime
from enum import Enum
import threading

class MuscleGroup(str, Enum):
    CHEST = "Chest"
    BACK = "Back"
    SHOULDERS = "Shoulders"
    BICEPS = "Biceps"
    TRICEPS = "Triceps"
    LEGS = "Legs"
    CORE = "Core"

class Exercise:
    def __init__(self, id, name, muscle_groups, description, equipment_needed=None, 
                 difficulty_level="beginner", recommended_rest=60):
        self.id = id
        self.name = name
        self.muscle_groups = muscle_groups if isinstance(muscle_groups, list) else [muscle_groups]
        self.description = description
        self.equipment_needed = equipment_needed
        self.difficulty_level = difficulty_level
        self.recommended_rest = recommended_rest
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "muscle_groups": [mg.value for mg in self.muscle_groups],
            "description": self.description,
            "equipment_needed": self.equipment_needed,
            "difficulty_level": self.difficulty_level,
            "recommended_rest": self.recommended_rest
        }

class WorkoutAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Workout App")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        self.exercises = self._load_exercise_database()
        self.workout_history = self._load_workout_history()
        
        self.current_workout = []
        self.current_exercise_index = 0
        self.current_set = 1
        self.timer_running = False
        self.timer_thread = None
        self.stop_timer = threading.Event()
            
        # Create tabs
        self.tab_control = ttk.Notebook(root)
        
        self.tab_home = ttk.Frame(self.tab_control)
        self.tab_exercises = ttk.Frame(self.tab_control)
        self.tab_create_workout = ttk.Frame(self.tab_control)
        self.tab_active_workout = ttk.Frame(self.tab_control)
        self.tab_history = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_home, text="Home")
        self.tab_control.add(self.tab_exercises, text="Exercises")
        self.tab_control.add(self.tab_create_workout, text="Create Workout")
        self.tab_control.add(self.tab_active_workout, text="Active Workout")
        self.tab_control.add(self.tab_history, text="History")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Set up each tab
        self._setup_home_tab()
        self._setup_exercises_tab()
        self._setup_create_workout_tab()
        self._setup_active_workout_tab()
        self._setup_history_tab()
        
        # Initially disable the Active Workout tab
        self.tab_control.tab(3, state="disabled")
    
    def _load_exercise_database(self):
        # Default exercise database if file doesn't exist
        default_exercises = {
            "push-up-001": Exercise(
                "push-up-001",
                "Push-ups",
                [MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
                "Standard push-up position, lower body until chest nearly touches ground",
                None,
                "beginner",
                60
            ),
            "squat-001": Exercise(
                "squat-001",
                "Bodyweight Squats",
                [MuscleGroup.LEGS],
                "Stand with feet shoulder-width apart, lower body until thighs are parallel to ground",
                None,
                "beginner",
                60
            ),
            "plank-001": Exercise(
                "plank-001",
                "Plank",
                [MuscleGroup.CORE],
                "Hold push-up position with arms extended or on forearms, keeping body straight",
                None,
                "beginner",
                45
            ),
            "pull-up-001": Exercise(
                "pull-up-001", 
                "Pull-ups",
                [MuscleGroup.BACK, MuscleGroup.BICEPS],
                "Grip bar with palms facing away, pull body up until chin clears bar",
                "Pull-up bar",
                "intermediate",
                90
            ),
            "lunge-001": Exercise(
                "lunge-001",
                "Walking Lunges",
                [MuscleGroup.LEGS],
                "Step forward into lunge position, lower back knee toward ground, alternate legs",
                None,
                "beginner",
                60
            ),
            "dips-001": Exercise(
                "dips-001",
                "Tricep Dips",
                [MuscleGroup.TRICEPS, MuscleGroup.CHEST],
                "Using parallel bars or chair, lower body by bending arms, then push back up",
                "Parallel bars or sturdy chair",
                "intermediate",
                75
            ),
            "crunches-001": Exercise(
                "crunches-001",
                "Crunches",
                [MuscleGroup.CORE],
                "Lie on back with knees bent, curl shoulders toward pelvis",
                None,
                "beginner",
                45
            ),
            "lateral-raise-001": Exercise(
                "lateral-raise-001",
                "Lateral Raises",
                [MuscleGroup.SHOULDERS],
                "Stand with dumbbells at sides, raise arms laterally to shoulder level",
                "Dumbbells",
                "beginner",
                60
            ),
            "bicep-curl-001": Exercise(
                "bicep-curl-001",
                "Bicep Curls",
                [MuscleGroup.BICEPS],
                "Stand with dumbbells at sides, palms forward, curl weights to shoulders",
                "Dumbbells",
                "beginner",
                60
            )
        }
        
        try:
            if os.path.exists("exercise_database.json"):
                with open("exercise_database.json", "r") as f:
                    data = json.load(f)
                    exercises = {}
                    for key, ex in data.items():
                        exercises[key] = Exercise(
                            ex["id"],
                            ex["name"],
                            [MuscleGroup(mg) for mg in ex["muscle_groups"]],
                            ex["description"],
                            ex["equipment_needed"],
                            ex["difficulty_level"],
                            ex["recommended_rest"]
                        )
                    return exercises
            
            # If we got here, either the file doesn't exist or there was an error
            # Save the default exercises to the file
            self._save_exercise_database(default_exercises)
                    
        except Exception as e:
            print(f"Error loading exercise database: {e}")
            print("Using default exercise database.")
        
        return default_exercises
    
    def _save_exercise_database(self, exercises=None):
        if exercises is None:
            exercises = self.exercises
            
        exercise_dict = {}
        for ex_id, ex in exercises.items():
            exercise_dict[ex_id] = ex.to_dict()
            
        with open("exercise_database.json", "w") as f:
            json.dump(exercise_dict, f, indent=4)
    
    def _load_workout_history(self):
        try:
            if os.path.exists("workout_history.json"):
                with open("workout_history.json", "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading workout history: {e}")
        
        return {}
    
    def _save_workout_history(self):
        with open("workout_history.json", "w") as f:
            json.dump(self.workout_history, f, indent=4)
    
    def _setup_home_tab(self):
        frame = ttk.Frame(self.tab_home, padding="20")
        frame.pack(expand=True, fill="both")
        
        # Title
        title_label = ttk.Label(frame, text="Workout Tracker App", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Logo or Image placeholder
        logo_frame = ttk.Frame(frame, width=200, height=200, relief="solid", borderwidth=1)
        logo_frame.pack(pady=20)
        logo_label = ttk.Label(logo_frame, text="💪 Workout App", font=("Arial", 16))
        logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Quick stats
        stats_frame = ttk.LabelFrame(frame, text="Your Stats", padding=10)
        stats_frame.pack(fill="x", pady=20)
        
        # Calculate stats
        total_workouts = len(self.workout_history)
        
        # Last workout date
        last_workout_date = "Never"
        if total_workouts > 0:
            dates = [workout["date"] for workout in self.workout_history.values()]
            last_workout_date = max(dates)
            last_workout_date = datetime.fromisoformat(last_workout_date).strftime("%Y-%m-%d %H:%M")
        
        # Display stats
        ttk.Label(stats_frame, text=f"Total Workouts: {total_workouts}").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(stats_frame, text=f"Last Workout: {last_workout_date}").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Quick actions
        actions_frame = ttk.Frame(frame)
        actions_frame.pack(fill="x", pady=20)
        
        ttk.Button(actions_frame, text="Start New Workout", 
                  command=lambda: self.tab_control.select(2)).pack(side="left", padx=10)
        ttk.Button(actions_frame, text="View Exercise Library", 
                  command=lambda: self.tab_control.select(1)).pack(side="left", padx=10)
        ttk.Button(actions_frame, text="Check Workout History", 
                  command=lambda: self.tab_control.select(4)).pack(side="left", padx=10)
    
    def _setup_exercises_tab(self):
        # Create a frame with a paned window
        frame = ttk.Frame(self.tab_exercises)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(frame, text="Exercise Library", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Create paned window
        paned = ttk.PanedWindow(frame, orient="horizontal")
        paned.pack(expand=True, fill="both")
        
        # Left panel - Exercise categories
        left_frame = ttk.Frame(paned, padding=10)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Filter by Muscle Group", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Create treeview for muscle groups
        self.muscle_tree = ttk.Treeview(left_frame, show="tree")
        self.muscle_tree.pack(expand=True, fill="both")
        
        # Add "All Exercises" option
        self.muscle_tree.insert("", "end", "all", text="All Exercises")
        
        # Add muscle groups
        for muscle in MuscleGroup:
            self.muscle_tree.insert("", "end", muscle.value, text=muscle.value)
        
        self.muscle_tree.bind("<<TreeviewSelect>>", self._filter_exercises)
        
        # Right panel - Exercise list and details
        right_frame = ttk.Frame(paned, padding=10)
        paned.add(right_frame, weight=2)
        
        # Create exercises treeview
        columns = ("name", "muscle_groups", "difficulty")
        self.exercise_tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        self.exercise_tree.heading("name", text="Exercise Name")
        self.exercise_tree.heading("muscle_groups", text="Muscle Groups")
        self.exercise_tree.heading("difficulty", text="Difficulty")
        
        self.exercise_tree.column("name", width=150)
        self.exercise_tree.column("muscle_groups", width=150)
        self.exercise_tree.column("difficulty", width=100)
        
        self.exercise_tree.pack(expand=True, fill="both", pady=(0, 10))
        
        # Exercise detail frame
        detail_frame = ttk.LabelFrame(right_frame, text="Exercise Details", padding=10)
        detail_frame.pack(expand=True, fill="both")
        
        # Add scrollbar to detail_frame
        detail_scroll = ttk.Scrollbar(detail_frame)
        detail_scroll.pack(side="right", fill="y")
        
        self.detail_text = tk.Text(detail_frame, wrap="word", height=8, 
                                 yscrollcommand=detail_scroll.set)
        self.detail_text.pack(expand=True, fill="both", padx=5, pady=5)
        detail_scroll.config(command=self.detail_text.yview)
        
        # Bind selection event to show details
        self.exercise_tree.bind("<<TreeviewSelect>>", self._show_exercise_details)
        
        # Populate the exercise list initially with all exercises
        self._populate_exercise_list()
    
    def _filter_exercises(self, event):
        selected_item = self.muscle_tree.focus()
        if selected_item:
            self._populate_exercise_list(selected_item)
    
    def _populate_exercise_list(self, muscle_filter="all"):
        # Clear current items
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)
        
        # Add exercises to the tree
        for ex_id, exercise in self.exercises.items():
            muscle_groups_str = ", ".join([mg.value for mg in exercise.muscle_groups])
            
            # Apply filter
            if muscle_filter == "all" or muscle_filter in [mg.value for mg in exercise.muscle_groups]:
                self.exercise_tree.insert("", "end", ex_id, values=(exercise.name, muscle_groups_str, exercise.difficulty_level))
    
    def _show_exercise_details(self, event):
        selected_id = self.exercise_tree.focus()
        if selected_id in self.exercises:
            exercise = self.exercises[selected_id]
            
            # Clear current text
            self.detail_text.delete(1.0, tk.END)
            
            # Add exercise details
            self.detail_text.insert(tk.END, f"Name: {exercise.name}\n\n")
            self.detail_text.insert(tk.END, f"Description: {exercise.description}\n\n")
            self.detail_text.insert(tk.END, f"Muscle Groups: {', '.join([mg.value for mg in exercise.muscle_groups])}\n\n")
            self.detail_text.insert(tk.END, f"Difficulty: {exercise.difficulty_level}\n\n")
            
            if exercise.equipment_needed:
                self.detail_text.insert(tk.END, f"Equipment: {exercise.equipment_needed}\n\n")
            else:
                self.detail_text.insert(tk.END, "Equipment: None needed\n\n")
                
            self.detail_text.insert(tk.END, f"Recommended Rest: {exercise.recommended_rest} seconds")
            
            # Make text read-only
            self.detail_text.config(state="disabled")
    
    def _setup_create_workout_tab(self):
        frame = ttk.Frame(self.tab_create_workout, padding="10")
        frame.pack(expand=True, fill="both")
        
        # Title
        title_label = ttk.Label(frame, text="Create Workout", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Split into two columns
        columns_frame = ttk.Frame(frame)
        columns_frame.pack(expand=True, fill="both", pady=10)
        
        # Left column - Exercise selection
        left_frame = ttk.LabelFrame(columns_frame, text="Select Exercises", padding=10)
        left_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))
        
        # Filter by muscle group
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by:").pack(side="left", padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                  values=["All"] + [mg.value for mg in MuscleGroup])
        filter_combo.pack(side="left", expand=True, fill="x")
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self._filter_exercise_selection())
        
        # Exercise selection listbox with scrollbar
        select_frame = ttk.Frame(left_frame)
        select_frame.pack(expand=True, fill="both")
        
        scrollbar = ttk.Scrollbar(select_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.exercise_listbox = tk.Listbox(select_frame, yscrollcommand=scrollbar.set, selectmode="single")
        self.exercise_listbox.pack(expand=True, fill="both")
        scrollbar.config(command=self.exercise_listbox.yview)
        
        # Populate the exercise list
        self._filter_exercise_selection()
        
        # Exercise details and add button
        details_frame = ttk.Frame(left_frame)
        details_frame.pack(fill="x", pady=10)
        
        sets_frame = ttk.Frame(details_frame)
        sets_frame.pack(fill="x", pady=5)
        ttk.Label(sets_frame, text="Sets:").pack(side="left", padx=(0, 5))
        self.sets_var = tk.IntVar(value=3)
        sets_spinbox = ttk.Spinbox(sets_frame, from_=1, to=10, textvariable=self.sets_var, width=5)
        sets_spinbox.pack(side="left")
        
        reps_frame = ttk.Frame(details_frame)
        reps_frame.pack(fill="x", pady=5)
        ttk.Label(reps_frame, text="Reps:").pack(side="left", padx=(0, 5))
        self.reps_var = tk.IntVar(value=10)
        reps_spinbox = ttk.Spinbox(reps_frame, from_=1, to=50, textvariable=self.reps_var, width=5)
        reps_spinbox.pack(side="left")
        
        ttk.Button(details_frame, text="Add to Workout", command=self._add_to_workout).pack(fill="x", pady=(10, 0))
        
        # Right column - Current workout plan
        right_frame = ttk.LabelFrame(columns_frame, text="Current Workout", padding=10)
        right_frame.pack(side="right", expand=True, fill="both", padx=(5, 0))
        
        # Workout exercise list with scrollbar
        workout_frame = ttk.Frame(right_frame)
        workout_frame.pack(expand=True, fill="both", pady=(0, 10))
        
        scrollbar2 = ttk.Scrollbar(workout_frame)
        scrollbar2.pack(side="right", fill="y")
        
        self.workout_listbox = tk.Listbox(workout_frame, yscrollcommand=scrollbar2.set)
        self.workout_listbox.pack(expand=True, fill="both")
        scrollbar2.config(command=self.workout_listbox.yview)
        
        # Buttons for workout management
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Remove Selected", 
                  command=self._remove_from_workout).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Clear All", 
                  command=self._clear_workout).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Start Workout", 
                  command=self._start_workout).pack(side="right")
        
        # Validation feedback
        self.validation_frame = ttk.LabelFrame(frame, text="Workout Validation", padding=10)
        self.validation_frame.pack(fill="x", pady=10)
        
        self.validation_text = tk.Text(self.validation_frame, wrap="word", height=4)
        self.validation_text.pack(expand=True, fill="both")
        self.validation_text.insert(tk.END, "Add exercises to create a workout...")
        self.validation_text.config(state="disabled")
    
    def _filter_exercise_selection(self):
        # Clear current items
        self.exercise_listbox.delete(0, tk.END)
        
        # Get selected filter
        filter_value = self.filter_var.get()
        
        # Sort exercises by name
        sorted_exercises = sorted(self.exercises.values(), key=lambda x: x.name)
        
        # Add exercises to the listbox
        for exercise in sorted_exercises:
            if filter_value == "All" or filter_value in [mg.value for mg in exercise.muscle_groups]:
                self.exercise_listbox.insert(tk.END, f"{exercise.name}")
                # Store the exercise ID as an item attribute
                self.exercise_listbox.itemconfig(tk.END, {"exercise_id": exercise.id})
    
    def _add_to_workout(self):
        selected_index = self.exercise_listbox.curselection()
        if not selected_index:
            messagebox.showinfo("Selection Required", "Please select an exercise first.")
            return
        
        # Get the selected exercise
        selected_index = selected_index[0]
        exercise_id = self.exercise_listbox.itemcget(selected_index, "exercise_id")
        exercise = self.exercises[exercise_id]
        
        # Add to current workout
        sets = self.sets_var.get()
        reps = self.reps_var.get()
        
        workout_item = {
            "exercise": exercise,
            "sets": sets,
            "reps": reps
        }
        
        self.current_workout.append(workout_item)
        
        # Update the workout listbox
        self.workout_listbox.insert(tk.END, f"{exercise.name} - {sets} sets x {reps} reps")
        
        # Validate the workout
        self._validate_workout()
    
    def _remove_from_workout(self):
        selected_index = self.workout_listbox.curselection()
        if not selected_index:
            messagebox.showinfo("Selection Required", "Please select a workout item to remove.")
            return
        
        # Remove from current workout
        selected_index = selected_index[0]
        self.current_workout.pop(selected_index)
        self.workout_listbox.delete(selected_index)
        
        # Validate the updated workout
        self._validate_workout()
    
    def _clear_workout(self):
        self.current_workout = []
        self.workout_listbox.delete(0, tk.END)
        
        # Update validation
        self.validation_text.config(state="normal")
        self.validation_text.delete(1.0, tk.END)
        self.validation_text.insert(tk.END, "Add exercises to create a workout...")
        self.validation_text.config(state="disabled")
    
    def _validate_workout(self):
        if not self.current_workout:
            self.validation_text.config(state="normal")
            self.validation_text.delete(1.0, tk.END)
            self.validation_text.insert(tk.END, "Add exercises to create a workout...")
            self.validation_text.config(state="disabled")
            return
        
        muscle_group_count = {}
        warnings = []
        
        for workout_item in self.current_workout:
            exercise = workout_item["exercise"]
            
            for muscle in exercise.muscle_groups:
                muscle_group_count[muscle.value] = muscle_group_count.get(muscle.value, 0) + 1
                
                if muscle_group_count[muscle.value] > 2:
                    warnings.append(f"Warning: {muscle.value} is being trained {muscle_group_count[muscle.value]} times. "
                                  f"This might lead to excessive fatigue.")
        
        # Update validation text
        self.validation_text.config(state="normal")
        self.validation_text.delete(1.0, tk.END)
        
        if warnings:
            self.validation_text.insert(tk.END, "WARNINGS:\n")
            for warning in warnings:
                self.validation_text.insert(tk.END, f"• {warning}\n")
        else:
            self.validation_text.insert(tk.END, "This workout has a good balance of muscle groups.\n")
        
        # Display muscle group distribution
        self.validation_text.insert(tk.END, "\nMuscle Group Distribution:\n")
        for muscle, count in muscle_group_count.items():
            self.validation_text.insert(tk.END, f"• {muscle}: {count} exercises\n")
            
        self.validation_text.config(state="disabled")
    
    def _start_workout(self):
        if not self.current_workout:
            messagebox.showinfo("Empty Workout", "Please add exercises to your workout first.")
            return
        
        # Initialize workout data
        self.current_exercise_index = 0
        self.current_set = 1
        
        # Enable and switch to the active workout tab
        self.tab_control.tab(3, state="normal")
        self.tab_control.select(3)
        
        # Update active workout UI
        self._update_active_workout_ui()
    
    def _setup_active_workout_tab(self):
        frame = ttk.Frame(self.tab_active_workout, padding="20")
        frame.pack(expand=True, fill="both")
        
        # Title
        self.workout_title_label = ttk.Label(frame, text="Current Workout", font=("Arial", 18, "bold"))
        self.workout_title_label.pack(pady=(0, 10))
        
        # Progress frame
        progress_frame = ttk.Frame(frame)
        progress_frame.pack(fill="x", pady=10)
        
        self.progress_label = ttk.Label(progress_frame, text="Exercise 0/0 - Set 0/0")
        self.progress_label.pack(side="left")
        
        self.overall_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate")
        self.overall_progress.pack(side="right", padx=10)
        
        # Exercise info frame
        exercise_frame = ttk.LabelFrame(frame, text="Current Exercise", padding=10)
        exercise_frame.pack(expand=True, fill="both", pady=10)
        
        # Exercise name and target
        self.exercise_name_label = ttk.Label(exercise_frame, text="Exercise Name", font=("Arial", 14, "bold"))
        self.exercise_name_label.pack(pady=(0, 10))
        
        self.exercise_target_label = ttk.Label(exercise_frame, text="Target: 0 sets x 0 reps")
        self.exercise_target_label.pack(pady=(0, 10))
        
        # Exercise description with scrollbar
        desc_frame = ttk.Frame(exercise_frame)
        desc_frame.pack(expand=True, fill="both", pady=10)
        
        desc_scroll = ttk.Scrollbar(desc_frame)
        desc_scroll.pack(side="right", fill="y")
        
        self.exercise_desc_text = tk.Text(desc_frame, wrap="word", height=5, yscrollcommand=desc_scroll.set)
        self.exercise_desc_text.pack(expand=True, fill="both")
        desc_scroll.config(command=self.exercise_desc_text.yview)
        
        # Set progress
        self.set_progress_frame = ttk.LabelFrame(frame, text="Set Progress", padding=10)
        self.set_progress_frame.pack(fill="x", pady=10)
        
        # Timer frame
        self.timer_frame = ttk.Frame(self.set_progress_frame)
        self.timer_frame.pack(fill="x", pady=10)
        
        self.timer_label = ttk.Label(self.timer_frame, text="00:00", font=("Arial", 24))
        self.timer_label.pack()
        
        # Start/Complete workout buttons
        self.workout_buttons_frame = ttk.Frame(frame)
        self.workout_buttons_frame.pack(fill="x", pady=20)
        
        self.start_set_button = ttk.Button(self.workout_buttons_frame, 
                                         text="Start Set", 
                                         command=self._start_set)
        self.start_set_button.pack(side="left", padx=5)
        
        self.complete_set_button = ttk.Button(self.workout_buttons_frame, 
                                            text="Complete Set", 
                                            command=self._complete_set,
                                            state="disabled")
        self.complete_set_button.pack(side="left", padx=5)
        
        self.cancel_workout_button = ttk.Button(self.workout_buttons_frame, 
                                             text="Cancel Workout", 
                                             command=self._cancel_workout)
        self.cancel_workout_button.pack(side="right", padx=5)
    
    def _update_active_workout_ui(self):
        if not self.current_workout:
            return
            
        if self.current_exercise_index >= len(self.current_workout):
            # Workout is complete
            self._complete_workout()
            return
            
        # Get current exercise info
        workout_item = self.current_workout[self.current_exercise_index]
        exercise = workout_item["exercise"]
        sets = workout_item["sets"]
        reps = workout_item["reps"]
        
        #Update progress labels
        # self.progress_label.config(
            # text=f"Exercise {self.current_exercise_index + 1}/len(self.current_workout)