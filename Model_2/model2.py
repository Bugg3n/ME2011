import sys
import os
import matplotlib.pyplot as plt
import numpy as np


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Model_1 import model1

# This model is supposed to take the customer flow from model 1 and create a shift suggestion for one specific day.

# Adapted Python script for Model 2 - Structured Output for Model 3

# Input: Customer flow per hour and opening hours
#customer_flow_per_hour = [5, 8, 12, 20, 25, 30, 35, 40, 38, 32, 25, 20, 15, 10]
opening_hours = ["08:00", "22:00"]
sales_capacity_per_hour = 12  # A salesperson can handle 12 customers per hour
min_shift_hours = 3
max_hours_without_lunch = 5
lunch_duration = 1 #in hours
max_hours_per_day = 8
store_id = "1"
day = "2025-01-22"


""" # Function to create shifts
def create_shifts(opening_hours,staffing, min_hours, max_hours_wo_lunch, max_hours):
    shifts = []
    start_time = 8  # Start time in hours
    shift_start = start_time
    staffing_for_shift = 0
    hours_in_shift = 0

    for hour, demand in enumerate(staffing, start=start_time):
        if hours_in_shift == 0:
            staffing_for_shift = demand
            shift_start = hour

        hours_in_shift += 1

        # Create a shift if max hours are reached or demand changes
        if hours_in_shift == max_hours or demand != staffing_for_shift:
            shifts.append({"start": f"{shift_start}:00", "end": f"{hour}:00", "staff_needed": staffing_for_shift})
            shift_start = hour
            staffing_for_shift = demand
            hours_in_shift = 1  # Reset for the next shift

    # Add the last shift if any remain
    if hours_in_shift > 0:
        shifts.append({"start": f"{shift_start}:00", "end": f"{hour + 1}:00", "staff_needed": staffing_for_shift})

    print(shifts)
    return shifts


 """
  

""" # Function to create shifts with longer shifts 
def create_shifts(opening_hours,required_staffing, min_hours_per_day, max_hours_wo_lunch,max_hours_per_day):
    shifts = []
    
    finished_shifts = []
    start_time = 8  # Start time in hours
    current_staffing = [0] * len(required_staffing)
    sufficient_staffing = False
    k = 0

    #Condition to see if demand for salespeople is met
    while sufficient_staffing == False:

        shift_start = False
        shift_end = False
        
        # we handle one open hour at a time
        for i in range(len(required_staffing)):
            start_time = i +8

            

            #Check if the required staffing is met for the hour of interest
            if current_staffing[i] < required_staffing[i] :
               
                #if the required staffing is higher than the previous hour and the shift has not started it is started
                if shift_start == False:
                    shift_start = True
                    
                    current_staffing[i] += 1
                    shifts.append([start_time,1,2])    #the format is [start_time, current duration, hours before lunch]

                
                #if the required staffing is higher than the previous hour and the shift has started we extend it
                elif shift_start == True:
                    if shifts[k][1] < max_hours_per_day and shift_end == False:
                        shifts[k][1] += 1
                        
                        current_staffing[i] += 1
                        
                        
                    elif shifts[k][1] == max_hours_per_day and shift_end == False:
                        
                       
                        finished_shifts.append(shifts[k])
                        shift_end = True

            
                        
            
            #if the required staffing is the same as the previous hour and the shift has started
            elif required_staffing[i] == required_staffing[i-1] and shift_start == True and shift_end == False:
              
              
                #we can extend a shift if the max hours per day is not reached
                if shifts[k][1] < max_hours_per_day:
                    shifts[k][1] += 1
                 
                    current_staffing[i] += 1
                    
                    

                #or we can end the shift if the max hours per day is reached
                elif shifts[k][1] == max_hours_per_day and shift_end == False:       
                    finished_shifts.append(shifts[k])
              
                    shift_end = True

            #if the opening hours are over and the shift has started and needs to be ended
            if i == len(required_staffing)-1 and shift_end == False:
                shift_end = True
                finished_shifts.append(shifts[k])
             
                
        k += 1

        #Check if the required staffing is met
        sufficient_staffing = True
        for i in range(len(required_staffing)):
            if current_staffing[i] < required_staffing[i]:
                sufficient_staffing = False
                break

    
    
    #A function that removes the lunch break and adds it to the shift, and that cleans the schedule from the back
    cleaned_shifts = clean_shifts(opening_hours,finished_shifts)
    print(current_staffing)
    input(required_staffing)
    return cleaned_shifts
 """

