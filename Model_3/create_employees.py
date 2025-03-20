import sqlite3
from employees import Employee
from datetime import date

employees = [
    Employee(name="Alice", employment_rate=1.0, late_preference=5, early_preference=7, spread=5, unavailable_dates=["2025-03-15", "2025-03-22"]),
    Employee(name="Bob", employment_rate=0.8, late_preference=8, early_preference=3, spread=4, unavailable_dates=[date(2025, 3, 17)]),
    Employee(name="Ceasar", employment_rate=0.6, late_preference=7, early_preference=2, spread=3, unavailable_dates=[date(2025, 3, 18)]),
    Employee(name="David", employment_rate=0.4, late_preference=1, early_preference=8, spread=2, unavailable_dates=[date(2025, 3, 19)]),
    Employee(name="Eve", employment_rate=0.5, late_preference=10, early_preference=10, spread=1, unavailable_dates=[date(2025, 3, 22), date(2025, 3, 20)]),
        Employee(name="Frank", employment_rate=0.5, late_preference=8, early_preference=7, spread=5, unavailable_dates=[date(2025, 3, 18), date(2025, 3, 22), date(2025, 3, 10)]),
    Employee(name="Grace", employment_rate=0.7, late_preference=4, early_preference=7, spread=3, unavailable_dates=[date(2025, 3, 20), date(2025, 3, 15)]),
    Employee(name="Hank", employment_rate=0.5, late_preference=10, early_preference=9, spread=4, unavailable_dates=[date(2025, 3, 22), date(2025, 3, 23), date(2025, 3, 10)]),
    Employee(name="Ivy", employment_rate=0.9, late_preference=6, early_preference=2, spread=3, unavailable_dates=[date(2025, 3, 15), date(2025, 3, 21)]),
    Employee(name="Jack", employment_rate=0.4, late_preference=5, early_preference=8, spread=1, unavailable_dates=[date(2025, 3, 12), date(2025, 3, 10)]),
    Employee(name="Kara", employment_rate=0.5, late_preference=4, early_preference=1, spread=1, unavailable_dates=[date(2025, 3, 17), date(2025, 3, 11), date(2025, 3, 16)]),
    Employee(name="Liam", employment_rate=0.6, late_preference=9, early_preference=10, spread=1, unavailable_dates=[date(2025, 3, 24), date(2025, 3, 17)]),
    Employee(name="Mona", employment_rate=0.7, late_preference=7, early_preference=7, spread=4, unavailable_dates=[date(2025, 3, 23)]),
    Employee(name="Noah", employment_rate=0.5, late_preference=1, early_preference=1, spread=3, unavailable_dates=[date(2025, 3, 16), date(2025, 3, 18), date(2025, 3, 22)]),
    Employee(name="Olivia", employment_rate=0.5, late_preference=8, early_preference=1, spread=2, unavailable_dates=[date(2025, 3, 13)]),
    Employee(name="Paul", employment_rate=0.6, late_preference=10, early_preference=8, spread=4, unavailable_dates=[date(2025, 3, 18), date(2025, 3, 21)]),
    Employee(name="Quinn", employment_rate=0.7, late_preference=2, early_preference=3, spread=4, unavailable_dates=[date(2025, 3, 17)]),
    Employee(name="Riley", employment_rate=0.7, late_preference=3, early_preference=8, spread=2, unavailable_dates=[date(2025, 3, 17), date(2025, 3, 11), date(2025, 3, 13)]),
    Employee(name="Sophia", employment_rate=0.6, late_preference=2, early_preference=7, spread=1, unavailable_dates=[date(2025, 3, 11), date(2025, 3, 17)]),
    Employee(name="Tom", employment_rate=0.9, late_preference=6, early_preference=6, spread=2, unavailable_dates=[date(2025, 3, 17), date(2025, 3, 23), date(2025, 3, 16)]),
    Employee(name="Uma", employment_rate=0.6, late_preference=7, early_preference=8, spread=5, unavailable_dates=[date(2025, 3, 20)]),
    Employee(name="Victor", employment_rate=0.8, late_preference=6, early_preference=8, spread=4, unavailable_dates=[date(2025, 3, 22), date(2025, 3, 15), date(2025, 3, 20)]),
    Employee(name="Wendy", employment_rate=0.5, late_preference=10, early_preference=6, spread=4, unavailable_dates=[date(2025, 3, 14), date(2025, 3, 23)]),
    Employee(name="Xander", employment_rate=0.9, late_preference=2, early_preference=3, spread=3, unavailable_dates=[date(2025, 3, 17)]),
    Employee(name="Yasmine", employment_rate=0.9, late_preference=6, early_preference=4, spread=4, unavailable_dates=[date(2025, 3, 14), date(2025, 3, 13)])
]

# Connect to (or create) the database
conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    emp_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    employment_rate REAL NOT NULL,
    max_hours_per_week REAL NOT NULL,
    late_preference INTEGER NOT NULL,
    early_preference INTEGER NOT NULL,
    spread INTEGER NOT NULL,
    manager BOOLEAN NOT NULL,
    unavailable_dates TEXT
)
""")

def insert_employee(emp):
    cursor.execute("""
    INSERT INTO employees (emp_id, name, employment_rate, max_hours_per_week, 
                           late_preference, early_preference, spread, manager, unavailable_dates)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        emp.emp_id,
        emp.name,
        emp.employment_rate,
        emp.max_hours_per_week,
        emp.late_preference,
        emp.early_preference,
        emp.spread,
        emp.manager,
        ",".join([d.strftime("%Y-%m-%d") for d in emp.unavailable_dates])  # Store dates as comma-separated strings
    ))

# Insert employees into the database
for emp in employees:
    insert_employee(emp)

# Commit changes and close the connection
conn.commit()
conn.close()

print("✅ Employees database created successfully!")