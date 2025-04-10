from math import ceil
from itertools import combinations
from datetime import datetime
import os
import sys
# insert root directory into python module search path
sys.path.insert(1, os.getcwd())
from Model_3 import employees, model3


def calculate_minimum_staffing(monthly_schedule, full_time_monthly_hours=170, target_employment_rate=0.8, efficiency_factor = 0.9):
    """
    Estimate the minimum number of employees needed to cover all shifts in a month,
    based on target employment rate, scheduling constraints, and max daily concurrency.

    Args:
        monthly_schedule (dict): A dictionary where each key is a date string (YYYY-MM-DD) and each value contains "shifts".
        full_time_monthly_hours (int): Maximum number of hours a full-time employee can work in a month.
        target_employment_rate (float): Target employment rate (e.g. 0.8 for 80%).

    Returns:
        dict: Estimated employee count and key figures.
    """

    total_required_hours, total_shifts_needed = calculate_average_shift_length(monthly_schedule)
    employee_capacity = full_time_monthly_hours * target_employment_rate * efficiency_factor

    work_days = set()
    max_employees_per_day = 0

    for date_str, info in monthly_schedule.items():
        shifts = info.get("shifts", [])
        if shifts:
            work_days.add(date_str)
            max_employees_per_day = max(max_employees_per_day, len(shifts))

    avg_shift_length = total_required_hours / total_shifts_needed if total_shifts_needed > 0 else 0

    max_shifts_per_employee = min(
        len(work_days),
        int(employee_capacity / avg_shift_length) if avg_shift_length else 0
    )

    employees_by_hours = ceil(total_required_hours / employee_capacity)
    employees_by_shifts = ceil(total_shifts_needed / max_shifts_per_employee) if max_shifts_per_employee > 0 else 0

    employees_needed = max(employees_by_hours, employees_by_shifts, max_employees_per_day)

    return {
        "employees_needed": employees_needed,
        "total_required_hours": total_required_hours,
        "employee_capacity": employee_capacity,
        "total_shifts_needed": total_shifts_needed,
        "max_shifts_per_employee": max_shifts_per_employee,
        "employees_by_hours": employees_by_hours,
        "employees_by_shifts": employees_by_shifts,
        "max_employees_needed_one_day": max_employees_per_day,
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

    return total_hours, total_shifts

def merge_employees(emp1, emp2):
    merged = employees.Employee(
        name=f"{emp1.name}_{emp2.name}_merged",
        employment_rate=min(1, emp1.employment_rate + emp2.employment_rate),
        early_late_preference=int((emp1.early_late_preference + emp2.early_late_preference) / 2),
        weekend_preference=int((emp1.weekend_preference + emp2.weekend_preference) / 2),
        spread=int((emp1.spread + emp2.spread) / 2),
        manager=emp1.manager or emp2.manager
    )
    return merged

def optimize_staffing_by_merging(monthly_schedule, employees, year, month, last_month_schedule, max_hours):
    best_employees = employees[:]
    improved = True

    while improved:
        improved = False

        # Sort by employment rate ascending
        best_employees.sort(key=lambda e: e.employment_rate)

        # Try pair merges first
        for i in range(len(best_employees)):
            for j in range(i + 1, len(best_employees)):
                e1, e2 = best_employees[i], best_employees[j]

                if e1.employment_rate + e2.employment_rate > 1.0:
                    continue

                merged = merge_employees(e1, e2)
                trial_employees = (
                    best_employees[:i]
                    + best_employees[i+1:j]
                    + best_employees[j+1:]
                    + [merged]
                )

                try:
                    assigned, unassigned, _ = model3.create_schedule(
                        monthly_schedule,
                        trial_employees,
                        year,
                        month,
                        last_month_schedule,
                        max_hours
                    )
                    if not unassigned:
                        print(f"✅ Merged {e1.name} and {e2.name}")
                        best_employees = trial_employees
                        improved = True
                        break
                except Exception as e:
                    print(f"⚠️ Merge error ({e1.name}+{e2.name}): {e}")
            if improved:
                break

        # Now try merging 3 into 2
        if not improved:
            for e1, e2, e3 in combinations(best_employees, 3):
                total_rate = e1.employment_rate + e2.employment_rate + e3.employment_rate
                if total_rate <= 2.0:
                    # Make two new employees at equal rate
                    rate_each = total_rate / 2
                    merged1 = merge_employees(e1, e2)
                    merged1.name += "_1"
                    merged1.employment_rate = rate_each

                    merged2 = merge_employees(e1, e3)  # doesn't really matter which
                    merged2.name += "_2"
                    merged2.employment_rate = rate_each

                    trial_employees = [
                        emp for emp in best_employees if emp not in [e1, e2, e3]
                    ] + [merged1, merged2]

                    try:
                        assigned, unassigned, _ = model3.create_schedule(
                            monthly_schedule,
                            trial_employees,
                            year,
                            month,
                            last_month_schedule,
                            max_hours
                        )
                        if not unassigned:
                            print(f"✅ Merged {e1.name}, {e2.name}, {e3.name} into 2 employees at {rate_each:.2f}")
                            best_employees = trial_employees
                            improved = True
                            break
                    except Exception as e:
                        print(f"⚠️ Merge3 error ({e1.name},{e2.name},{e3.name}): {e}")
            if improved:
                break

    return best_employees

def test_minimum_staffing_feasibility(monthly_schedule, year, month, last_month_schedule, hours_per_month, open = "8:00", close = "22:00", max_daily_hours = 10, target_employment_rate = 0.8, efficiency_factor=0.9):
    result = calculate_minimum_staffing(monthly_schedule, hours_per_month, target_employment_rate, efficiency_factor)
    num_employees = result["employees_needed"]
    employees = generate_test_employees(num_employees, rate=0.8)

    assigned, unassigned, _ = model3.create_schedule(
        monthly_schedule,
        employees,
        year,
        month,
        last_month_schedule,
        max_hours=hours_per_month,
        debug=False,
        store_open=open,
        store_close=close,
        max_daily_hours=10
    )

    result["can_fill_schedule"] = len(unassigned) == 0
    result["unassigned_count"] = len(unassigned)
    return result

from Model_3.employees import Employee

def generate_test_employees(num_employees, rate=0.8):
    return [
        Employee(
            name=f"AutoEmp_{i+1}",
            employment_rate=rate,
            early_late_preference=5,
            weekend_preference=5,
            spread=5,
            manager=False
        )
        for i in range(num_employees)
    ]


