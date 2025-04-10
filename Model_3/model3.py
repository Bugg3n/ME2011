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

    if last_month_schedule:
        carryover_hours = track_carryover_weekly_hours(employees, last_month_schedule, year, month)
        for emp in employees:
            if week_num == 0 and emp.name in carryover_hours:
                weekly_hours[emp.name][week_num] += carryover_hours[emp.name]

def assign_shift_to_best_employee(shift, date_str, employees, assigned_shifts, monthly_hours, weekly_hours, week_num, max_hours, unassigned_shifts, debug):
    shift_start, shift_end, shift_lunch = shift["start"], shift["end"],shift["lunch"]
    best_employee, best_fit_score = None, float('-inf')
    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    for emp in employees:
        if not emp.manager:
            fit_score = get_fit_score(emp, date, shift_start, shift_end, max_hours, debug)
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


def cover_remaining_shifts(assigned_shifts, unassigned_shifts, employees, year, month, store_open, store_close, max_daily_hours, monthly_hours):
    store_open_time = datetime.strptime(store_open, "%H:%M")
    store_close_time = datetime.strptime(store_close, "%H:%M")
    still_unassigned = []

    for shift in unassigned_shifts:
        
        assigned = (
            try_extend_under_scheduled(assigned_shifts, employees, shift, store_open_time, store_close_time, monthly_hours) or
            try_assign_manager(assigned_shifts, employees, shift, monthly_hours) or
            try_assign_overtime(assigned_shifts, employees, shift, monthly_hours) or
            try_swap_shift_to_manager(assigned_shifts, employees, shift, monthly_hours)
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
    shift_start = datetime.strptime(shift["start"], "%H:%M")
    shift_end = datetime.strptime(shift["end"], "%H:%M")
    shift_hours = (shift_end - shift_start).seconds // 3600
    date = datetime.strptime(shift["date"], "%Y-%m-%d").date()


    # Reject if not between 8–17
    if shift_start.hour < 8 or shift_end.hour > 17:
        return False

    # Reject if weekend (Saturday = 5, Sunday = 6)
    shift_day = date.weekday()
    if shift_day >= 5:
        return False

    for emp in employees:
        if emp.manager and emp.get_total_weekly_hours(date) >= shift_hours:
            emp.assign_shift(shift)
            assigned_shifts[emp.name].append(shift)
            emp.monthly_assigned_hours += shift_hours
            return True
    return False

def try_swap_shift_to_manager(assigned_shifts, employees, unassigned_shift, monthly_hours, debug = False):
    """
    Attempts to let a manager take over a regular employee's weekday day shift,
    so that the employee can work the unassigned evening/weekend shift.
    """
    shift_date = datetime.strptime(unassigned_shift["date"], "%Y-%m-%d")
    shift_start = datetime.strptime(unassigned_shift["start"], "%H:%M")
    shift_end = datetime.strptime(unassigned_shift["end"], "%H:%M")
    shift_hours = (shift_end - shift_start).seconds // 3600
    shift_day = shift_date.weekday()  # 0=Mon, 6=Sun
    if debug: print(f"Trying to fix the unassigned shift: {shift_date}, from {shift_start} until {shift_end}")


    # Proceed only if the unassigned shift is an evening or weekend
    if shift_day < 5 and (shift_start.hour >= 8 and shift_end.hour <= 17):
        if debug: print("Not an evening shift.")
        return False


    for emp in employees:
        if emp.manager:
            continue
        if debug:
            print(f"Testing to swap shift with: {emp.name}")
            no_suiting_swap = True
            mananger_not_available = False
            employee_still_not_available = False
        # Look for a swappable shift (weekday, daytime)
        for shift in assigned_shifts.get(emp.name, []):
            s_date = datetime.strptime(shift["date"], "%Y-%m-%d")
            s_day = s_date.weekday()
            s_start = datetime.strptime(shift["start"], "%H:%M")
            s_end = datetime.strptime(shift["end"], "%H:%M")
            s_hours = (s_end - s_start).seconds // 3600
            lunch = 1 if shift.get("lunch", "None") != "None" else 0
            s_hours -= lunch
            if not (0 <= s_day <= 4 and 8 <= s_start.hour and s_end.hour <= 17):
                continue  # Skip non-daytime or weekend shifts
            # Find manager who can take this day shift
            for mgr in employees:
                if not mgr.manager:
                    continue
                if mgr.is_available(shift["date"], shift["start"], shift["end"], monthly_hours, debug = debug):
                    no_suiting_swap = False
                    # Swap the shift
                    emp.remove_shift(shift)
                    mgr.assign_shift(shift)
                    assigned_shifts[emp.name].remove(shift)
                    assigned_shifts[mgr.name].append(shift)

                    # Now recheck if employee can take the unassigned shift
                    if emp.is_available(unassigned_shift["date"], unassigned_shift["start"], unassigned_shift["end"], monthly_hours, debug=debug):
                        if debug: print("employee available. Succesfull change")
                        emp.assign_shift(unassigned_shift)
                        assigned_shifts[emp.name].append(unassigned_shift)
                        return True

                    # If it fails, undo
                    employee_still_not_available = True
                    emp.assign_shift(shift)
                    mgr.remove_shift(shift)
                    assigned_shifts[emp.name].append(shift)
                    assigned_shifts[mgr.name].remove(shift)
                else: mananger_not_available = True
    if debug:
        print(f"swap failed due to: ")
        print(f"manager not available: {mananger_not_available}")
        print(f"no suiting swap: {no_suiting_swap}")
        print(f"employee still not available: {employee_still_not_available}")


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

    time_bonus = calculate_time_of_day_bonus(emp, shift_start, shift_end)
    workload_bonus = calculate_workload_bonus(emp, shift_date)
    weekend_bonus = calculate_weekend_bonus(emp, shift_date)
    spread_bonus = calculate_spread_bonus(emp, shift_date, emp.spread)

    return time_bonus + workload_bonus + weekend_bonus + spread_bonus


def calculate_time_of_day_bonus(emp, shift_start, shift_end):
    start_hour = int(shift_start.split(":")[0])
    end_hour = int(shift_end.split(":")[0])
    if end_hour < 17:
        return 10 - emp.early_late_preference
    elif end_hour >= 18:
        return emp.early_late_preference
    return 5  # Neutral for midday

def calculate_workload_bonus(emp, shift_date):
    current_week_hours = emp.get_total_weekly_hours(shift_date)
    return (1 - current_week_hours / emp.max_hours_per_week) * 20

def calculate_weekend_bonus(emp, shift_date):
    weekday = shift_date.weekday()
    return emp.weekend_preference if weekday >= 5 else 0


def calculate_spread_bonus(emp, proposed_date, spread_preference):
    """
    Calculates how well this shift fits with the employee's spread preference,
    normalized by their employment rate.
    """
    scheduled_dates = [datetime.strptime(shift["date"], "%Y-%m-%d").date() for shift in emp.schedule]
    
    if not scheduled_dates:
        return 5  # Neutral if nothing scheduled yet

    # Minimum number of days between existing shifts and the proposed one
    min_day_diff = min(abs((proposed_date - s_date).days) for s_date in scheduled_dates)

    # Normalize expected spacing based on employment rate
    expected_spacing = 1 / emp.employment_rate if emp.employment_rate > 0 else 7  # Avoid div-by-zero
    spread_factor = min_day_diff / expected_spacing

    if spread_preference >= 6:
        # Prefers more spread → high bonus for high spread_factor
        bonus = spread_factor * (spread_preference / 10)
    else:
        # Prefers clustered shifts → bonus for low spread_factor
        bonus = (1 / (1 + spread_factor)) * (11 - spread_preference)

    return bonus


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
        hours_needed = emp.employment_rate * monthly_hours - emp.monthly_assigned_hours
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
    

def create_schedule(monthly_schedule, employees, YEAR, MONTH, last_month_schedule, max_hours, debug = False, store_open = "8:00", store_close = "22:00", max_daily_hours = 10):
    
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
    assigned_shifts_by_date = transform_schedule_format(assigned_shifts, YEAR, MONTH)

    return assigned_shifts, unassigned_shifts, assigned_shifts_by_date