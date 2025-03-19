from Model_1 import model1
from Model_2 import model2
from Model_3 import model3
from visualize import *
from Model_3.employees import *

sales_capacity = 12
customer_flow_per_hour = [23, 8, 8, 4, 8, 8, 35, 40, 38, 32, 25, 13, 15, 10]


#get data from kjell
def get_data():
    return 0


#Recieves demand for the store from model1
def get demand():

    return model1.main(customer_flow_per_hour, sales_capacity)


def main():
    """Main function to create an optimized employee schedule."""
    
    store_id = "1"
    day = "2025-03-18"
    opening_hours = ["08:00", "22:00"]
    min_shift_hours = 3
    max_hours_without_lunch = 5
    max_hours_per_day = 8
    staffing_per_hour = model1.calculate_staffing(customer_flow_per_hour, sales_capacity)
    
    print(model1.calculate_staffing(customer_flow_per_hour, sales_capacity))
    print("📊 Generating shift suggestions...")
    shifts = model2.construct_shifts(
        opening_hours=opening_hours,
        required_staffing = staffing_per_hour,
        min_hours_per_day=min_shift_hours,
        max_hours_before_lunch=max_hours_without_lunch,
        max_hours_per_day=max_hours_per_day
    )

    print("✅ Shift suggestions generated.")

    print("📊 Visualizing shift creation from Model 2...")
    model2.visualize_schedule(shifts, staffing_per_hour)

    print("👥 Loading employee data...")
    employees = load_employees()
    print(f"✅ Loaded {len(employees)} employees.")

    print("📅 Assigning shifts to employees...")
    assigned_shifts = model3.assign_shifts_to_employees(shifts, employees, day)
    print("✅ Shift assignment completed.")

    print("📊 Visualizing the final schedule...")
    visualize_assigned_shifts(assigned_shifts, day)

    return assigned_shifts

if __name__ == "__main__":
    final_schedule = main()
    print("📅 Final Schedule:")
    for employee, shifts in final_schedule.items():
        print(f"{employee}: {shifts}")