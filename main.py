from Model_1 import model1
from Model_2 import model2
from Model_3 import model3
from Analysis import analyze_employees
import os
import calendar
import json
# from visualize import main as visualize_model_3
from Analysis.visualize2 import generate_html as visualize_schedule
from Analysis.analyze_employees import *

from Model_3.employees import *

YEAR = 2025
MONTH = 1
STORE_ID = "1"
SALES_CAPACITY = 12  # Customers per employee per hour
SCHEDULE_FOLDER = "schedules"
SALES_CAPACITY = 12
CUSTOMER_FLOW_PER_HOUR = [23, 8, 8, 4, 8, 8, 35, 40, 38, 32, 25, 13, 15, 10]

hour_per_month = {
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
    # 1 skala 1-10 istället för 2
    # Input för hur gärna du vill jobba helg
    # Vikta den som blir tilldelad pass baserat på svaren jämfört med varandra (probalistiskt)
    # Implementera chefs-roll som buffert
    # Fixa visualiseringen och lägg till knappen för kundflöde under dagen
    # Ta fram funktioner för statistik om anställda

# Funktion för att se till att alla timmar för varje anställd uppnås
# Om den anställda vill arbeta mer - Om det beövs fler arbtestimmar efter att allas kontrakt är uppfyllda tas timmar härifrån i proportion till arbetsgrad
# Städa model2. Ta bort funktioner som inte används
# Lägg till ReadMe-fil och förklaringar för varje modul
# Fixa model 1
# Flytta all visualisering till vizualize.py

# Model 4?
# Maximalt antal samtida anställda
# Antalet timmar uppnås
# Inga kollektivavtalsregler bryts
# Utifrånd detta räkna ut minsta antal anställda med högsta möjliga anställningsgrad




# Här ska alla parametrar finnas


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


def main():
    """Main function to create an optimized monthly employee schedule."""

    ensure_schedule_folder()

    print(f"📅 Getting staffing requirements from Model 1 for {calendar.month_name[MONTH]} {YEAR}...")
    
    # Step 1: Generate staffing needs (Model 1)
    monthly_staffing = model1.generate_monthly_staffing(YEAR, MONTH, STORE_ID, SALES_CAPACITY)

    print(f"📊 Generating shift schedules for {calendar.month_name[MONTH]} {YEAR}...")

    # Step 2: Pass staffing data to Model 2 for scheduling
    monthly_schedule = model2.generate_monthly_schedule(
        year=YEAR,
        month=MONTH,
        store_id=STORE_ID,
        monthly_staffing=monthly_staffing,  # Passing this instead of calling model1 inside model2
        visualize=False  # Set to True if you want to visualize daily schedules
    )

    print(f"👥 Loading employees...")
    employees = load_employees()

    print(f"🔍 Checking for previous month's schedule...")
    last_month_schedule = get_last_month_schedule(YEAR, MONTH)

    print(f"📅 Assigning shifts to employees for {calendar.month_name[MONTH]} {YEAR}...")

    print(f"📅 Assigning shifts to employees for {calendar.month_name[MONTH]} {YEAR}...")

    # Step 3: Assign shifts to employees (Model 3)
    assigned_shifts = model3.assign_shifts_to_employees_monthly(monthly_schedule, employees, YEAR, MONTH, last_month_schedule, max_hours=hour_per_month[MONTH])

    # Save final schedule
    schedule_filename = os.path.join(SCHEDULE_FOLDER, f"final_schedule_{YEAR}_{MONTH}.json")
    with open(schedule_filename, "w") as f:
        json.dump(assigned_shifts, f, indent=4)

    print(f"✅ Final employee schedule saved to {schedule_filename}")

    # Step 4: Transform schedule format for visualization
    assigned_shifts_by_date = model3.transform_schedule_format(assigned_shifts, YEAR, MONTH)

    schedule_by_date_filename = os.path.join(SCHEDULE_FOLDER, f"final_schedule_{YEAR}_{MONTH}_by_date.json")
    with open(schedule_by_date_filename, "w") as f:
        json.dump(assigned_shifts_by_date, f, indent=4)

    # Step 5: Visualize the final schedule
    print(f"📊 Opening schedule visualization...")
    visualize_schedule(assigned_shifts_by_date)

    df = analyze_monthly_hours_from_employees(employees = employees, schedule_json_path = schedule_filename, monthly_expected_fulltime = hour_per_month[MONTH])
    print(df)

    staffing_summary = analyze_total_staffing_balance(employees, schedule_json_path = schedule_filename, monthly_expected_fulltime = hour_per_month[MONTH])
    print(f"Total Scheduled Hours: {staffing_summary['total_scheduled_hours']} hours")
    print(f"Total Expected Hours: {staffing_summary['total_expected_hours']} hours")
    print(f"Difference: {staffing_summary['difference']} hours")
    print(f"Staffing Status: {staffing_summary['status']}")

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

if __name__ == "__main__":
    main()