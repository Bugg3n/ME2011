import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import calendar
from datetime import datetime, timedelta
import json

# This model is supposed to take the customer flow from model 1 and create a shift suggestion for one specific day.

# Adapted Python script for Model 2 - Structured Output for Model 3

OPENING_HOURS = ["08:00", "22:00"]
MIN_SHIFT_HOURS = 3
MAX_HOURS_WITHOUT_LUNCH = 5
MAX_HOURS_PER_DAY = 8

opening_hours = ["08:00", "22:00"]
sales_capacity_per_hour = 12  # A salesperson can handle 12 customers per hour
min_shift_hours = 3
max_hours_without_lunch = 5
earliest_lunch_time = 11
lunch_duration = 1 #in hours
max_hours_per_day = 8
store_id = "1"
day = "2025-01-22"

######################################################### Method 2 ####################################################################
 
def shift_cost(shift_length):
    cost = [1,1,1,0.85,0.85,0.75,0.75,0.5,0.5,2]
    #sum of cost for the length of the shift
    return sum(cost[:shift_length])

#Shift is a vector of 1s in the hours where the shift is active
def transaction_gain(shift, required_staffing, current_staffing):
    #Calculates the net gain of a shift based on required staffing.
    hours_worked = sum(shift)
    cost = shift_cost(hours_worked)

    gain = 0
    for i in range(len(shift)):
        if shift[i] == 1 and current_staffing[i] < required_staffing[i]:  
            gain += 1  # Gain only if it's actually needed

    return gain - cost

def is_sufficient_staffing(current_staffing, required_staffing):
    return all(c >= r for c, r in zip(current_staffing, required_staffing))
                

def construct_shifts(opening_hours, required_staffing, min_hours_per_day, max_hours_before_lunch, max_hours_per_day,visualize = False):
    #Finds an optimized schedule for store clerks iteratively instead of using recursion.

    # Ensure required staffing is at least 1 everywhere
    
    current_staffing = [0] * len(required_staffing)
    shifts = []  # Store valid shifts

    iteration_count = 0  # Debugging: Track loop iterations

    # While we do not meet required staffing, keep adding shifts
    while not is_sufficient_staffing(current_staffing, required_staffing):
        best_shift = None
        best_gain = float('-inf')

        # Generate possible shifts
        for shift_length in range(min_hours_per_day, max_hours_per_day + 1):
            for shift_start in range(len(required_staffing) - shift_length + 1):
                
                # Create a new shift
                new_shift = [0] * len(required_staffing)
                new_shift[shift_start:shift_start + shift_length] = [1] * shift_length

                # Calculate transaction gain (considering current staffing)
                t_gain = transaction_gain(new_shift, required_staffing, current_staffing)

                # Select the best shift based on gain (only if it helps)
                if t_gain > best_gain and any(a < b for a, b in zip(current_staffing, required_staffing)):
                    best_gain = t_gain
                    best_shift = new_shift

        # If no valid shift is found, break the loop (prevents infinite loop)
        if best_shift is None:
            print("No feasible shift found, stopping optimization.")
            break

        # Add best shift to the schedule
        shifts.append(best_shift)
        current_staffing = [a + b for a, b in zip(current_staffing, best_shift)]

        # Debugging: Print current staffing and shift selection
        
        iteration_count += 1

        # Safety stop: Prevent infinite loops by setting a max iteration count
        if iteration_count > len(required_staffing) * 2:
            print("Error: Maximum iterations reached. Possible infinite loop!")
            break
        
    
    cleaned_shifts = []
    for shift in shifts:
       
        shift_start_time = shift.index(1) + int(opening_hours[0].split(":")[0])
        shift_end_time = shift_start_time + shift.count(1)
        lunch_time = None
        cleaned_shifts.append({"start": f"{shift_start_time}:00", "end": f"{shift_end_time}:00", "lunch": lunch_time})
      
   
    
    if visualize:
        
        visualize_schedule(cleaned_shifts, required_staffing, "Initial Shifts")
   
    

    cleaned_shifts_with_lunch  = add_lunch_breaks(cleaned_shifts, required_staffing, current_staffing, opening_hours, max_hours_before_lunch)
    
    if visualize:
        
        visualize_schedule(cleaned_shifts_with_lunch, required_staffing, "Initial Shifts")

    cleaned_shifts_with_coverage = adjust_for_coverage(cleaned_shifts_with_lunch, required_staffing, opening_hours,min_hours_per_day)
    
    if visualize:
        
        visualize_schedule(cleaned_shifts_with_coverage, required_staffing, "Shifts with Lunch Breaks and Coverage")
    

    cleaned_shifts_with_coverage_optimized = optimize_shift_timings(cleaned_shifts_with_coverage, required_staffing, opening_hours,min_hours_per_day)

    if visualize:
        visualize_schedule(cleaned_shifts_with_coverage_optimized, required_staffing, "Optimized Shifts")
        input(cleaned_shifts_with_coverage_optimized)

    return cleaned_shifts_with_coverage