# Function to create shifts with longer shifts and lunch breaks
def create_shifts(opening_hours,required_staffing, min_hours_per_day, max_hours_wo_lunch,max_hours_per_day):
    shifts = []
    
    finished_shifts = []
    start_time = 8  # Start time in hours
    current_staffing = [0] * len(required_staffing)
    sufficient_staffing = False
    k = 0

    #To make sure that the required staffing is never 0
    required_staffing = list(map(lambda x: 1 if x == 0 else x, required_staffing))

    #Condition to see if demand for salespeople is met
    while sufficient_staffing == False:

        shift_start = False
        shift_end = False
        
        # we handle one open hour at a time
        for i in range(len(required_staffing)):
            start_time = i +8

            

            #Check if the required staffing is met for the hour of interest
            if current_staffing[i] < required_staffing[i] :
                #print("check")
                #if the required staffing is higher than the previous hour and the shift has not started it is started
                if shift_start == False:
                    shift_start = True
                    
                    current_staffing[i] += 1
                    shifts.append([start_time,1,2])    #the format is [start_time, current duration, hours before lunch]

                
                #if the required staffing is higher than the previous hour and the shift has started we extend it
                elif shift_start == True:
                    if shifts[k][1] < max_hours_per_day and shift_end == False:
                        shifts[k][1] += 1
                       
                        
                        current_staffing[i] += 1
                        
                        
                    elif shifts[k][1] == max_hours_per_day and shift_end == False:
                        
                        
                        finished_shifts.append(shifts[k])
                        #input(shifts[k])
                        shift_end = True
            elif current_staffing[i] >= required_staffing[i] and shift_start == True:
                
                if shifts[k][1] >= min_hours_per_day and shift_end == False:
                        finished_shifts.append(shifts[k])
                        #input(shifts[k])
                        shift_end = True

                elif shifts[k][1] < min_hours_per_day and shift_end == False:
                    shifts[k][1] += 1
                    current_staffing[i] += 1
                        
                        
                elif shifts[k][1] == max_hours_per_day and shift_end == False:
                        
                        
                    finished_shifts.append(shifts[k])
                        #input(shifts[k])
                    shift_end = True

            
                        
            

            #if the opening hours are over and the shift has started and needs to be ended
            if i == len(required_staffing)-1 and shift_end == False:
                shift_end = True
                #print(shifts[k], start_time)
                finished_shifts.append(shifts[k])

         
        finished_shifts       
        k += 1

        #Check if the required staffing is met
        sufficient_staffing = True
        for i in range(len(required_staffing)):
            if current_staffing[i] < required_staffing[i]:
                sufficient_staffing = False
                break

    
    
    #A function that removes the lunch break and adds it to the shift, and that cleans the schedule from the back
    cleaned_shifts = clean_shifts(opening_hours,finished_shifts)

    return cleaned_shifts
       


def clean_shifts(opening_hours ,shifts):
    cleaned_shifts = []

    
    closing_hour = opening_hours[1].split(":")[0]
    """ if shifts[-2][1] > shifts[-1][1]:
        difference = shifts[-2][1] - shifts[-1][1]
        half_difference = difference // 2  # Floor division to ensure an integer
        remainder = difference % 2  # Get remainder if difference is odd

        shifts[-2][1] -= half_difference + remainder  # Ensure no rounding errors
        shifts[-1][1] += half_difference 

 """
    for shift in shifts:
        cleaned_shifts.append({"start": f"{shift[0]}:00", "end": f"{shift[0]+shift[1]}:00", "lunch": f"{shift[0]+shift[2]}:00"})
    return cleaned_shifts




######################################################### Method 2 ####################################################################

def shift_cost(shift_length):
    cost = [1,1,1,0.85,0.85,0.75,0.75,0.5,2,2]
    #sum of cost for the length of the shift
    return sum(cost[:shift_length])



