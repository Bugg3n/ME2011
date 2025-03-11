import sqlite3
from employees import Employee
from datetime import date

employees = [
    Employee(name="Alice", employment_rate=1.0, late_preference=5, early_preference=7, spread=5, unavailable_dates=["2025-03-15", "2025-03-22"]),
    Employee(name="Bob", employment_rate=0.8, late_preference=8, early_preference=3, spread=4, unavailable_dates=[date(2025, 3, 17)]),
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