from Model_1 import model1
from Model_2 import model2
from Model_3 import model3
import calendar
import json
from visualize import main as visualize_model_3
from visualize2 import generate_html as visualize_schedule
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

    print(f"👥 Loading employees...")
    employees = load_employees()

    print(f"📅 Assigning shifts to employees for {calendar.month_name[MONTH]} {YEAR}...")

    # Step 3: Assign shifts to employees (Model 3)
    assigned_shifts = model3.assign_shifts_to_employees_monthly(monthly_schedule, employees, YEAR, MONTH)

    # Save final schedule
    schedule_filename = f"final_schedule_{YEAR}_{MONTH}.json"
    with open(schedule_filename, "w") as f:
        json.dump(assigned_shifts, f, indent=4)

    print(f"✅ Final employee schedule saved to {schedule_filename}")

    # Step 4: Transform schedule format for visualization
    assigned_shifts_by_date = model3.transform_schedule_format(assigned_shifts, YEAR, MONTH)

    schedule_filename = f"final_schedule_{YEAR}_{MONTH}_by_date.json"
    with open(schedule_filename, "w") as f:
        json.dump(assigned_shifts_by_date, f, indent=4)

    # Step 5: Visualize the final schedule
    print(f"📊 Opening schedule visualization...")
    visualize_schedule(assigned_shifts_by_date)

if __name__ == "__main__":
    main()