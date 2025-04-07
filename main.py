from Model_1 import model1
from Model_2 import model2
from Model_3 import model3
from Model_3.employees import *
from Model_4 import model4
import os
import calendar
import json
from visualize import generate_html, generate_employee_summary_html
from Model_4.analyze_employees import *
from webserver.webserver import *
import csv


YEAR = 2025
MONTH = 2
STORE_ID = "1"
SALES_CAPACITY = 12  # Customers per employee per hour
SCHEDULE_FOLDER = "schedules"
CUSTOMER_FLOW_PER_HOUR = [23, 8, 8, 4, 8, 8, 35, 40, 38, 32, 25, 13, 15, 10]
DEBUG = False
STORE_OPEN = "8:00"
STORE_CLOSE = "22:00"
MAX_DAILY_HOURS = 10
TARGET_EMPLOYMENT_RATE = 0.8
EFFICIENCY_FACTOR = 0.95

HOURS_PER_MONTH = {
    1: 176,
    2: 160,
    3: 168,
    4: 160,
    5: 160,
    6: 144,
    7: 184,
    8: 168,
    9: 176,
    10: 184,
    11: 160,
    12: 168,
}


#TODO
# Färdigställa modell 3
    # Implementera spread
        # När vi får data från Kjell:
        # Experimentera med olika sätt att välja den bästa employeen. Probabalistiskt eller deterministiskt?
        

# Städa model2. Ta bort funktioner som inte används
# Fixa model 1 när vi får data från Kjell

# Model 4 - Räkna ut minsta antalet anställda och deras anställningsgrader som krävs för att driva butiken under ett år.
# Maximalt antal samtida anställda
# Antalet timmar uppnås
# Inga kollektivavtalsregler bryts
# Utifrånd detta räkna ut minsta antal anställda med högsta möjliga anställningsgrad


#get data from kjell
def get_data():
    return 0


#Recieves demand for the store from model1
def get_demand():
    demand = model1.main(CUSTOMER_FLOW_PER_HOUR, SALES_CAPACITY)
    return 0

def ensure_schedule_folder():
    """Ensure that the schedules folder exists."""
    if not os.path.exists(SCHEDULE_FOLDER):
        os.makedirs(SCHEDULE_FOLDER)


#a function to create a schedule
def create_schedule(web_mode=False, web_params = None):
    """Main function to create an optimized monthly employee schedule."""
    ensure_schedule_folder()
    sales_capacity = SALES_CAPACITY
    if web_params:
        sales_capacity = web_params.get('sales_capacity', SALES_CAPACITY)
        average_service_time = web_params.get('average_service_time', 10)
        target_wait_time = web_params.get('target_wait_time', 5)

    print(f"📅 Getting staffing requirements from Model 1 for {calendar.month_name[MONTH]} {YEAR}...")
    
    # Step 1: Generate staffing needs (Model 1)
    monthly_staffing = model1.generate_monthly_staffing(YEAR, MONTH, STORE_ID, sales_capacity)


    print(f"📊 Generating shift schedules for {calendar.month_name[MONTH]} {YEAR}...")

    # Step 2: Pass staffing data to Model 2 for scheduling
    monthly_schedule = model2.generate_monthly_schedule(
        year=YEAR,
        month=MONTH,
        store_id=STORE_ID,
        monthly_staffing=monthly_staffing,
        visualize=False  # Set to True if you want to visualize daily schedules
    )
    
    total_required_hours = calculate_total_required_hours(monthly_schedule)
    employees = load_employees()
    last_month_schedule = get_last_month_schedule(YEAR, MONTH)

    print(f"📅 Assigning shifts to employees for {calendar.month_name[MONTH]} {YEAR}...")

    
    # Step 3: Assign shifts to employees (Model 3)
    assigned_shifts, unassigned_shifts, assigned_shifts_by_date = model3.create_schedule(
        monthly_schedule, 
        employees, 
        YEAR, MONTH, 
        last_month_schedule, 
        max_hours=HOURS_PER_MONTH[MONTH], 
        debug = DEBUG,
        store_open = STORE_OPEN, 
        store_close = STORE_CLOSE, 
        max_daily_hours = MAX_DAILY_HOURS, 
        )
    
    assigned_shifts_by_date = inject_unassigned_into_schedule(assigned_shifts_by_date, unassigned_shifts)
    df_summary, staffing_summary = analyze_employees(employees=employees, assigned_shifts=assigned_shifts, unassigned_shifts=unassigned_shifts, monthly_expected_fulltime = HOURS_PER_MONTH[MONTH], total_required_hours = total_required_hours)
    export_schedule(assigned_shifts, unassigned_shifts, assigned_shifts_by_date, df_summary, staffing_summary)

    print(model4.test_minimum_staffing_feasibility(monthly_schedule, YEAR, MONTH, last_month_schedule, HOURS_PER_MONTH[MONTH], open = STORE_OPEN, close = STORE_CLOSE, max_daily_hours = MAX_DAILY_HOURS, target_employment_rate=TARGET_EMPLOYMENT_RATE, efficiency_factor=EFFICIENCY_FACTOR))
    
    best_employees = model4.optimize_staffing_by_merging(monthly_schedule, employees, YEAR, MONTH, last_month_schedule, HOURS_PER_MONTH[MONTH])    
    for emp in best_employees:
        print(f"name: {emp.name}, emp_rate: {emp.employment_rate}")

    return assigned_shifts_by_date, unassigned_shifts, staffing_summary


