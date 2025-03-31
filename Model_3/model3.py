from .employees import *
from datetime import datetime, timedelta
import calendar

from .employees import *
from datetime import datetime, timedelta
import calendar

def assign_shifts_to_employees_monthly(monthly_shifts, employees, year, month, last_month_schedule=None, max_hours=170, debug=False):
    assigned_shifts = {emp.name: [] for emp in employees}
    unassigned_shifts = []

    weekly_hours = {emp.name: [0] * 5 for emp in employees}
    monthly_hours = {emp.name: 0 for emp in employees}
    num_days = calendar.monthrange(year, month)[1]

    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        week_num = (datetime(year, month, day).isocalendar()[1]) % 5

        handle_new_periods(employees, day, date_str, week_num, last_month_schedule, weekly_hours, year, month)

        if date_str not in monthly_shifts:
            continue

        shifts = monthly_shifts[date_str]["shifts"]
        employees.sort(key=lambda e: (monthly_hours[e.name], abs(weekly_hours[e.name][week_num] - (e.max_hours_per_week / 4))))

        for shift in shifts:
            
            assign_shift_to_best_employee(shift, date_str, employees, assigned_shifts, monthly_hours, weekly_hours, week_num, max_hours, unassigned_shifts, debug)
        
    return assigned_shifts, unassigned_shifts

def handle_new_periods(employees, day, date_str, week_num, last_month_schedule, weekly_hours, year, month):
    if day == 1:
        reset_all_monthly_hours(employees)

    if datetime.strptime(date_str, "%Y-%m-%d").weekday() == 0:
        reset_all_weekly_hours(employees)

    if last_month_schedule:
        carryover_hours = track_carryover_weekly_hours(employees, last_month_schedule, year, month)
        for emp in employees:
            if week_num == 0 and emp.name in carryover_hours:
                weekly_hours[emp.name][week_num] += carryover_hours[emp.name]

def assign_shift_to_best_employee(shift, date_str, employees, assigned_shifts, monthly_hours, weekly_hours, week_num, max_hours, unassigned_shifts, debug):
    shift_start, shift_end, shift_lunch = shift["start"], shift["end"],shift["lunch"]
    best_employee, best_fit_score = None, float('-inf')

    for emp in employees:
        if not emp.manager:
            fit_score = get_fit_score(emp, date_str, shift_start, shift_end, max_hours, debug)
            if fit_score and fit_score > best_fit_score:
                best_fit_score = fit_score
                best_employee = emp

    if best_employee:
        assign_shift(best_employee, shift, date_str, assigned_shifts, monthly_hours, weekly_hours, week_num)
    else:
        if debug: print(f"No employee available on {date_str} for shift {shift_start} - {shift_end}")
        unassigned_shifts.append({"date": date_str, "start": shift_start, "end": shift_end, "lunch": shift_lunch})
    
    
   
        

def assign_shift(emp, shift, date_str, assigned_shifts, monthly_hours, weekly_hours, week_num):
    shift_with_date = {
        "date": date_str,
        "start": shift["start"],
        "end": shift["end"],
        "lunch": shift.get("lunch", "None")
    }
    emp.assign_shift(shift_with_date)
    assigned_shifts[emp.name].append(shift_with_date)

    shift_hours = (datetime.strptime(shift["end"], "%H:%M") - datetime.strptime(shift["start"], "%H:%M")).seconds // 3600
    if shift["lunch"] != "None":
        shift_hours -= 1

    weekly_hours[emp.name][week_num] += shift_hours
    monthly_hours[emp.name] += shift_hours

# Next step would be to extract parts from cover_remaining_shifts, extend_shifts_to_fulfill_contracts, and create_schedule in the same manner.

def cover_remaining_shifts(assigned_shifts, unassigned_shifts, employees, year, month, store_open, store_close, max_daily_hours, monthly_hours):
    store_open_time = datetime.strptime(store_open, "%H:%M")
    store_close_time = datetime.strptime(store_close, "%H:%M")
    still_unassigned = []

    for shift in unassigned_shifts:
        
        assigned = (
            try_extend_under_scheduled(assigned_shifts, employees, shift, store_open_time, store_close_time, monthly_hours) or
            try_assign_manager(assigned_shifts, employees, shift, monthly_hours) or
            try_assign_overtime(assigned_shifts, employees, shift, monthly_hours)
        )
        if not assigned:
            
            still_unassigned.append(shift)

    return assigned_shifts, still_unassigned