def add_lunch_breaks(shifts, required_staffing, current_staffing, opening_hours, max_hours_before_lunch):
    """Adds lunch breaks to shifts if they exceed max_hours_before_lunch, placing them optimally."""
    
    cleaned_shifts = []
    
    for shift in shifts:
        shift_start_time = int(shift["start"].split(":")[0])
        shift_end_time = int(shift["end"].split(":")[0])
        shift_length = shift_end_time - shift_start_time

        lunch_time = "None"

        if shift_length > max_hours_before_lunch:
            middle_section = range(shift_start_time + (shift_length // 2) -2, shift_start_time + (shift_length // 2) + 2)
            
            middle_section = [h for h in middle_section if shift_start_time <= h < shift_end_time and h >= earliest_lunch_time]

            best_lunch_hour = None
            max_overstaffing = -1

            for hour in middle_section:
                staffing_index = hour - int(opening_hours[0].split(":")[0])
                if current_staffing[staffing_index] > required_staffing[staffing_index]:  # Overstaffed hour
                    overstaffing_amount = current_staffing[staffing_index] - required_staffing[staffing_index]
                    if overstaffing_amount > max_overstaffing:
                        max_overstaffing = overstaffing_amount
                        best_lunch_hour = hour

            if best_lunch_hour:
                lunch_time = f"{best_lunch_hour}:00"
            else:
                for hour in middle_section:
                    if lunch_time != "None":
                        break
                    for other_shifts in shifts:
                        other_shift_start_time = int(other_shifts["start"].split(":")[0])
                        other_shift_end_time = int(other_shifts["end"].split(":")[0])
                        other_shifts_length = other_shift_end_time - other_shift_start_time
                        
                        if hour == other_shift_end_time +1 and other_shifts_length < max_hours_before_lunch:                              
                            lunch_time = f"{hour-1}:00"
                            
                            
                            other_shift_end_time += 1
                            shifts[shifts.index(other_shifts)]["end"] = f"{other_shift_end_time}:00"
                            break
                        elif hour == other_shift_start_time -1 and other_shifts_length < max_hours_before_lunch:
                            lunch_time = f"{hour}:00"
                            other_shift_start_time -= 1
                            shifts[shifts.index(other_shifts)]["start"] = f"{other_shift_start_time}:00"
                if lunch_time == "None":
                    lunch_time = f"{middle_section[0]}:00"            

        cleaned_shifts.append({"start": shift["start"], "end": shift["end"], "lunch": lunch_time})

    return cleaned_shifts


def adjust_for_coverage(shifts, required_staffing, opening_hours, min_hours_per_day):
    """
    Ensures all hours are fully covered, extending shifts or adding new ones optimally.
    Uses transaction_gain to determine the best adjustment.
    """

    current_staffing = [0] * len(required_staffing)

    # Convert shift start/end times to hour indices for tracking
    shift_intervals = []
    for shift in shifts:
        start_idx = int(shift["start"].split(":")[0]) - int(opening_hours[0].split(":")[0])
        end_idx = int(shift["end"].split(":")[0]) - int(opening_hours[0].split(":")[0])
        lunch_idx = None if shift["lunch"] == "None" else int(shift["lunch"].split(":")[0]) - int(opening_hours[0].split(":")[0])
        
        for i in range(start_idx, end_idx):
            if i != lunch_idx:  # Do not count lunch break as coverage
                current_staffing[i] += 1

        shift_intervals.append((start_idx, end_idx, lunch_idx))

    # Identify coverage gaps and decide whether to extend a shift or add a new one
    for i in range(len(required_staffing)):
        if current_staffing[i] < required_staffing[i]:  # Gap detected
            best_option = None
            best_gain = float('-inf')

            # **Option 1: Extend an existing shift**
            for j, (start_idx, end_idx, lunch_idx) in enumerate(shift_intervals):
                if start_idx <= i < end_idx and (lunch_idx is None or lunch_idx != i):
                    # Simulate extending the shift
                    extended_shift = shifts[j].copy()
                    extended_shift["end"] = f"{int(extended_shift['end'].split(':')[0]) + 1}:00"
                    
                    # Compute gain
                    extended_gain = transaction_gain([1] * (end_idx - start_idx + 1), required_staffing, current_staffing)

                    if extended_gain > best_gain:
                        best_gain = extended_gain
                        best_option = ("extend", j)

            # **Option 2: Create a new shift**
            new_shift_start = i + int(opening_hours[0].split(":")[0])
            new_shift_end = new_shift_start + min_hours_per_day
            new_shift = {"start": f"{new_shift_start}:00", "end": f"{new_shift_end}:00", "lunch": "None"}

            # Compute gain
            new_shift_gain = transaction_gain([1] * min_hours_per_day, required_staffing, current_staffing)

            if new_shift_gain > best_gain:
                best_gain = new_shift_gain
                best_option = ("new", new_shift)

            # Apply the best option
            if best_option[0] == "extend":
                shifts[best_option[1]]["end"] = f"{int(shifts[best_option[1]]['end'].split(':')[0]) + 1}:00"
            else:
                shifts.append(best_option[1])

            # Update staffing after the change
            for k in range(i, i + min_hours_per_day):
                if k < len(current_staffing):
                    current_staffing[k] += 1

    return shifts

def optimize_shift_timings(shifts, required_staffing, opening_hours,min_hours_per_day):
    
    optimized_shifts = []
    opening_time = int(opening_hours[0].split(":")[0])
    current_staffing = [0] * len(required_staffing)


    for shift in shifts:
        start_time = int(shift["start"].split(":")[0])
        end_time = int(shift["end"].split(":")[0])
        lunch_time = shift["lunch"]

        for i in range(0, len(required_staffing)):
            if shift["lunch"] == None or shift["lunch"] == "None":
                
                if i + opening_time >= start_time and i + opening_time < end_time:
                    current_staffing[i] += 1
            else:
                if i + opening_time >= start_time and i + opening_time < end_time and i + opening_time != int(lunch_time.split(":")[0]):
                    current_staffing[i] += 1
            
    for shift in shifts:
        start_time = int(shift["start"].split(":")[0])
        end_time = int(shift["end"].split(":")[0])-1
        #check if the start time or end time can be moved because of overstaffing
        if shift["lunch"] == None or shift["lunch"] == "None":
            if current_staffing[start_time - opening_time] > required_staffing[start_time - opening_time] and end_time - start_time > min_hours_per_day:
                start_time += 1
                current_staffing[start_time - opening_time] -= 1
                shifts[shifts.index(shift)]["start"] = f"{start_time}:00"
            elif current_staffing[end_time - opening_time] > required_staffing[end_time - opening_time] and end_time - start_time > min_hours_per_day:
                end_time -= 1
                current_staffing[end_time - opening_time] -= 1
                shifts[shifts.index(shift)]["end"] = f"{end_time}:00"
    return shifts
        
        
 
##########################################################################################################################################
# TODO
# Move all visualization to visualize.py

def visualize_schedule(schedule, staff_needed, title= "placeholder"):
    """
    Visualizes a work schedule using a horizontal bar chart with an additional "Staff Needed" metric,
    and highlights lunch breaks.

    Parameters:
    schedule (list of dict): A list of shifts, each represented as a dictionary 
                             with 'start', 'end', and 'lunch' time strings (e.g., '9:00').
    staff_needed (list of int): A list of values representing staff requirements over time.
    """
    
    def time_to_float(time_str):
        """Convert time string (e.g., '9:00') to float (e.g., 9.0)."""
        if time_str == "None" or time_str is None:
            return None  # No lunch break
        h, m = map(int, time_str.split(':'))
        return h + m / 60

    # Extract shift details
    shift_labels = [f"Shift {i+1}" for i in range(len(schedule))]
    shift_start = [time_to_float(shift['start']) for shift in schedule]
    shift_end = [time_to_float(shift['end']) for shift in schedule]
    shift_duration = [end - start for start, end in zip(shift_start, shift_end)]
    lunch_times = [time_to_float(shift['lunch']) for shift in schedule]

    # Define time labels based on the staff_needed list
    time_labels = np.arange(8, 8 + len(staff_needed), 1)  # Time from 8:00 onward

    # Create figure
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot work schedule as horizontal bars
    y_positions = np.arange(len(schedule))
    ax1.barh(y_positions, shift_duration, left=shift_start, height=0.6, color='skyblue', edgecolor='black', label="Shifts")

    # Highlight lunch breaks in gray
    for i, lunch_time in enumerate(lunch_times):
        if lunch_time is not None:
            ax1.barh(y_positions[i], 1, left=lunch_time, height=0.6, color='gray', label="Lunch Break" if i == 0 else "")
            ax1.text(lunch_time + 0.1, y_positions[i], 'Lunch', va='center', ha='left', color='black', fontsize=10, fontweight='bold')

    # Labels for shifts
    ax1.set_yticks(y_positions)
    ax1.set_yticklabels(shift_labels)
    ax1.set_xlabel("Time")
    ax1.set_title(title)

    # Set x-axis to display time labels
    ax1.set_xticks(time_labels)
    ax1.set_xticklabels([f"{int(t)}:00" for t in time_labels])

    # Create a secondary y-axis for the "Staff Needed" metric
    ax2 = ax1.twinx()
    ax2.set_ylim(ax1.get_ylim())  # Align y-axis limits
    ax2.bar(time_labels + 0.5, staff_needed, width=0.4, alpha=0.6, color='red', label="Staff Needed")
    ax2.set_ylabel("Staff Needed")

    # Legends
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.show()

# Function to create output for Model 3
def create_output(opening_hours, staffing_per_hour, shifts, store_id, day):
  
    output = {
        "day": day,
        "store_id": store_id,
        "opening_hours": opening_hours,
        "staffing_per_hour": {
            f"{8 + i}:00": staff for i, staff in enumerate(staffing_per_hour)
        },
        "shift_suggestions": shifts,
        "metadata": {
            "delivery_day": True,  # Example metadata
        }
    }
    return output


def generate_monthly_schedule(year, month, store_id, monthly_staffing, 
                              min_shift_hours=MIN_SHIFT_HOURS, 
                              max_hours_without_lunch=MAX_HOURS_WITHOUT_LUNCH, 
                              max_hours_per_day=MAX_HOURS_PER_DAY, 
                              visualize=False):
    """
    Generates a full month's shift schedule using staffing data passed from main.py.
    """

    # Get number of days in the month
    num_days = calendar.monthrange(year, month)[1]

    # Storage for full month schedule
    monthly_schedule = {}

    # Iterate over each day
    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"

        print(f"📅 Generating shifts for {date_str}...")

        # Get staffing per hour for this day from input data
        staffing_per_hour = monthly_staffing.get(date_str, [])

        # Generate shifts for this day
        daily_shifts = construct_shifts(
            opening_hours=OPENING_HOURS,
            required_staffing=staffing_per_hour,
            min_hours_per_day=min_shift_hours,
            max_hours_before_lunch=max_hours_without_lunch,
            max_hours_per_day=max_hours_per_day,
            visualize=visualize
        )

        # Store the results
        monthly_schedule[date_str] = {
            "staffing_per_hour": staffing_per_hour,
            "shifts": daily_shifts
        }

    return monthly_schedule

if __name__ == "__main__":
    # Example usage: Generate schedule for March 2025
    year, month = 2025, 3
    store_id = "1"

    full_month_schedule = generate_monthly_schedule(year, month, store_id, visualize=True)

    # Save schedule to a JSON file for easy reference
    with open(f"schedule_{year}_{month}.json", "w") as f:
        json.dump(full_month_schedule, f, indent=4)

    print(f"📅 Monthly schedule saved to schedule_{year}_{month}.json")