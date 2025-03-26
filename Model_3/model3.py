from .employees import *
from datetime import datetime, timedelta
import calendar

def assign_shifts_to_employees_monthly(monthly_shifts, employees, year, month, last_month_schedule = None, max_hours = 170, debug = False):
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
    unassigned_shifts = []

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
                if not emp.manager:
                    fit_score = get_fit_score(emp, date_str, shift_start, shift_end, max_hours, debug)
                    if fit_score:
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
                best_employee.assign_shift(shift_with_date)
                assigned_shifts[best_employee.name].append(shift_with_date)

                shift_hours = (datetime.strptime(shift_end, "%H:%M") - datetime.strptime(shift_start, "%H:%M")).seconds // 3600
                if shift["lunch"] != "None":
                    shift_hours -= 1  # Deduct lunch hour
                weekly_hours[best_employee.name][week_num] += shift_hours
                monthly_hours[best_employee.name] += shift_hours
            else: 
                print(f"No employee available on {date_str} for shift {shift_start} - {shift_end}")
                unassigned_shifts.append({
                "date": date_str,
                "start": shift_start,
                "end": shift_end
                })

    return assigned_shifts, unassigned_shifts

def cover_remaining_shifts(assigned_shifts, unassigned_shifts, employees, year, month, store_open, store_close, max_daily_hours, monthly_hours):
    """
    Attempts to cover unassigned shifts using available employees, managers, or overtime.
    """

    store_open_time = datetime.strptime(store_open, "%H:%M")
    store_close_time = datetime.strptime(store_close, "%H:%M")

    still_unassigned = []

    for shift in unassigned_shifts:
        shift_date = shift["date"]
        start_time = datetime.strptime(shift["start"], "%H:%M")
        end_time = datetime.strptime(shift["end"], "%H:%M")
        shift_hours = (end_time - start_time).seconds // 3600

        assigned = False

        # 1️⃣ Try to extend existing shifts of under-scheduled employees
        under_scheduled = [e for e in employees if e.monthly_assigned_hours < monthly_hours * e.employment_rate]
        for emp in under_scheduled:
            for existing_shift in assigned_shifts.get(emp.name, []):
                if existing_shift["date"] == shift_date:
                    existing_start = datetime.strptime(existing_shift["start"], "%H:%M")
                    existing_end = datetime.strptime(existing_shift["end"], "%H:%M")

                    # Try extending end
                    if existing_end == start_time and (existing_end + timedelta(hours=shift_hours)) <= store_close_time:
                        existing_shift["end"] = end_time.strftime("%H:%M")
                        emp.monthly_assigned_hours += shift_hours
                        assigned = True
                        print("Made a shift end later")
                        break
                    # Try extending start
                    elif existing_start == end_time and (existing_start - timedelta(hours=shift_hours)) >= store_open_time:
                        existing_shift["start"] = start_time.strftime("%H:%M")
                        emp.monthly_assigned_hours += shift_hours
                        assigned = True
                        print("Made a shift start earlier")
                        break
            if assigned:
                break

        if assigned:
            continue

        # 2️⃣ Try assigning a manager with remaining sales hours
        for emp in employees:
            if emp.manager and hasattr(emp, "weekly_sales_hours") and emp.weekly_sales_hours >= shift_hours:
                shift = {
                    "date": shift_date,
                    "start": shift["start"],
                    "end":  shift["end"],
                    "lunch": shift.get("lunch", "None")  # Include lunch if available
                }
                emp.assign_shift(shift)
                assigned_shifts[emp.name].append(shift)
                emp.weekly_sales_hours -= shift_hours
                emp.monthly_assigned_hours += shift_hours
                assigned = True
                break

        if assigned:
            continue

        # 3️⃣ Try assigning someone available for overtime
        for emp in employees:
            if emp.is_available_for_overtime(shift_date, shift["start"], shift["end"], monthly_hours):
                shift = {
                    "date": shift_date,
                    "start": shift["start"],
                    "end":  shift["end"],
                    "lunch": shift.get("lunch", "None")  # Include lunch if available
                }
                emp.assign_shift(shift)
                assigned_shifts[emp.name].append(shift)
                emp.monthly_assigned_hours += shift_hours
                assigned = True
                break

        if not assigned:
            print(f"⚠️ Could not cover shift on {shift_date} from {shift['start']} to {shift['end']}")
            still_unassigned.append(shift)

    return assigned_shifts, still_unassigned

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


def get_fit_score(emp, shift_date, shift_start, shift_end, month_max_hours, debug):
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

    if not emp.is_available(shift_date, shift_start, shift_end, month_max_hours, debug=debug):
        return None

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


def extend_shifts_to_fulfill_contracts(employees, assigned_shifts_by_employee, store_open="08:00", store_close="22:00", max_daily_hours=9, monthly_hours=170):
    """
    Extend existing shifts for employees who have not yet fulfilled their monthly contract.
    
    Args:
        employees (list): List of Employee objects (with monthly_assigned_hours updated).
        assigned_shifts_by_employee (dict): Mapping of employee names to list of assigned shifts.
        store_open (str): Earliest time a shift can start (e.g., "08:00").
        store_close (str): Latest time a shift can end (e.g., "22:00").
        max_daily_hours (int): Maximum length a shift can be extended to.
    
    Returns:
        dict: Updated assigned_shifts_by_employee with extended shifts.
    """
    store_open_time = datetime.strptime(store_open, "%H:%M")
    store_close_time = datetime.strptime(store_close, "%H:%M")
    
    emp_lookup = {e.name: e for e in employees}

    for emp_name, shifts in assigned_shifts_by_employee.items():
        emp = emp_lookup[emp_name]
        if not emp.manager:
            hours_needed = emp.employment_rate * monthly_hours - emp.monthly_assigned_hours

            for shift in shifts:
                if hours_needed <= 0:
                    break  # Contract fulfilled
                
                start_time = datetime.strptime(shift["start"], "%H:%M")
                end_time = datetime.strptime(shift["end"], "%H:%M")
                lunch_break = 1 if shift["lunch"] != "None" else 0

                # Current shift length (excluding lunch)
                current_length = (end_time - start_time).seconds / 3600 - lunch_break
                if emp.name == "Quinn": print(f"current length {current_length}")
                remaining_expandable = max_daily_hours - current_length
                if emp.name == "Quinn": print(remaining_expandable)

                if remaining_expandable <= 0:
                    continue  # Already at max length

                # Determine how many hours we can add (without exceeding store hours)
                max_start_extension = int((start_time - store_open_time).seconds / 3600)
                max_end_extension = int((store_close_time - end_time).seconds / 3600)

                # Try to balance early and late extension
                total_possible_extension = min(
                    remaining_expandable,
                    max_start_extension + max_end_extension,
                    hours_needed
                )

                # Prefer balanced extensions
                extend_early = min(max_start_extension, total_possible_extension // 2)
                extend_late = min(max_end_extension, total_possible_extension - extend_early)

                # Apply extensions
                new_start = start_time - timedelta(hours=extend_early)
                new_end = end_time + timedelta(hours=extend_late)

                # Update shift
                shift["start"] = new_start.strftime("%H:%M")
                shift["end"] = new_end.strftime("%H:%M")
                if emp.name == "Quinn":print(shift["start"])
                if emp.name == "Quinn":shift["end"]

                # Update tracking
                emp.monthly_assigned_hours += (extend_early + extend_late)
                hours_needed -= (extend_early + extend_late)

    return assigned_shifts_by_employee

