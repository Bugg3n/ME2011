from Model_1 import model1
from Model_2 import model2
from Model_3 import model3
import calendar
import json
from visualize import main as visualize_main
from visualize import *
from Model_3.employees import *

YEAR = 2025
MONTH = 3
STORE_ID = "1"
SALES_CAPACITY = 12  # Customers per employee per hour


#TODO
# Färdigställa modell 3 
    # 1 skala 1-10 istället för 2
    # Input för hur gärna du vill jobba helg
    # Vikta den som blir tilldelad pass baserat på svaren jämfört med varandra (probalistiskt)
    # Vecko-visualisering
    # Implementera chefs-roll som buffert
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


sales_capacity = 12
customer_flow_per_hour = [23, 8, 8, 4, 8, 8, 35, 40, 38, 32, 25, 13, 15, 10]
# Här ska alla parametrar finnas


#get data from kjell
def get_data():
    return 0


#Recieves demand for the store from model1
def get_demand():
    demand = model1.main(customer_flow_per_hour, sales_capacity)
    return 0


def main():
    """Main function to create an optimized monthly employee schedule."""

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

    # Step 3: Save monthly schedule to JSON
    schedule_filename = f"schedule_{YEAR}_{MONTH}.json"
    with open(schedule_filename, "w") as f:
        json.dump(monthly_schedule, f, indent=4)

    print(f"✅ Monthly schedule saved to {schedule_filename}")

    # Step 4: Visualize the schedule for a specific day (optional)
    visualize_day = f"{YEAR}-{MONTH:02d}-15"  # Example: visualize March 15
    if visualize_day in monthly_schedule:
        print(f"📊 Visualizing schedule for {visualize_day}...")
        model2.visualize_schedule(monthly_schedule[visualize_day]["shifts"], monthly_staffing[visualize_day], visualize_day)

    # return assigned_shifts

    print("👥 Loading employee data...")
    employees = load_employees()
    print(f"✅ Loaded {len(employees)} employees.")

    print("📅 Assigning shifts to employees...")
    assigned_shifts = model3.assign_shifts_to_employees(shifts, employees, day)
    print("✅ Shift assignment completed.")

    print("📊 Visualizing the final schedule...")
    visualize_assigned_shifts(assigned_shifts, day)


if __name__ == "__main__":
    final_schedule = main()
    print("📅 Final Schedule:")
    for employee, shifts in final_schedule.items():
       print(f"{employee}: {shifts}")



    #this function opens up a window displaying some interactive information about the schedule that has been created
    visualize_main(year_month= "2025 - January",store = "SE01", monthly_schedule = None,staff_needed=None)