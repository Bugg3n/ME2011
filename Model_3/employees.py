from datetime import datetime, date
import sqlite3

# Class for the employees.

class Employee:

    def __init__(self, name, employment_rate, early_late_preference, spread, unavailable_dates=None, manager = False, overtime = False, emp_id=None, weekend_preference=5):
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
        
        if not isinstance(weekend_preference, int) or not (1 <= weekend_preference <= 10):
            raise ValueError("Weekend preference must be an int between 1 and 10.")
        
        self.weekend_preference = weekend_preference
        self.name = name.strip()
        self.employment_rate = employment_rate
        self.max_hours_per_week = employment_rate * 45
        self.early_late_preference = early_late_preference # 1 = Likes morning shifts, 10 = Likes Evening shifts.
        self.spread = spread
        self.manager = manager
        self.monthly_assigned_hours = 0
        self.schedule = []
        self.past_schedules = []
        self.is_available_for_overtime = overtime
        self.emp_id = emp_id
    
        if self.manager:
            self.set_sales_hour(10)

    def set_sales_hour(self, weekly_sales_hours): # Will be used to have the manager step in if needed
        if self.manager:
            self.max_hours_per_week = weekly_sales_hours
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
            weekly_max_hours = 40
        else:
            monthly_max_hours = int(monthly_max_hours * self.employment_rate)
            weekly_max_hours = self.max_hours_per_week

        if isinstance(shift_date, str):
            shift_date = date.fromisoformat(shift_date)

        # Check if employee is unavailable on that specific date
        if shift_date in self.unavailable_dates:
            if debug: print("Unavailable date")
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

        if self.get_total_weekly_hours(shift_date) + shift_hours > weekly_max_hours:
            if debug: print("too many hours this week")
            return False  
        
        if self.get_total_monthly_hours() + shift_hours > monthly_max_hours:
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
        # self.assigned_hours += shift_hours-lunch_break
        self.monthly_assigned_hours += shift_hours-lunch_break
        self.schedule.append({
            "date": shift["date"] if isinstance(shift["date"], str) else shift["date"].strftime("%Y-%m-%d"),
            "start": shift["start"],
            "end": shift["end"]
        })

    def remove_shift(self, shift):
        """Removes a shift from the employee's schedule and updates assigned hours."""
        shift_start_time = datetime.strptime(shift["start"], "%H:%M")
        shift_end_time = datetime.strptime(shift["end"], "%H:%M")
        shift_hours = (shift_end_time - shift_start_time).seconds // 3600
        lunch_break = 1 if shift.get("lunch", "None") != "None" else 0

        self.monthly_assigned_hours -= (shift_hours - lunch_break)

        # Remove from schedule
        self.schedule = [s for s in self.schedule if not (
            s["date"] == shift["date"] and
            s["start"] == shift["start"] and
            s["end"] == shift["end"]
        )]

    def get_total_weekly_hours(self, date_obj: date):
        """
        Returns total hours assigned during the same ISO week as the given date.
        :param date_obj: A datetime.date or datetime.datetime object.
        :return: Total hours worked in that ISO week.
        """
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        elif isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
            

        target_week = date_obj.isocalendar()[1]
        total = 0

        for shift in self.schedule:
            shift_date = datetime.strptime(shift["date"], "%Y-%m-%d").date()
            if shift_date.isocalendar()[1] == target_week:
                start = datetime.strptime(shift["start"], "%H:%M")
                end = datetime.strptime(shift["end"], "%H:%M")
                lunch_break = 1 if shift.get("lunch", "None") != "None" else 0
                total += ((end - start).seconds // 3600) - lunch_break

        return total

    def get_total_monthly_hours(self):
        return self.monthly_assigned_hours
    

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

    cursor.execute("""
        SELECT emp_id, name, employment_rate, early_late_preference, spread, manager,
            unavailable_dates, is_available_for_overtime, weekend_preference
        FROM employees
    """)    

    rows = cursor.fetchall()
    employees = []
    
    for row in rows:
        (emp_id, name, employment_rate, early_late_preference, spread, manager, unavailable_dates, is_available_for_overtime, weekend_preference) = row

        # Convert unavailable_dates (stored as comma-separated string) back into a list of date objects
        if unavailable_dates:
            unavailable_dates = [date.fromisoformat(d) for d in unavailable_dates.split(",")]
        else:
            unavailable_dates = []

        # Create Employee object
        employee = Employee(
            emp_id=emp_id,
            name=name,
            employment_rate=employment_rate,
            early_late_preference=early_late_preference,
            spread=spread,
            unavailable_dates=unavailable_dates,
            manager=bool(manager),
            overtime=is_available_for_overtime,
            weekend_preference=weekend_preference
        )
        employees.append(employee)

    conn.close()
    return employees