import json
from datetime import datetime
import pandas as pd

def analyze_monthly_hours_from_employees(employees: list, schedule_json_path: str, monthly_expected_fulltime: int = 170) -> pd.DataFrame:
    """
    Analyzes how many of their expected hours each employee has fulfilled in a month.

    Args:
        employees (list): List of Employee objects (must have .name and .employment_rate attributes).
        schedule_json_path (str): Path to JSON file with assigned shifts (grouped by employee name).
        monthly_expected_fulltime (int): Expected hours for a full-time employee (default = 160).

    Returns:
        pd.DataFrame: Summary with scheduled hours, expected hours, and % fulfilled.
    """
    # Load schedule data
    with open(schedule_json_path, "r") as f:
        schedule = json.load(f)

    # Build lookup table for employment rates
    rate_lookup = {emp.name: emp.employment_rate for emp in employees}

    # Analyze each employee
    analysis = []
    for employee_name, shifts in schedule.items():
        print(shifts)
        total_hours = sum(calc_hours(shift["start"], shift["end"], shift["lunch"]) for shift in shifts)
        employment_rate = rate_lookup.get(employee_name, 1.0)
        expected_hours = employment_rate * monthly_expected_fulltime
        percent = (total_hours / expected_hours * 100) if expected_hours > 0 else 0

        analysis.append({
            "Employee": employee_name,
            "Employment Rate": employment_rate,
            "Scheduled Hours": round(total_hours, 1),
            "Expected Hours": round(expected_hours, 1),
            "% of Expected Hours": round(percent, 1)
        })

    return pd.DataFrame(analysis).sort_values("% of Expected Hours", ascending=False)

def analyze_total_staffing_balance(employees, schedule_json_path, monthly_expected_fulltime=170):
    """
    Analyzes the total scheduled hours versus the expected staffing hours.

    Args:
        employees (list of Employee): List of Employee objects.
        schedule_json_path (str): Path to the JSON schedule file.
        monthly_expected_fulltime (int): Expected monthly hours for full-time employees (default: 160 hours).

    Returns:
        dict: Summary containing total scheduled hours, expected hours, and the difference.
    """
    
    # Load schedule data from JSON
    with open(schedule_json_path, 'r') as file:
        schedule_data = json.load(file)

    total_scheduled_hours = 0

    # Calculate total scheduled hours
    for shifts in schedule_data.values():  # Iterate over employees' schedules
        for shift in shifts:
            start_time = datetime.strptime(shift["start"], "%H:%M")
            end_time = datetime.strptime(shift["end"], "%H:%M")
            shift_hours = (end_time - start_time).seconds / 3600  # Convert seconds to hours
            
            # Subtract lunch break if applicable
            if shift["lunch"] != "None":
                shift_hours -= 1  # Assume 1-hour lunch breaks
            
            total_scheduled_hours += shift_hours

    # Calculate total expected hours based on employee employment rates
    total_expected_hours = sum(emp.employment_rate * monthly_expected_fulltime for emp in employees)

    # Compare the scheduled and expected hours
    difference = total_scheduled_hours - total_expected_hours
    staffing_status = "Balanced"
    if difference > 0:
        staffing_status = "Understaffed"
    elif difference < 0:
        staffing_status = "Overstaffed"

    # Return results as a summary dictionary
    return {
        "total_scheduled_hours": round(total_scheduled_hours, 2),
        "total_expected_hours": round(total_expected_hours, 2),
        "difference": round(difference, 2),
        "status": staffing_status
    }

# Helper function to calculate shift hours
def calc_hours(start, end, lunch):
    s = datetime.strptime(start, "%H:%M")
    e = datetime.strptime(end, "%H:%M")
    hours = (e - s).seconds / 3600
    if lunch != "None":
        hours -= 1  # fixed 1-hour lunch break
    return max(hours, 0)