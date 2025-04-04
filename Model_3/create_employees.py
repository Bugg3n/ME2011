import sqlite3
from employees import Employee
from datetime import date

employees = [
    # Employee(name="BC", employment_rate=1.0, early_late_preference=5, spread=5, unavailable_dates=[], overtime=False, manager=True, weekend_preference=6),
    Employee(name="Alice", employment_rate=0.8, early_late_preference=5, spread=5, unavailable_dates=["2025-03-15", "2025-03-22"], overtime=True, weekend_preference=8),
    Employee(name="Bob", employment_rate=0.8, early_late_preference=8, spread=4, unavailable_dates=[date(2025, 3, 17)], weekend_preference=9),
    Employee(name="Ceasar", employment_rate=0.6, early_late_preference=7, spread=3, unavailable_dates=[date(2025, 3, 18)], overtime=True, weekend_preference=1),
    Employee(name="David", employment_rate=0.5, early_late_preference=1, spread=2, unavailable_dates=[date(2025, 3, 19)], weekend_preference=3),
    Employee(name="Eve", employment_rate=0.5, early_late_preference=10, spread=1, unavailable_dates=[date(2025, 3, 22), date(2025, 3, 20)], overtime=True, weekend_preference=5),
    Employee(name="Frank", employment_rate=0.5, early_late_preference=8, spread=5, unavailable_dates=[date(2025, 3, 18), date(2025, 3, 22), date(2025, 3, 10)], weekend_preference=5),
    Employee(name="Grace", employment_rate=0.7, early_late_preference=4, spread=3, unavailable_dates=[date(2025, 3, 20), date(2025, 3, 15)], overtime=True, weekend_preference=5),
    Employee(name="Hank", employment_rate=0.5, early_late_preference=10, spread=4, unavailable_dates=[date(2025, 3, 22), date(2025, 3, 23), date(2025, 3, 10)], weekend_preference=7),
    Employee(name="Ivy", employment_rate=0.9, early_late_preference=6, spread=3, unavailable_dates=[date(2025, 3, 15), date(2025, 3, 21)], overtime=True, weekend_preference=10),
    Employee(name="Jack", employment_rate=0.4, early_late_preference=5, spread=1, unavailable_dates=[date(2025, 3, 12), date(2025, 3, 10)], weekend_preference=1),
    Employee(name="Kara", employment_rate=0.5, early_late_preference=4, spread=1, unavailable_dates=[date(2025, 3, 17), date(2025, 3, 11), date(2025, 3, 16)], weekend_preference=2),
    Employee(name="Liam", employment_rate=0.6, early_late_preference=9, spread=1, unavailable_dates=[date(2025, 3, 24), date(2025, 3, 17)], overtime=True, weekend_preference=8),]

# Connect to (or create) the database
conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

cursor.execute("""
DROP TABLE IF EXISTS employees;
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    employment_rate REAL NOT NULL,
    max_hours_per_week REAL NOT NULL,
    early_late_preference INTEGER NOT NULL,
    spread INTEGER NOT NULL,
    manager BOOLEAN NOT NULL,
    unavailable_dates TEXT,
    is_available_for_overtime BOOLEAN NOT NULL,
    weekend_preference INTEGER NOT NULL
)
""")

def insert_employee(emp):
    cursor.execute("""
    INSERT INTO employees (name, employment_rate, max_hours_per_week, 
                           early_late_preference, spread, manager, unavailable_dates, 
                           is_available_for_overtime, weekend_preference)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        emp.name,
        emp.employment_rate,
        emp.max_hours_per_week,
        emp.early_late_preference,
        emp.spread,
        emp.manager,
        ",".join([d.strftime("%Y-%m-%d") for d in emp.unavailable_dates]),
        emp.is_available_for_overtime,
        emp.weekend_preference
    ))
    emp.emp_id = cursor.lastrowid


# Insert employees into the database
for emp in employees:
    insert_employee(emp)

# Commit changes and close the connection
conn.commit()
conn.close()

print("✅ Employees database created successfully!")