from datetime import datetime, date
import sqlite3

# Class for the employees.

class Employee:

    def __init__(self, name, employment_rate, early_late_preference, spread, unavailable_dates=None, manager = False, overtime = False, emp_id=None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string.")
        
        if not isinstance(employment_rate, (int, float)) or not (0 <= employment_rate <= 1):
            raise ValueError("Employment rate must be a number between 0 and 1.")
                
        if not isinstance(early_late_preference, int) or not (1 <= early_late_preference <= 10):
            raise ValueError("early preference must be an int between 1 and 10")
        
        if not isinstance(spread, int) or not (1 <= spread <= 10):
            raise ValueError("spread must be an int between 1 and 10")
        
        if unavailable_dates:
            if not isinstance(unavailable_dates, list) or not all(isinstance(d, (str, date)) for d in unavailable_dates):
                raise ValueError("Unavailable dates must be a list of strings in 'YYYY-MM-DD' format or date objects.")
            self.unavailable_dates = [date.fromisoformat(d) if isinstance(d, str) else d for d in unavailable_dates]
        else:
            self.unavailable_dates = []

        if not isinstance(manager, bool):
            raise ValueError("Manager must be a boolean (True/False).")
        

        self.weekly_sales_hours = None
        self.name = name.strip()
        self.employment_rate = employment_rate
        self.max_hours_per_week = employment_rate * 45
        self.early_late_preference = early_late_preference # 1 = Likes morning shifts, 10 = Likes Evening shifts.
        self.spread = spread
        self.manager = manager
        self.assigned_hours = 0
        self.monthly_assigned_hours = 0
        self.schedule = []
        self.past_schedules = []
        self.is_available_for_overtime = overtime
        self.emp_id = emp_id
    
        if self.manager:
            self.set_sales_hour(5)

    def set_sales_hour(self, weekly_sales_hours): # Will be used to have the manager step in if needed
        if self.manager:
            self.weekly_sales_hours = weekly_sales_hours
            return True
        else: 
            return False

    def is_available(self, shift_date, shift_start, shift_end, monthly_max_hours, debug = False, overtime = False):
        """
        Check if the employee is available on a given date and time.
        :param shift_date: A string 'YYYY-MM-DD' or a date object.
        :param shift_start: Start time in 'HH:MM' format.
        :param shift_end: End time in 'HH:MM' format.
        :return: True if available, False if unavailable.
        """
        if debug: print({f"Checking if {self.name} is available for the shift on {shift_date} between {shift_start} and {shift_end}"})
        if overtime:
            monthly_max_hours = monthly_max_hours
        else:
            monthly_max_hours = int(monthly_max_hours * self.employment_rate)

        if isinstance(shift_date, str):
            shift_date = date.fromisoformat(shift_date)

        # Check if employee is unavailable on that specific date
        if shift_date in self.unavailable_dates:
            return False  

        shift_start_time = datetime.strptime(shift_start, "%H:%M")
        shift_end_time = datetime.strptime(shift_end, "%H:%M")
        shift_hours = (shift_end_time - shift_start_time).seconds // 3600  

        # Check if employee already has a shift on that day
        for shift in self.schedule:
            if date.fromisoformat(shift["date"]) == shift_date:
                if debug: print("already scheduled today")
                return False  # The employee already has a shift that day, so unavailable

        # Check if adding this shift exceeds max weekly hours
        if self.assigned_hours + shift_hours > self.max_hours_per_week:
            if debug: print("too many hours this week")
            return False  
        
        if self.monthly_assigned_hours + shift_hours > monthly_max_hours:

            if debug: print("too many hours this month")
            return False  

        return True
    
    def is_available_for_overtime_function(self, shift_date, shift_start, shift_end, monthly_max_hours, debug = False):
        
        if self.is_available_for_overtime:
            return self.is_available(shift_date, shift_start, shift_end, monthly_max_hours, debug = debug, overtime = True)
        return False
    
    
    def assign_shift(self, shift):
        """Assigns a shift to the employee and updates hours."""
        shift_start_time = datetime.strptime(shift["start"], "%H:%M")
        shift_end_time = datetime.strptime(shift["end"], "%H:%M")
        shift_hours = (shift_end_time - shift_start_time).seconds // 3600  # Convert to hours
        lunch_break = 1 if shift["lunch"] != "None" else 0
        self.assigned_hours += shift_hours-lunch_break
        self.monthly_assigned_hours += shift_hours-lunch_break
        self.schedule.append({
            "date": shift["date"] if isinstance(shift["date"], str) else shift["date"].strftime("%Y-%m-%d"),
            "start": shift["start"],
            "end": shift["end"]
        })
        
    def reset_weekly_schedule(self):
        self.assigned_hours = 0

    def reset_monthly_schedule(self):
        if self.schedule:
            self.past_schedules.append({
                "month": datetime.now().strftime("%Y-%M"),
                "shifts": self.schedule.copy()
            })
            self.schedule = []
            self.monthly_assigned_hours = 0


def load_employees():
    """Fetch employees from the database and return a list of Employee objects."""
    
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    cursor.execute("SELECT emp_id, name, employment_rate, early_late_preference, spread, manager, unavailable_dates, is_available_for_overtime FROM employees")
    rows = cursor.fetchall()

    employees = []
    
    for row in rows:
        emp_id, name, employment_rate, early_late_preference, spread, manager, unavailable_dates, is_available_for_overtime = row

        # Convert unavailable_dates (stored as comma-separated string) back into a list of date objects
        if unavailable_dates:
            unavailable_dates = [date.fromisoformat(d) for d in unavailable_dates.split(",")]
        else:
            unavailable_dates = []

        # Create Employee object
        employee = Employee(
            emp_id = emp_id,
            name=name,
            employment_rate=employment_rate,
            early_late_preference=early_late_preference,
            spread=spread,
            unavailable_dates=unavailable_dates,
            manager=bool(manager),
            overtime=is_available_for_overtime
        )
        
        employees.append(employee)

    conn.close()
    return employees