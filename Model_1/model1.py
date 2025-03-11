

#Using queueing theory to model the number of customers in a store over time and returning the demanded number of employees per hour
#hyperparameters
sales_capacity = 12

customer_flow_per_hour = [5, 8, 12, 20, 25, 30, 35, 40, 38, 32, 25, 20, 15, 10]


# Function to calculate staffing per hour
def calculate_staffing(customer_flow, sales_capacity):
    return [round(customers / sales_capacity) for customers in customer_flow]



def main(store_id, day):

    staffing = calculate_staffing(customer_flow_per_hour, sales_capacity)
  
    return staffing



if __name__ == "__main__":
    main(store_id="1", day="2025-01-22")

