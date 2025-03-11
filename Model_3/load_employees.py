import sqlite3
from employees import Employee
from datetime import datetime, date

def load_employees():
    """Fetch employees from the database and return a list of Employee objects."""
    
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    cursor.execute("SELECT emp_id, name, employment_rate, late_preference, early_preference, spread, manager, unavailable_dates FROM employees")
    rows = cursor.fetchall()

    employees = []
    
    for row in rows:
        emp_id, name, employment_rate, late_preference, early_preference, spread, manager, unavailable_dates = row

        # Convert unavailable_dates (stored as comma-separated string) back into a list of date objects
        if unavailable_dates:
            unavailable_dates = [date.fromisoformat(d) for d in unavailable_dates.split(",")]
        else:
            unavailable_dates = []

        # Create Employee object
        employee = Employee(
            name=name,
            employment_rate=employment_rate,
            late_preference=late_preference,
            early_preference=early_preference,
            spread=spread,
            unavailable_dates=unavailable_dates,
            manager=bool(manager)
        )
        
        employees.append(employee)

    conn.close()
    return employees
