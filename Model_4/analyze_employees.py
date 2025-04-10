import json
from datetime import datetime
import pandas as pd

def analyze_monthly_hours_from_employees(employees: list, assigned_shifts: dict, monthly_expected_fulltime: int = 170) -> pd.DataFrame:
    """
    Analyzes how many of their expected hours each employee has fulfilled in a month,
    using assigned_shifts directly (not from a JSON file).

    Args:
        employees (list): List of Employee objects (must have .name and .employment_rate attributes).
        assigned_shifts (dict): Dictionary with employee names as keys and list of shifts as values.
        monthly_expected_fulltime (int): Expected hours for a full-time employee (default = 170).

    Returns:
        pd.DataFrame: Summary with scheduled hours, expected hours, and % fulfilled.
    """
    # Build lookup table for employment rates
    rate_lookup = {emp.name: emp.employment_rate for emp in employees}

    # Analyze each employee
    analysis = []
    for employee_name, shifts in assigned_shifts.items():
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

from datetime import datetime

def analyze_total_staffing_balance(employees, assigned_shifts, monthly_expected_fulltime=170, unassigned_shifts=None, total_required_hours=None):
    """
    Analyzes the total scheduled hours versus the expected staffing hours using assigned_shifts directly.

    Args:
        employees (list of Employee): List of Employee objects.
        assigned_shifts (dict): Dictionary with employee names as keys and list of shifts as values.
        monthly_expected_fulltime (int): Expected monthly hours for full-time employees (default: 170).
        unassigned_shifts (list, optional): List of unassigned shifts.
        total_required_hours (float, optional): Total required store coverage hours.

    Returns:
        dict: Summary containing total scheduled hours, expected hours, and the difference.
    """
    total_scheduled_hours = 0

    # Calculate total scheduled hours
    for shifts in assigned_shifts.values():
        for shift in shifts:
            start_time = datetime.strptime(shift["start"], "%H:%M")
            end_time = datetime.strptime(shift["end"], "%H:%M")
            shift_hours = (end_time - start_time).seconds / 3600

            if shift["lunch"] != "None":
                shift_hours -= 1

            total_scheduled_hours += shift_hours

    # Calculate total expected hours based on employee employment rates
    total_expected_hours = sum(emp.employment_rate * monthly_expected_fulltime for emp in employees)

    # Compare the scheduled and expected hours
    difference = float(total_required_hours) - float(total_expected_hours)
    staffing_status = "Balanced"
    if difference > 0:
        staffing_status = "Understaffed"
    elif difference < total_required_hours * -0.1:
        staffing_status = "Overstaffed"

    result = {
        "total_scheduled_hours": round(total_scheduled_hours, 2),
        "total_expected_hours": round(total_expected_hours, 2),
        "total_required_hours": round(total_required_hours, 2),
        "staff shortage": round(difference, 2),
        "status": staffing_status,
        "note": None
    }

    if total_required_hours is not None:
        coverage_ratio = total_scheduled_hours / total_required_hours
        result["store_coverage_%"] = round(coverage_ratio * 100, 1)

        if coverage_ratio < 0.9:
            result["coverage_status"] = "Under-covered"
        elif coverage_ratio > 1.05:
            result["coverage_status"] = "Over-covered"
        else:
            result["coverage_status"] = "Balanced"

    if unassigned_shifts and len(unassigned_shifts) > 0:
        result["note"] = f"{len(unassigned_shifts)} shifts were unassigned due to lack of available staff."

    return result

# Helper function to calculate shift hours
def calc_hours(start, end, lunch):
    s = datetime.strptime(start, "%H:%M")
    e = datetime.strptime(end, "%H:%M")
    hours = (e - s).seconds / 3600
    if lunch != "None":
        hours -= 1  # fixed 1-hour lunch break
    return max(hours, 0)

def calculate_total_required_hours(monthly_schedule):
    total_required_hours = 0
    for day in monthly_schedule.values():
        for shift in day["shifts"]:
            start_time = datetime.strptime(shift["start"], "%H:%M")
            end_time = datetime.strptime(shift["end"], "%H:%M")
            shift_hours = (end_time - start_time).seconds / 3600
            if shift["lunch"] != "None":
                shift_hours -= 1
            total_required_hours += shift_hours
    return total_required_hours