def analyze_employees(employees, assigned_shifts, unassigned_shifts, monthly_expected_fulltime, total_required_hours):
    df_summary = analyze_monthly_hours_from_employees(employees = employees, assigned_shifts = assigned_shifts, monthly_expected_fulltime = monthly_expected_fulltime)
    staffing_summary = analyze_total_staffing_balance(employees, assigned_shifts, monthly_expected_fulltime, unassigned_shifts, total_required_hours)
    return df_summary, staffing_summary


def export_schedule(assigned_shifts, unassigned_shifts, assigned_shifts_by_date, df_summary, staffing_summary):    
    
    # Save final schedule
    schedule_filename = os.path.join(SCHEDULE_FOLDER, f"final_schedule_{YEAR}_{MONTH}.json")
    with open(schedule_filename, "w") as f:
        json.dump(assigned_shifts, f, indent=4)

    print(f"✅ Final employee schedule saved to {schedule_filename}")

    export_schedule_to_csv(assigned_shifts, filename=f"csv-files/final_schedule_{YEAR}_{MONTH}.csv")

    schedule_by_date_filename = os.path.join(SCHEDULE_FOLDER, f"final_schedule_{YEAR}_{MONTH}_by_date.json")
    with open(schedule_by_date_filename, "w") as f:
        json.dump(assigned_shifts_by_date, f, indent=4)

    summary_html = generate_employee_summary_html(df_summary)

    os.makedirs("HTML-files", exist_ok=True)

    with open("HTML-files/employee_summary.html", "w", encoding="utf-8") as f:
        f.write(summary_html)

    # Step 5: Visualize the final schedule
    print(f"📊 Opening schedule visualization...")
    
    generate_html(assigned_shifts_by_date, unassigned_shifts, staffing_summary, output_path="HTML-files/monthly_schedule.html")


def inject_unassigned_into_schedule(assigned_by_date, unassigned_shifts):
    """Adds unassigned shifts to the schedule dictionary as Unassigned 1, 2, etc."""
    unassigned_counter = {}

    for i, shift in enumerate(unassigned_shifts, start=1):
        date = shift["date"]
        label = f"Unassigned {i}"

        if date not in assigned_by_date:
            assigned_by_date[date] = {}

        if label not in assigned_by_date[date]:
            assigned_by_date[date][label] = []

        assigned_by_date[date][label].append({
            "start": shift["start"],
            "end": shift["end"],
            "lunch": "None",  # or leave out if not needed
            "date": date,
            "unassigned": True
        })

    return assigned_by_date
    
def get_last_month_schedule (year, month):
    last_year, last_month = get_last_month(year, month)
    last_schedule_filename = f"final_schedule_{last_year}_{last_month}.json"
    last_month_schedule = {}

    # Check if last month's schedule exists
    if os.path.exists(last_schedule_filename):
        print(f"📂 Found last month's schedule: {last_schedule_filename}")
        with open(last_schedule_filename, "r") as f:
            last_month_schedule = json.load(f)
            return last_month_schedule
    else:
        print(f"⚠️ No schedule found for {calendar.month_name[last_month]} {last_year}. Proceeding without carry-over data.")
        return None

def get_last_month(year, month):
    if month == 1:
        last_year = year - 1
        last_month = 12
    else:
        last_year = year
        last_month = month - 1
    return last_year, last_month

import csv
from datetime import datetime

def export_schedule_to_csv(assigned_shifts, filename="final_schedule.csv"):
    # Calculate monthly hours per employee
    monthly_hours = {}
    for employee, shifts in assigned_shifts.items():
        total_hours = 0
        for shift in shifts:
            start = datetime.strptime(shift["start"], "%H:%M")
            end = datetime.strptime(shift["end"], "%H:%M")
            duration = (end - start).seconds / 3600
            if shift.get("lunch") != "None":
                duration -= 1
            total_hours += duration
        monthly_hours[employee] = round(total_hours, 2)

    with open(filename, mode="w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["Employee", "Date", "Weekday", "Start", "End", "Lunch", "Duration", "Monthly Total Hours"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for employee, shifts in assigned_shifts.items():
            first = True
            for shift in shifts:
                start = datetime.strptime(shift["start"], "%H:%M")
                end = datetime.strptime(shift["end"], "%H:%M")
                duration = (end - start).seconds / 3600
                if shift.get("lunch") != "None":
                    duration -= 1

                date_obj = datetime.strptime(shift["date"], "%Y-%m-%d")
                weekday = date_obj.strftime("%A")

                writer.writerow({
                    "Employee": employee,
                    "Date": shift["date"],
                    "Weekday": weekday,
                    "Start": shift["start"],
                    "End": shift["end"],
                    "Lunch": shift.get("lunch", "None"),
                    "Duration": round(duration, 2),
                    "Monthly Total Hours": monthly_hours[employee] if first else ""
                })
                first = False

    print(f"✅ Schedule exported to {filename}")

def main():
    os.environ['WEB_MODE'] = "0"
    
    # Start server (which will now auto-open browser)
    monthly_schedule = create_schedule()

    print("Starting server at http://localhost:8000")
    print("Browser should open automatically...")
    run_server()


if __name__ == "__main__":
    main()