from .employees import *
from datetime import datetime, timedelta
import calendar

def assign_shifts_to_employees_monthly(monthly_shifts, employees, year, month, last_month_schedule = None, max_hours = 170):
    """
    Assigns shifts to employees for a full month while ensuring:
    - Employees reach their required monthly hours.
    - Weekly hours do not differ by more than 5 hours.
    
    Args:
        monthly_shifts (dict): Mapping of days to shift lists from Model 2.
        employees (list of Employee): List of Employee objects.
        year (int): The year of the schedule.
        month (int): The month of the schedule.
    
    Returns:
        dict: Mapping of employees to their assigned shifts.
    """

    assigned_shifts = {emp.name: [] for emp in employees}

    # Track weekly assigned hours per employee
    weekly_hours = {emp.name: [0] * 5 for emp in employees}  # 5 weeks max in a month
    monthly_hours = {emp.name: 0 for emp in employees}

    # Get number of days in the month
    num_days = calendar.monthrange(year, month)[1]

    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        week_num = (datetime(year, month, day).isocalendar()[1]) % 5  # Normalize to 0-4

        if datetime(year, month, day).day == 1:
            print("New month, reseting time counters")
            reset_all_monthly_hours(employees)

        if datetime(year, month, day).weekday() == 0:  # Reset on Mondays
            reset_all_weekly_hours(employees)
        
        if date_str not in monthly_shifts:
            continue  # Skip if no shifts for this day

        shifts = monthly_shifts[date_str]["shifts"]
        if last_month_schedule:
            carryover_hours = track_carryover_weekly_hours(employees, last_month_schedule, year, month)
            for emp in employees:
                if week_num == 0 and emp.name in carryover_hours:
                    weekly_hours[emp.name][week_num] += carryover_hours[emp.name]  # Add carryover hours
                    carryover_hours[emp.name] = 0  # Reset after adjustment
        
        # Sort employees dynamically based on:
        # 1. Employees with the least assigned hours.
        # 2. Employees closest to their weekly target.
        employees.sort(key=lambda e: (
            monthly_hours[e.name], 
            abs(weekly_hours[e.name][week_num] - (e.max_hours_per_week / 4))
        ))

        for shift in shifts:
            shift_start, shift_end = shift["start"], shift["end"]
            
            best_employee = None
            best_fit_score = float('-inf')
            i = 0
            for emp in employees:
                fit_score = get_fit_score(emp, date_str, shift_start, shift_end, max_hours)

                if fit_score > best_fit_score:
                    best_fit_score = fit_score
                    best_employee = emp

            if best_employee:
                # Add the date to the shift dictionary
                shift_with_date = {
                    "date": date_str,
                    "start": shift_start,
                    "end": shift_end,
                    "lunch": shift.get("lunch", "None")  # Include lunch if available
                }
                best_employee.assign_shift(date_str, shift_start, shift_end)
                assigned_shifts[best_employee.name].append(shift_with_date)

                shift_hours = (datetime.strptime(shift_end, "%H:%M") - datetime.strptime(shift_start, "%H:%M")).seconds // 3600
                if shift["lunch"] != "None":
                    shift_hours -= 1  # Deduct lunch hour
                weekly_hours[best_employee.name][week_num] += shift_hours
                monthly_hours[best_employee.name] += shift_hours
            else: 
                print("No employee available")

    return assigned_shifts

def track_carryover_weekly_hours(employees, last_month_schedule, year, month):
    """
    Adjusts employees' weekly hours for the first week of the new month by considering 
    any hours worked in the last week of the previous month.
    
    Args:
        employees (list of Employee): List of employees.
        last_month_schedule (dict): Schedule from the last month.
        year (int): The current scheduling year.
        month (int): The current scheduling month.
    
    Returns:
        dict: Carryover hours for employees.
    """

    first_day_current_month = datetime(year, month, 1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    last_week_previous_month = last_day_previous_month.isocalendar()[1]

    carryover_hours = {emp.name: 0 for emp in employees}

    for employee_name, shifts in last_month_schedule.items():
        for shift in shifts:
            shift_date = datetime.strptime(shift["date"], "%Y-%m-%d")
            week_number = shift_date.isocalendar()[1]

            if week_number == last_week_previous_month:  # If the shift was in the last week
                start_time = datetime.strptime(shift["start"], "%H:%M")
                end_time = datetime.strptime(shift["end"], "%H:%M")
                shift_hours = (end_time - start_time).seconds / 3600

                # Subtract lunch break if applicable
                if shift["lunch"] != "None":
                    shift_hours -= 1  

                carryover_hours[employee_name] += shift_hours

    return carryover_hours


def get_fit_score(emp, shift_date, shift_start, shift_end, month_max_hours):
    """
    Calculates a fit score for assigning an employee to a shift.
    
    - Rewards employees who prefer early shifts when assigning morning shifts.
    - Rewards employees who prefer late shifts when assigning evening shifts.
    - Considers employment rate and assigned workload.
    
    Args:
        emp (Employee): The employee object.
        shift_date (str): The shift's date (YYYY-MM-DD).
        shift_start (str): Shift start time (HH:MM).
        shift_end (str): Shift end time (HH:MM).
    
    Returns:
        float: The fit score (higher is better). Returns a large negative value if the employee is unavailable.
    """
    if not emp.is_available(shift_date, shift_start, shift_end, month_max_hours):
        return -10000  # Large negative value to strongly discourage selection

    shift_start_hour = int(shift_start.split(":")[0])

    early_threshold = 12  # Before 12:00 is considered an early shift
    late_threshold = 17   # After 17:00 is considered a late shift

    # Convert the single preference value (1 = prefers early, 10 = prefers late)
    if shift_start_hour < early_threshold:
        preference_bonus = 10 - emp.early_late_preference  # Prefers early shifts
    elif shift_start_hour >= late_threshold:
        preference_bonus = emp.early_late_preference  # Prefers late shifts
    else:
        preference_bonus = 5  # Neutral preference for midday shifts

    # Calculate workload factor (favor employees with fewer assigned hours)
    workload_factor = (1 - emp.assigned_hours / emp.max_hours_per_week) * 10

    # Final fit score
    return preference_bonus + workload_factor

def reset_all_weekly_hours(employees):
    """Resets weekly hour counters for all employees at the start of a new week."""
    for emp in employees:
        emp.reset_weekly_schedule()

def reset_all_monthly_hours(employees):
    """Resets monthly hour counters for all employees at the start of a new month."""
    for emp in employees:
        emp.reset_monthly_schedule()

def transform_schedule_format(employee_schedule, year, month):
    """
    Converts employee-based schedule into a date-based schedule.

    Args:
        employee_schedule (dict): The original schedule where shifts are grouped by employee.
        year (int): The year of the schedule.
        month (int): The month of the schedule.

    Returns:
        dict: The transformed schedule where shifts are grouped by date.
    """
    transformed_schedule = {}

    # Get number of days in the month
    num_days = calendar.monthrange(year, month)[1]

    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        transformed_schedule[date_str] = {}

    for employee, shifts in employee_schedule.items():
        for shift in shifts:
            shift_date = shift["date"]  # Use the date field from the shift
            if employee not in transformed_schedule[shift_date]:
                transformed_schedule[shift_date][employee] = []
            
            transformed_schedule[shift_date][employee].append(shift)

    return transformed_schedule
