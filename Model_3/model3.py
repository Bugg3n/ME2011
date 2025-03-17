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
def get_fit_score(emp, shift_date, shift_start, shift_end):
    """
    Calculates a fit score for assigning an employee to a shift.
    
    - Rewards early-preference employees for early shifts.
    - Rewards late-preference employees for late shifts.
    - Considers employment rate and assigned workload.
    
    Args:
        emp (Employee): The employee object.
        shift_date (str): The shift's date (YYYY-MM-DD).
        shift_start (str): Shift start time (HH:MM).
        shift_end (str): Shift end time (HH:MM).
    
    Returns:
        float: The fit score (higher is better). Returns 0 if the employee is unavailable.
    """
    if not emp.is_available(shift_date, shift_start, shift_end):
        return 0

    shift_start_hour = int(shift_start.split(":")[0])

    early_threshold = 12  # Consider before 12:00 as an early shift
    late_threshold = 17   # Consider after 17:00 as a late shift

    early_bonus = max(0, (10 - emp.early_preference) if shift_start_hour >= early_threshold else emp.early_preference)
    late_bonus = max(0, (10 - emp.late_preference) if shift_start_hour < late_threshold else emp.late_preference)

    # Calculate workload factor (favor employees with fewer assigned hours)
    workload_factor = (1 - emp.assigned_hours / emp.max_hours_per_week) * 10

    # Final fit score
    return early_bonus + late_bonus + workload_factor


if __name__ == "__main__":
    main()
        