def try_extend_under_scheduled(assigned_shifts, employees, shift, store_open_time, store_close_time, monthly_hours):
    start_time = datetime.strptime(shift["start"], "%H:%M")
    end_time = datetime.strptime(shift["end"], "%H:%M")
    shift_hours = (end_time - start_time).seconds // 3600

    for emp in employees:
        if emp.monthly_assigned_hours < monthly_hours * emp.employment_rate:
            for s in assigned_shifts.get(emp.name, []):
                s_start = datetime.strptime(s["start"], "%H:%M")
                s_end = datetime.strptime(s["end"], "%H:%M")
                if s["date"] == shift["date"]:
                    if s_end == start_time and s_end + timedelta(hours=shift_hours) <= store_close_time:
                        s["end"] = shift["end"]
                        emp.monthly_assigned_hours += shift_hours
                        return True
                    elif s_start == end_time and s_start - timedelta(hours=shift_hours) >= store_open_time:
                        s["start"] = shift["start"]
                        emp.monthly_assigned_hours += shift_hours
                        return True
    return False


def try_assign_manager(assigned_shifts, employees, shift, monthly_hours):
    shift_hours = (datetime.strptime(shift["end"], "%H:%M") - datetime.strptime(shift["start"], "%H:%M")).seconds // 3600
    for emp in employees:
        if emp.manager and hasattr(emp, "weekly_sales_hours") and emp.weekly_sales_hours >= shift_hours:
            emp.assign_shift(shift)
            assigned_shifts[emp.name].append(shift)
            emp.weekly_sales_hours -= shift_hours
            emp.monthly_assigned_hours += shift_hours
            return True
    
    return False

