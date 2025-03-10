from datetime import datetime, date


class Employee:
    _id_counter = 1

    def __init__(self, name, employment_rate, late_preference, early_preference, spread, unavailable_dates=None, manager = False):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string.")
        
        if not isinstance(employment_rate, (int, float)) or not (0 <= employment_rate <= 1):
            raise ValueError("Employment rate must be a number between 0 and 1.")
        
        if not isinstance(late_preference, int) or not (1 <= late_preference <= 10):
            raise ValueError("late preference must be an int between 1 and 10")
        
        if not isinstance(early_preference, int) or not (1 <= early_preference <= 10):
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
        
        self.emp_id = f"E{Employee._id_counter}"
        Employee._id_counter += 1
        self.name = name.strip()
        self.employment_rate = employment_rate
        self.max_hours_per_week = employment_rate * 40
        self.late_preference = late_preference
        self.early_preference = early_preference
        self.spread = spread
        self.manager = manager
        self.assigned_hours = 0
        self.schedule = []
        self.past_schedules = []


    def is_available(self, shift_date, shift_start, shift_end):
        """
        Check if the employee is available on a given date and time.
        :param shift_date: A string 'YYYY-MM-DD' or a date object.
        :param shift_start: Start time in 'HH:MM' format.
        :param shift_end: End time in 'HH:MM' format.
        :return: True if available, False if unavailable.
        """
        # TODO: Should probably also check if person already has a shift on this day.
        if isinstance(shift_date, str):
            shift_date = date.fromisoformat(shift_date)

        if shift_date in self.unavailable_dates:
            return False  # Employee is unavailable on this specific date

        shift_start_time = datetime.strptime(shift_start, "%H:%M")
        shift_end_time = datetime.strptime(shift_end, "%H:%M")
        shift_hours = (shift_end_time - shift_start_time).seconds // 3600  # Convert to hours

        if self.assigned_hours + shift_hours > self.max_hours_per_week:
            return False  # Would exceed weekly hour limit

        return True
    
    
    def assign_shift(self, shift_date, shift_start, shift_end):
        """Assigns a shift to the employee and updates hours."""
        shift_start_time = datetime.strptime(shift_start, "%H:%M")
        shift_end_time = datetime.strptime(shift_end, "%H:%M")
        shift_hours = (shift_end_time - shift_start_time).seconds // 3600  # Convert to hours
        self.assigned_hours += shift_hours
        self.schedule.append({
            "date": shift_date if isinstance(shift_date, str) else shift_date.strftime("%Y-%m-%d"),
            "start": shift_start,
            "end": shift_end
        })
        
    def reset_weekly_schedule(self):
        """Moves the current schedule to history and resets weekly counters."""
        if self.schedule:
            self.past_schedules.append({
                "week": datetime.now().strftime("%Y-%W"),
                "shifts": self.schedule.copy()
            })
            self.schedule = []
            self.assigned_hours = 0

    if __name__ == "__main__":
        print("This should NOT be executed during import.")



