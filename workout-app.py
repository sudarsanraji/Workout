import time
import json
import os
from datetime import datetime
from enum import Enum

class MuscleGroup(str, Enum):
    CHEST = "Chest"
    BACK = "Back"
    SHOULDERS = "Shoulders"
    BICEPS = "Biceps"
    TRICEPS = "Triceps"
    LEGS = "Legs"
    CORE = "Core"

class Exercise:
    def __init__(self, id, name, muscle_groups, description, equipment_needed=None, difficulty_level="beginner", recommended_rest=60):
        self.id = id
        self.name = name
        self.muscle_groups = muscle_groups
        self.description = description
        self.equipment_needed = equipment_needed
        self.difficulty_level = difficulty_level
        self.recommended_rest = recommended_rest

class WorkoutApp:
    def __init__(self):
        self.exercises = self._load_exercise_database()
        self.workout_history = self._load_workout_history()
        
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
        except Exception as e:
            print(f"Error loading exercise database: {e}")
            print("Using default exercise database.")
        
        return default_exercises
    
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
    
    def display_exercises_by_muscle_group(self):
        muscle_groups = {mg.value: [] for mg in MuscleGroup}
        
        for ex in self.exercises.values():
            for mg in ex.muscle_groups:
                muscle_groups[mg.value].append(ex.name)
        
        print("\n=== EXERCISES BY MUSCLE GROUP ===")
        for mg, exercises in muscle_groups.items():
            if exercises:
                print(f"\n{mg}:")
                for i, ex in enumerate(exercises, 1):
                    print(f"  {i}. {ex}")
    
    def list_all_exercises(self):
        print("\n=== ALL EXERCISES ===")
        for i, ex in enumerate(self.exercises.values(), 1):
            muscle_groups = ", ".join([mg.value for mg in ex.muscle_groups])
            print(f"{i}. {ex.name} - {muscle_groups}")
            print(f"   Description: {ex.description}")
            print(f"   Difficulty: {ex.difficulty_level}")
            print(f"   Equipment: {ex.equipment_needed or 'None'}")
            print(f"   Rest time: {ex.recommended_rest} seconds")
            print()
    
    def create_workout(self):
        print("\n=== CREATE WORKOUT ===")
        workout_plan = []
        
        # Convert exercises dictionary to list for easier indexing
        exercise_list = list(self.exercises.values())
        
        while True:
            print("\nAvailable exercises:")
            for i, ex in enumerate(exercise_list, 1):
                muscle_groups = ", ".join([mg.value for mg in ex.muscle_groups])
                print(f"{i}. {ex.name} - {muscle_groups}")
            
            try:
                choice = input("\nEnter exercise number (or 'done' to finish): ")
                if choice.lower() == 'done':
                    break
                
                ex_index = int(choice) - 1
                if ex_index < 0 or ex_index >= len(exercise_list):
                    print("Invalid exercise number!")
                    continue
                
                selected_exercise = exercise_list[ex_index]
                
                sets = int(input(f"How many sets of {selected_exercise.name}? "))
                reps = int(input(f"How many reps per set? "))
                
                workout_plan.append({
                    "exercise": selected_exercise,
                    "sets": sets,
                    "reps": reps
                })
                
                print(f"Added {selected_exercise.name} to workout.")
                
            except ValueError:
                print("Please enter a valid number.")
        
        if not workout_plan:
            print("Workout is empty. Returning to main menu.")
            return
        
        # Validate workout
        self.validate_workout(workout_plan)
        
        # Start workout
        self.start_workout(workout_plan)
    
    def validate_workout(self, workout_plan):
        print("\n=== WORKOUT VALIDATION ===")
        muscle_group_count = {}
        warnings = []
        
        for workout_item in workout_plan:
            exercise = workout_item["exercise"]
            
            for muscle in exercise.muscle_groups:
                muscle_group_count[muscle.value] = muscle_group_count.get(muscle.value, 0) + 1
                
                if muscle_group_count[muscle.value] > 2:
                    warnings.append(f"Warning: {muscle.value} is being trained {muscle_group_count[muscle.value]} times. "
                                  f"This might lead to excessive fatigue.")
        
        print("\nMuscle Group Distribution:")
        for muscle, count in muscle_group_count.items():
            print(f"  {muscle}: {count} exercises")
        
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  {warning}")
            
            proceed = input("\nDo you want to proceed with this workout? (y/n): ")
            return proceed.lower() == 'y'
        else:
            print("\nThis workout has a good balance of muscle groups.")
            return True
    
    def start_timer(self, duration):
        print(f"\nRest timer: {duration} seconds")
        start_time = time.time()
        try:
            while True:
                elapsed = time.time() - start_time
                remaining = duration - int(elapsed)
                
                if remaining <= 0:
                    print("\nRest time complete!")
                    break
                
                mins, secs = divmod(remaining, 60)
                timer_display = f"\rTime remaining: {mins:02d}:{secs:02d}"
                print(timer_display, end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nTimer stopped.")
            return
    
    def start_workout(self, workout_plan):
        print("\n=== STARTING WORKOUT ===")
        workout_id = f"workout_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = time.time()
        completed_exercises = []
        
        for workout_item in workout_plan:
            exercise = workout_item["exercise"]
            planned_sets = workout_item["sets"]
            planned_reps = workout_item["reps"]
            
            print(f"\n--- {exercise.name} ---")
            print(f"Target: {planned_sets} sets x {planned_reps} reps")
            print(f"Description: {exercise.description}")
            if exercise.equipment_needed:
                print(f"Equipment needed: {exercise.equipment_needed}")
            
            exercise_completion = {
                "exercise_id": exercise.id,
                "exercise_name": exercise.name,
                "planned_sets": planned_sets,
                "planned_reps": planned_reps,
                "completed_sets": 0,
                "actual_reps": [],
                "difficulty_ratings": []
            }
            
            for current_set in range(1, planned_sets + 1):
                input(f"\nPress ENTER to start set {current_set}/{planned_sets}...")
                
                set_start_time = time.time()
                input("Performing exercise... Press ENTER when completed.")
                set_end_time = time.time()
                
                try:
                    actual_reps = int(input(f"How many reps did you complete? (target: {planned_reps}): "))
                    difficulty = int(input("Rate difficulty (1-5): "))
                    
                    # Validate input
                    if difficulty < 1 or difficulty > 5:
                        difficulty = 3
                        print("Invalid difficulty rating, setting to 3.")
                        
                except ValueError:
                    print("Invalid input, using default values.")
                    actual_reps = planned_reps
                    difficulty = 3
                
                exercise_completion["completed_sets"] += 1
                exercise_completion["actual_reps"].append(actual_reps)
                exercise_completion["difficulty_ratings"].append(difficulty)
                
                # Rest timer between sets
                if current_set < planned_sets:
                    self.start_timer(exercise.recommended_rest)
            
            completed_exercises.append(exercise_completion)
        
        end_time = time.time()
        total_time = int(end_time - start_time)
        
        # Calculate average difficulty
        total_difficulty = 0
        total_ratings = 0
        for exercise in completed_exercises:
            total_difficulty += sum(exercise["difficulty_ratings"])
            total_ratings += len(exercise["difficulty_ratings"])
        
        average_difficulty = total_difficulty / total_ratings if total_ratings > 0 else 0
        
        # Save workout to history
        workout_summary = {
            "date": datetime.now().isoformat(),
            "total_time": total_time,
            "exercises": completed_exercises,
            "average_difficulty": average_difficulty
        }
        
        self.workout_history[workout_id] = workout_summary
        self._save_workout_history()
        
        # Display workout summary
        print("\n=== WORKOUT COMPLETED ===")
        print(f"Total time: {total_time // 60} mins {total_time % 60} secs")
        print(f"Average difficulty: {average_difficulty:.1f}/5")
        
        for exercise in completed_exercises:
            print(f"\n{exercise['exercise_name']}:")
            print(f"  Planned: {exercise['planned_sets']} sets x {exercise['planned_reps']} reps")
            print(f"  Completed: {exercise['completed_sets']} sets")
            print(f"  Actual reps: {exercise['actual_reps']}")
            print(f"  Difficulty ratings: {exercise['difficulty_ratings']}")
    
    def view_workout_history(self):
        if not self.workout_history:
            print("\nNo workout history available.")
            return
        
        print("\n=== WORKOUT HISTORY ===")
        
        # Sort workouts by date (newest first)
        sorted_workouts = sorted(
            self.workout_history.items(),
            key=lambda x: x[1]["date"],
            reverse=True
        )
        
        for workout_id, workout in sorted_workouts:
            date_obj = datetime.fromisoformat(workout["date"])
            formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\nWorkout ID: {workout_id}")
            print(f"Date: {formatted_date}")
            print(f"Duration: {workout['total_time'] // 60} mins {workout['total_time'] % 60} secs")
            print(f"Average difficulty: {workout['average_difficulty']:.1f}/5")
            
            print("\nExercises:")
            for exercise in workout["exercises"]:
                print(f"  • {exercise['exercise_name']}: {exercise['completed_sets']} sets, {sum(exercise['actual_reps'])} total reps")
            
            print("-" * 50)
    
    def main_menu(self):
        while True:
            print("\n=== WORKOUT APP MENU ===")
            print("1. List All Exercises")
            print("2. Browse Exercises by Muscle Group")
            print("3. Create and Start Workout")
            print("4. View Workout History")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":
                self.list_all_exercises()
            elif choice == "2":
                self.display_exercises_by_muscle_group()
            elif choice == "3":
                self.create_workout()
            elif choice == "4":
                self.view_workout_history()
            elif choice == "5":
                print("Thank you for using the Workout App. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    app = WorkoutApp()
    app.main_menu()