#Shift is a vector of 1s in the hours where the shift is active
def transaction_gain(shift, required_staffing, current_staffing):
    """Calculates the net gain of a shift based on required staffing."""
    hours_worked = sum(shift)
    cost = shift_cost(hours_worked)

    gain = 0
    for i in range(len(shift)):
        if shift[i] == 1 and current_staffing[i] < required_staffing[i]:  
            gain += 1  # Gain only if it's actually needed

    return gain - cost

def is_sufficient_staffing(current_staffing, required_staffing):
    return all(c >= r for c, r in zip(current_staffing, required_staffing))
                

def construct_shifts(opening_hours, required_staffing, min_hours_per_day, max_hours_before_lunch, max_hours_per_day):
    """Finds an optimized schedule for store clerks iteratively instead of using recursion."""

    # Ensure required staffing is at least 1 everywhere
    required_staffing = [max(1, r) for r in required_staffing]
    
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
        lunch_time = "TBD"
        cleaned_shifts.append({"start": f"{shift_start_time}:00", "end": f"{shift_end_time}:00", "lunch": lunch_time})
    print(cleaned_shifts)
    
    return cleaned_shifts
##########################################################################################################################################333
  
def visualize_schedule(schedule, staff_needed):
    """
    Visualizes a work schedule using a horizontal bar chart with an additional "Staff Needed" metric.

    Parameters:
    schedule (list of dict): A list of shifts, each represented as a dictionary 
                             with 'start' and 'end' time strings (e.g., '9:00').
    staff_needed (list of int): A list of values representing staff requirements over time.
    """
    
    def time_to_float(time_str):
        """Convert time string (e.g., '9:00') to float (e.g., 9.0)."""
        h, m = map(int, time_str.split(':'))
        return h + m / 60

    # Extract shift details
    shift_labels = [f"Shift {i+1}" for i in range(len(schedule))]
    shift_start = [time_to_float(shift['start']) for shift in schedule]
    shift_end = [time_to_float(shift['end']) for shift in schedule]
    shift_duration = [end - start for start, end in zip(shift_start, shift_end)]

    # Define time labels based on the staff_needed list
    time_labels = np.arange(8, 8 + len(staff_needed), 1)  # Time from 8:00 onward

    # Create figure
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot work schedule as horizontal bars
    y_positions = np.arange(len(schedule))
    ax1.barh(y_positions, shift_duration, left=shift_start, height=0.6, color='skyblue', edgecolor='black', label="Shifts")

    # Labels for shifts
    ax1.set_yticks(y_positions)
    ax1.set_yticklabels(shift_labels)
    ax1.set_xlabel("Time")
    ax1.set_title("Work Schedule Visualization with Staff Needed")

    # Set x-axis to display time labels
    ax1.set_xticks(time_labels)
    ax1.set_xticklabels([f"{int(t)}:00" for t in time_labels])

    # Create a secondary y-axis for the "Staff Needed" metric
    ax2 = ax1.twinx()
    ax2.set_ylim(ax1.get_ylim())  # Align y-axis limits
    ax2.bar(time_labels, staff_needed, width=0.4, alpha=0.6, color='red', label="Staff Needed")
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


def main(opening_hours, store_id, day, 
         sales_capacity_per_hour=12, min_shift_hours=3, 
         max_hours_without_lunch=5, max_hours_per_day=8, 
         lunch_duration=1):

    #uses queueing theory to model the number of customers in a store over time and returning the demanded number of employees per hour
    staffing_per_hour = model1.main(store_id,day)

    shifts = create_shifts(opening_hours,staffing_per_hour, min_shift_hours, max_hours_without_lunch, max_hours_per_day)
    visualize_schedule(shifts,staffing_per_hour)
    print(shifts)
    best_shift = construct_shifts(opening_hours,staffing_per_hour, min_shift_hours, max_hours_without_lunch, max_hours_per_day)
    visualize_schedule(best_shift,staffing_per_hour)
    
    #return create_output(opening_hours, staffing_per_hour, shifts, store_id, day)

if __name__ == "__main__":  
    main(opening_hours, store_id, day, sales_capacity_per_hour, min_shift_hours, max_hours_without_lunch, max_hours_per_day, lunch_duration)
  
