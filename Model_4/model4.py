from math import ceil
from datetime import datetime

def calculate_minimum_staffing(monthly_schedule, full_time_monthly_hours=170, target_employment_rate=0.8):
    """
    Estimate the minimum number of employees needed to cover all shifts in a month,
    based on target employment rate and scheduling constraints.

    Args:
        monthly_schedule (dict): A dictionary where each key is a date string (YYYY-MM-DD) and each value contains "shifts".
        full_time_monthly_hours (int): Maximum number of hours a full-time employee can work in a month.
        target_employment_rate (float): Target employment rate (e.g. 0.8 for 80%).

    Returns:
        dict: Estimated employee count and key figures.
    """

    avg_shift_length = calculate_average_shift_length(monthly_schedule)
    employee_capacity = full_time_monthly_hours * target_employment_rate

    total_required_hours = 0
    total_shifts_needed = 0
    work_days = set()

    for date_str, info in monthly_schedule.items():
        shifts = info.get("shifts", [])
        total_shifts_needed += len(shifts)
        total_required_hours += len(shifts) * avg_shift_length
        if shifts:
            work_days.add(date_str)

    # Max shifts one employee can take based on hours and 1 shift/day constraint
    max_shifts_per_employee = min(
        len(work_days),
        int(employee_capacity / avg_shift_length)
    )

    # Estimate based on hours
    employees_by_hours = ceil(total_required_hours / employee_capacity)
    # Estimate based on shift constraints
    employees_by_shifts = ceil(total_shifts_needed / max_shifts_per_employee)

    employees_needed = max(employees_by_hours, employees_by_shifts)

    return {
        "employees_needed": employees_needed,
        "total_required_hours": total_required_hours,
        "employee_capacity": employee_capacity,
        "total_shifts_needed": total_shifts_needed,
        "max_shifts_per_employee": max_shifts_per_employee,
        "employees_by_hours": employees_by_hours,
        "employees_by_shifts": employees_by_shifts,
        "work_days_count": len(work_days)
    }


def calculate_average_shift_length(monthly_schedule):
    total_hours = 0
    total_shifts = 0

    for _, info in monthly_schedule.items():
        for shift in info.get("shifts", []):
            start = datetime.strptime(shift["start"], "%H:%M")
            end = datetime.strptime(shift["end"], "%H:%M")
            shift_length = (end - start).seconds / 3600
            if shift.get("lunch", "None") != "None":
                shift_length -= 1  # subtract lunch hour
            total_hours += shift_length
            total_shifts += 1

    if total_shifts == 0:
        return 0.0

    return total_hours / total_shifts

def main():
    print("Nothing")


if __name__ == "__main__":
    main()