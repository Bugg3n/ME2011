from employees import Employee
# from visualize import visualize_schedule
from datetime import date
from load_employees import load_employees

# This part of the code is supposed to take the shift suggestions from part 2 and then create the actual schedule. 
# It also visualizes the schedule

employees = load_employees()


for emp in employees:
    print(emp)

shift_date = "2025-03-15" # Alice should be unavailable
shift_start = "09:00"
shift_end = "17:00"

print(f"Alice available on {shift_date}? {employees[0].is_available(shift_date, shift_start, shift_end)}")
print(f"Bob available on {shift_date}? {employees[1].is_available(shift_date, shift_start, shift_end)}")

# visualize_schedule()

