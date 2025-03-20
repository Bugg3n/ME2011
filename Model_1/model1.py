import calendar
import numpy as np

def estimate_customer_flow(day_of_week): # This i going to change when we get the data. 
    """
    Simulates customer flow variations per day.
    Example: Higher customer flow on weekends (Friday, Saturday).
    """
    base_flow = [10, 15, 20, 25, 30, 35, 40, 38, 32, 25, 20, 15, 10, 5]
    
    # Adjust for weekdays (0=Monday, 6=Sunday)
    if day_of_week in [4, 5]:  # Friday, Saturday = busiest
        return [int(x * 1.3) for x in base_flow]
    elif day_of_week in [0, 6]:  # Monday, Sunday = slower
        return [int(x * 0.8) for x in base_flow]
    else:
        return base_flow  # Normal weekday flow


def calculate_staffing(customer_flow_per_hour, sales_capacity):
    """
    Determines how many employees are required per hour based on customer demand.
    """
    staffing_per_hour = [max(1, int(np.ceil(flow / sales_capacity))) for flow in customer_flow_per_hour]
    return staffing_per_hour


def generate_monthly_staffing(year, month, store_id, sales_capacity=12):
    """
    Generates the required staffing per hour for each day in a given month.
    """
    num_days = calendar.monthrange(year, month)[1]
    monthly_staffing = {}

    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        day_of_week = calendar.weekday(year, month, day)

        # Simulate customer flow based on the day of the week
        customer_flow_per_hour = estimate_customer_flow(day_of_week)

        # Calculate staffing needs
        staffing_per_hour = calculate_staffing(customer_flow_per_hour, sales_capacity)

        # Store the result
        monthly_staffing[date_str] = staffing_per_hour

    return monthly_staffing


if __name__ == "__main__":
    # Example: Generate staffing requirements for March 2025
    year, month = 2025, 3
    store_id = "1"

    staffing_requirements = generate_monthly_staffing(year, month, store_id)

    # Display output
    for date, staffing in staffing_requirements.items():
        print(f"{date}: {staffing}")