def try_assign_overtime(assigned_shifts, employees, shift, monthly_hours):
    
    for emp in employees:

        if emp.is_available_for_overtime_function(shift["date"], shift["start"], shift["end"], monthly_hours):
      
            emp.assign_shift(shift)
            assigned_shifts[emp.name].append(shift)
            shift_hours = (datetime.strptime(shift["end"], "%H:%M") - datetime.strptime(shift["start"], "%H:%M")).seconds // 3600
            emp.monthly_assigned_hours += shift_hours
            return True
 
    return False


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
    
    Returns:
        float: The fit score (higher is better). Returns a large negative value if the employee is unavailable.
    """

    if not emp.is_available(shift_date, shift_start, shift_end, month_max_hours, debug=debug):
        return None

    shift_start_hour = int(shift_start.split(":")[0])
    shift_end_hour = int(shift_end.split(":")[0])

    early_threshold = 17  # Before 12:00 is considered an early shift
    late_threshold = 18   # After 17:00 is considered a late shift

    # Convert the single preference value (1 = prefers early, 10 = prefers late)
    if shift_end_hour < early_threshold:
        preference_bonus = 10 - emp.early_late_preference  # Prefers early shifts
    elif shift_end_hour >= late_threshold:
        preference_bonus = emp.early_late_preference  # Prefers late shifts
    else:
        preference_bonus = 5  # Neutral preference for midday shifts

    # Calculate workload factor (favor employees with fewer assigned hours)
    workload_factor = (1 - emp.assigned_hours / emp.max_hours_per_week) * 10

    # Weekend preference bonus
    shift_day = datetime.strptime(shift_date, "%Y-%m-%d").weekday()  # 0=Mon, ..., 5=Sat, 6=Sun
    if shift_day in (5, 6):  # If Saturday or Sunday
        weekend_bonus = emp.weekend_preference
    else:
        weekend_bonus = 0

    # Final fit score
    return preference_bonus + workload_factor + weekend_bonus

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
    store_open_time = datetime.strptime(store_open, "%H:%M")
    store_close_time = datetime.strptime(store_close, "%H:%M")
    emp_lookup = {e.name: e for e in employees}
    still_needs_extension = []

    for emp_name, shifts in assigned_shifts_by_employee.items():
        emp = emp_lookup[emp_name]
        if emp.manager:
            continue

        hours_needed = emp.employment_rate * monthly_hours - emp.monthly_assigned_hours
        shifts.sort(key=shift_duration)

        for shift in shifts:
            if hours_needed <= 0:
                break
            extend_early, extend_late = extend_shift_logic(shift, store_open_time, store_close_time, hours_needed, max_daily_hours)
            hours_added = extend_early + extend_late
            if hours_added == 0:
                continue
            shift = apply_extension(shift, extend_early, extend_late)
            emp.monthly_assigned_hours += hours_added
            hours_needed -= hours_added

        if hours_needed > 0:
            still_needs_extension.append((emp, shifts))

    for emp, shifts in still_needs_extension:
        print(f"Still need extension accessed: {emp}")
        hours_needed = emp.employment_rate * monthly_hours - emp.monthly_assigned_hours
        print(f"hours needed: {hours_needed}")
        for shift in shifts:
            if hours_needed <= 0:
                break
            result = extend_shift_with_lunch(shift, store_open_time, store_close_time, hours_needed, max_daily_hours)
            if result is not None:
                extend_early, extend_late, lunch_time = result
                shift = apply_extension(shift, extend_early, extend_late, lunch_time)
                hours_added = extend_early + extend_late
                emp.monthly_assigned_hours += hours_added
                hours_needed -= hours_added

    return assigned_shifts_by_employee

def extend_shift_with_lunch(shift, store_open_time, store_close_time, hours_needed, max_daily_hours):
    start_time = datetime.strptime(shift["start"], "%H:%M")
    end_time = datetime.strptime(shift["end"], "%H:%M")
    current_length = (end_time - start_time).seconds / 3600

    if current_length > 5:
        return None  # Skip long shifts already

    max_start_extension = int((start_time - store_open_time).seconds / 3600)
    max_end_extension = int((store_close_time - end_time).seconds / 3600)
    remaining_expandable = max_daily_hours - current_length

    required_extension = max(4, min(remaining_expandable, hours_needed))
    total_with_lunch = required_extension + 1

    if max_end_extension >= total_with_lunch:
        lunch_time = end_time.strftime("%H:%M")
        return 0, required_extension, lunch_time
    elif max_start_extension >= total_with_lunch:
        lunch_time = (start_time - timedelta(hours=1)).strftime("%H:%M")
        return required_extension, 0, lunch_time
    return None

def apply_extension(shift, extend_early, extend_late, lunch_time=None):
    start_time = datetime.strptime(shift["start"], "%H:%M")
    end_time = datetime.strptime(shift["end"], "%H:%M")
    new_start = start_time - timedelta(hours=extend_early)
    new_end = end_time + timedelta(hours=extend_late)

    shift["start"] = new_start.strftime("%H:%M")
    shift["end"] = new_end.strftime("%H:%M")

    if lunch_time:
        shift["lunch"] = lunch_time

    return shift

def extend_shift_logic(shift, store_open_time, store_close_time, hours_needed, max_daily_hours):
    start_time = datetime.strptime(shift["start"], "%H:%M")
    end_time = datetime.strptime(shift["end"], "%H:%M")
    lunch_break = 1 if shift["lunch"] != "None" else 0
    current_length = (end_time - start_time).seconds / 3600 - lunch_break

    max_start_extension = int((start_time - store_open_time).seconds / 3600)
    max_end_extension = int((store_close_time - end_time).seconds / 3600)
    remaining_expandable = max_daily_hours - current_length

    if current_length < 5:
        max_total_extension = min(remaining_expandable, max_start_extension + max_end_extension, 5 - current_length)
    else:
        max_total_extension = min(remaining_expandable, max_start_extension + max_end_extension, hours_needed)

    extend_early = 0
    extend_late = 0

    # Prefer extending in both directions if possible
    if max_start_extension >= max_end_extension:
        extend_early = min(max_start_extension, max_total_extension)
        remaining = max_total_extension - extend_early
        extend_late = min(max_end_extension, remaining)
    else:
        extend_late = min(max_end_extension, max_total_extension)
        remaining = max_total_extension - extend_late
        extend_early = min(max_start_extension, remaining)

    return extend_early, extend_late



def shift_duration(shift):
    start = datetime.strptime(shift["start"], "%H:%M")
    end = datetime.strptime(shift["end"], "%H:%M")
    lunch = 1 if shift["lunch"] != "None" else 0
    return (end - start).seconds / 3600 - lunch
    

def create_schedule(monthly_schedule, employees, YEAR, MONTH, last_month_schedule, max_hours, debug, store_open, store_close, max_daily_hours):
    
    assigned_shifts, unassigned_shifts = assign_shifts_to_employees_monthly(
        monthly_schedule, 
        employees, 
        YEAR, 
        MONTH, 
        last_month_schedule, 
        max_hours, 
        debug
    )
  
    assigned_shifts, unassigned_shifts = cover_remaining_shifts(
        assigned_shifts,
        unassigned_shifts,
        employees,
        year=YEAR,
        month=MONTH,
        store_open=store_open,
        store_close=store_close,
        max_daily_hours=max_daily_hours,
        monthly_hours=max_hours
    )
  
    assigned_shifts = extend_shifts_to_fulfill_contracts(
        employees, 
        assigned_shifts, 
        store_open=store_open,
        store_close=store_close,
        max_daily_hours=max_daily_hours,
        monthly_hours=max_hours
    )
    

    return assigned_shifts, unassigned_shifts