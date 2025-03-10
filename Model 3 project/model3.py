from employees import Employee
from datetime import date

employees = [
    Employee(name="Alice", employment_rate=1.0, late_preference=2, early_preference=8, spread=5, unavailable_dates=["2025-03-15", "2025-03-22"]),
    Employee(name="Bob", employment_rate=0.8, late_preference=8, early_preference=2, spread=4, unavailable_dates=[date(2025, 3, 17)]),
]


for emp in employees:
    print(emp)

shift_date = "2025-03-15" # Alice should be unavailable
shift_start = "09:00"
shift_end = "17:00"

print(f"Alice available on {shift_date}? {employees[0].is_available(shift_date, shift_start, shift_end)}")
print(f"Bob available on {shift_date}? {employees[1].is_available(shift_date, shift_start, shift_end)}")


