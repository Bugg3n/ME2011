import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Model_1 import model1

# This model is supposed to take the customer flow from model 1 and create a shift suggestion for one specific day.

# Adapted Python script for Model 2 - Structured Output for Model 3

# Input: Customer flow per hour and opening hours
#customer_flow_per_hour = [5, 8, 12, 20, 25, 30, 35, 40, 38, 32, 25, 20, 15, 10]
opening_hours = ["08:00", "21:00"]
sales_capacity_per_hour = 12  # A salesperson can handle 12 customers per hour
min_shift_hours = 3
max_hours_without_lunch = 5
max_hours_per_day = 8
store_id = "1"
day = "2025-01-22"


# Function to create shifts
def create_shifts(staffing, min_hours, max_hours):
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

    return shifts

# Run the model logic
#staffing_per_hour = calculate_staffing(customer_flow_per_hour, sales_capacity_per_hour)
staffing_per_hour = model1.main()
shifts = create_shifts(staffing_per_hour, min_shift_hours, max_hours_without_lunch)

# Create the structured output for Model 3
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

print(output)
