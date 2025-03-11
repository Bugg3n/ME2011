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
  

# Function to create shifts with longer shifts and lunch breaks
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
                    if shifts[k][1] < max_hours_per_day:
                        shifts[k][1] += 1
                        current_staffing[i] += 1
                        
                    elif shifts[k][1] == max_hours_per_day and shift_end == False:
                        
                       
                        finished_shifts.append(shifts[k])
                        shift_end = True
                        
            
            #if the required staffing is the same as the previous hour and the shift has started
            elif required_staffing[i] == required_staffing[i-1] and shift_start == True:
              
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


        


def clean_shifts(opening_hours ,shifts):
    cleaned_shifts = []

    
    closing_hour = opening_hours[1].split(":")[0]
    if shifts[-2][1] > shifts[-1][1]:
        difference = shifts[-2][1] - shifts[-1][1]
        half_difference = difference // 2  # Floor division to ensure an integer
        remainder = difference % 2  # Get remainder if difference is odd

        shifts[-2][1] -= half_difference + remainder  # Ensure no rounding errors
        shifts[-1][1] += half_difference 



        



    for shift in shifts:
        cleaned_shifts.append({"start": f"{shift[0]}:00", "end": f"{shift[0]+shift[1]}:00", "lunch": f"{shift[0]+shift[2]}:00"})
    return cleaned_shifts


  
def visualize_schedule(schedule):
    """
    Visualizes a work schedule using a horizontal bar chart.

    Parameters:
    schedule (list of dict): A list of shifts, each represented as a dictionary 
                             with 'start' and 'end' time strings (e.g., '9:00').
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

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))

    # Plot each shift as a horizontal bar
    y_positions = np.arange(len(schedule))
    ax.barh(y_positions, shift_duration, left=shift_start, height=0.6, color='skyblue', edgecolor='black')

    # Add labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(shift_labels)
    ax.set_xlabel("Time")
    ax.set_title("Work Schedule Visualization")

    # Set x-axis to display time labels
    time_labels = np.arange(8, 23, 1)  # Time from 8:00 to 22:00
    ax.set_xticks(time_labels)
    ax.set_xticklabels([f"{int(t)}:00" for t in time_labels])

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
    visualize_schedule(shifts)
    print(shifts)
    
    #return create_output(opening_hours, staffing_per_hour, shifts, store_id, day)

if __name__ == "__main__":  
    main(opening_hours, store_id, day, sales_capacity_per_hour, min_shift_hours, max_hours_without_lunch, max_hours_per_day, lunch_duration)
  
