from .employees import *
from datetime import date

# This part of the code is supposed to take the shift suggestions from part 2 and then create the actual schedule. 
# It also visualizes the schedule

def main():
    employees = load_employees()


    for emp in employees:
        print(emp)

    shift_date = "2025-03-15" # Alice should be unavailable
    shift_start = "09:00"
    shift_end = "17:00"

    print(f"Alice available on {shift_date}? {employees[0].is_available(shift_date, shift_start, shift_end)}")
    print(f"Bob available on {shift_date}? {employees[1].is_available(shift_date, shift_start, shift_end)}")

def assign_shifts_to_employees(shifts, employees, shift_date):
    """
    Assign shifts to employees optimally based on their availability, preferences, and employment rate.
    
    Parameters:
    shifts (list of dict): List of shifts, each with 'start' and 'end' times.
    employees (list of Employee): List of Employee objects.
    shift_date (str): The date of the shifts (YYYY-MM-DD).
    
    Returns:
    dict: Mapping of employees to their assigned shifts.
    """
    assigned_shifts = {emp.name: [] for emp in employees}

    # Sort employees by employment rate (full-time first) and preference
    employees.sort(key=lambda e: (-e.employment_rate, -e.early_preference, e.late_preference))

    for shift in shifts:
        shift_start, shift_end = shift["start"], shift["end"]
        
        best_employee = None
        best_fit_score = float('-inf')

        for emp in employees:
            fit_score = get_fit_score(emp, shift_date, shift_start, shift_end)
            if fit_score > best_fit_score:
                best_fit_score = fit_score
                best_employee = emp

        if best_employee:
            best_employee.assign_shift(shift_date, shift_start, shift_end)
            assigned_shifts[best_employee.name].append(shift)

    return assigned_shifts

def get_fit_score(emp, shift_date, shift_start, shift_end): # Detta ska anpassas efter oss
    if emp.is_available(shift_date, shift_start, shift_end):
    # Score based on early/late preferences, employment rate, and workload
        return (
            (10 - abs(emp.early_preference - 5)) +  # Balance early preference
            (10 - abs(emp.late_preference - 5)) +   # Balance late preference
            (1 - emp.assigned_hours / emp.max_hours_per_week) * 10  # Less assigned is better
        )
    else:
        return 0

if __name__ == "__main__":
    main()
        
