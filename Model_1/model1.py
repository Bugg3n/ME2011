import calendar
import numpy as np
import math
from scipy import stats

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



#####################################################################
# Cashier Requirement Calculator using Queueing Theory
#####################################################################



def calculate_cashier_requirements(
    customer_arrival_rates, 
    avg_service_time_minutes=3.0,
    target_wait_time_minutes=5.0,
    target_utilization=0.8,
    confidence_level=0.95
):
    """
    Calculate the required number of cashiers per hour based on queueing theory (M/M/c model).
    
    Parameters:
    -----------
    customer_arrival_rates : list
        Expected number of customer arrivals per hour
    avg_service_time_minutes : float
        Average time to serve a customer in minutes
    target_wait_time_minutes : float
        Target maximum customer waiting time in minutes
    target_utilization : float
        Target cashier utilization (between 0 and 1)
    confidence_level : float
        Statistical confidence level for handling demand variability
    
    Returns:
    --------
    dict : Contains the following keys:
        'cashiers_required': List of required cashiers per hour
        'utilization': List of expected utilization per hour
        'wait_times': List of expected wait times per hour
        'service_level': List of expected service levels per hour
    """
    results = {
        'cashiers_required': [],
        'utilization': [],
        'wait_times': [],
        'service_level': []
    }
    
    # Convert minutes to hours for calculation consistency
    avg_service_time_hours = avg_service_time_minutes / 60.0
    target_wait_time_hours = target_wait_time_minutes / 60.0
    
    # Calculate service rate per cashier per hour
    service_rate_per_cashier = 1.0 / avg_service_time_hours
    
    # Z-score for adding buffer based on confidence level
    z_score = stats.norm.ppf(confidence_level)
    
    for hour, arrival_rate in enumerate(customer_arrival_rates):
        # Add buffer to arrival rate based on confidence level
        # Assuming Poisson distribution, variance equals the mean
        adjusted_arrival_rate = arrival_rate + z_score * math.sqrt(arrival_rate)
        
        # Calculate traffic intensity (ρ = λ/μ)
        traffic_intensity = adjusted_arrival_rate / service_rate_per_cashier
        
        # Calculate minimum number of cashiers needed for stability (ρ/c < 1)
        min_cashiers_for_stability = math.ceil(traffic_intensity)
        
        # Calculate minimum number of cashiers needed to meet target utilization
        min_cashiers_for_utilization = math.ceil(traffic_intensity / target_utilization)
        
        # Calculate minimum cashiers needed for target wait time using Erlang C formula
        c = min_cashiers_for_stability
        wait_time = calculate_expected_wait_time(adjusted_arrival_rate, service_rate_per_cashier, c)
        
        while wait_time > target_wait_time_hours and c <= 20:  # Cap at 20 cashiers
            c += 1
            wait_time = calculate_expected_wait_time(adjusted_arrival_rate, service_rate_per_cashier, c)
        
        # Take the maximum of all constraints
        required_cashiers = max(min_cashiers_for_stability, min_cashiers_for_utilization, c)
        
        # Calculate final metrics with the chosen number of cashiers
        utilization = adjusted_arrival_rate / (required_cashiers * service_rate_per_cashier)
        final_wait_time = calculate_expected_wait_time(adjusted_arrival_rate, service_rate_per_cashier, required_cashiers)
        service_level = calculate_service_level(adjusted_arrival_rate, service_rate_per_cashier, required_cashiers, target_wait_time_hours)
        
        # Store results
        results['cashiers_required'].append(required_cashiers)
        results['utilization'].append(utilization)
        results['wait_times'].append(final_wait_time * 60)  # Convert back to minutes
        results['service_level'].append(service_level)
        
    return results

def calculate_expected_wait_time(arrival_rate, service_rate, num_cashiers):
    """
    Calculate expected waiting time in queue using M/M/c queueing model.
    
    Parameters:
    -----------
    arrival_rate : float
        Customer arrival rate (customers per hour)
    service_rate : float
        Service rate per cashier (customers per hour)
    num_cashiers : int
        Number of cashiers
        
    Returns:
    --------
    float : Expected waiting time in hours
    """
    if arrival_rate >= num_cashiers * service_rate:
        return float('inf')  # System is unstable
    
    rho = arrival_rate / (num_cashiers * service_rate)  # Server utilization
    
    # Calculate P0 (probability of empty system)
    sum_term = 0
    for n in range(num_cashiers):
        sum_term += (arrival_rate / service_rate) ** n / math.factorial(n)
    
    p0_denominator = sum_term + (arrival_rate / service_rate) ** num_cashiers / \
        (math.factorial(num_cashiers) * (1 - rho))
    
    p0 = 1 / p0_denominator
    
    # Calculate probability of queueing (Erlang C formula)
    erlang_c = (arrival_rate / service_rate) ** num_cashiers / \
        (math.factorial(num_cashiers) * (1 - rho)) * p0
    
    # Calculate average wait time in queue
    wq = erlang_c / (num_cashiers * service_rate - arrival_rate)
    
    return wq

def calculate_service_level(arrival_rate, service_rate, num_cashiers, target_time):
    """
    Calculate the service level - probability that a customer waits less than the target time.
    
    Parameters:
    -----------
    arrival_rate : float
        Customer arrival rate (customers per hour)
    service_rate : float
        Service rate per cashier (customers per hour)
    num_cashiers : int
        Number of cashiers
    target_time : float
        Target waiting time in hours
        
    Returns:
    --------
    float : Service level (between 0 and 1)
    """
    if arrival_rate >= num_cashiers * service_rate:
        return 0.0  # System is unstable
    
    rho = arrival_rate / (num_cashiers * service_rate)
    
    # Calculate P0 (probability of empty system) - same as in calculate_expected_wait_time
    sum_term = 0
    for n in range(num_cashiers):
        sum_term += (arrival_rate / service_rate) ** n / math.factorial(n)
    
    p0_denominator = sum_term + (arrival_rate / service_rate) ** num_cashiers / \
        (math.factorial(num_cashiers) * (1 - rho))
    
    p0 = 1 / p0_denominator
    
    # Calculate probability of queueing (Erlang C formula)
    erlang_c = (arrival_rate / service_rate) ** num_cashiers / \
        (math.factorial(num_cashiers) * (1 - rho)) * p0
    
    # Calculate probability of waiting less than target time
    service_level = 1 - erlang_c * math.exp(-(num_cashiers * service_rate - arrival_rate) * target_time)
    
    return max(0, min(1, service_level))  # Ensure value is between 0 and 1

def optimize_cashier_schedule(
    customer_arrival_rates,
    avg_service_time_minutes=3.0,
    cost_per_cashier_hour=150,
    target_service_level=0.90,
    min_cashiers=1,
    max_cashiers=10
):
    """
    Optimize cashier staffing to minimize cost while meeting target service level.
    
    Parameters:
    -----------
    customer_arrival_rates : list
        Expected number of customer arrivals per hour
    avg_service_time_minutes : float
        Average time to serve a customer in minutes
    cost_per_cashier_hour : float
        Hourly cost of a cashier
    target_service_level : float
        Target service level (probability customer waits less than 5 minutes)
    min_cashiers : int
        Minimum number of cashiers required at any time
    max_cashiers : int
        Maximum number of cashiers available
        
    Returns:
    --------
    dict : Contains optimized cashier schedule and metrics
    """
    avg_service_time_hours = avg_service_time_minutes / 60.0
    service_rate_per_cashier = 1.0 / avg_service_time_hours
    target_wait_time_hours = 5.0 / 60.0  # 5 minutes in hours
    
    optimized_schedule = {
        'cashiers': [],
        'service_level': [],
        'utilization': [],
        'wait_times_minutes': []
    }
    
    total_cost = 0
    
    for hour, arrival_rate in enumerate(customer_arrival_rates):
        best_cashiers = max_cashiers
        best_cost = float('inf')
        
        # Find minimum number of cashiers that meet the service level target
        for num_cashiers in range(min_cashiers, max_cashiers + 1):
            service_level = calculate_service_level(
                arrival_rate, service_rate_per_cashier, num_cashiers, target_wait_time_hours
            )
            
            if service_level >= target_service_level:
                hour_cost = num_cashiers * cost_per_cashier_hour
                if hour_cost < best_cost:
                    best_cost = hour_cost
                    best_cashiers = num_cashiers
        
        # Calculate metrics with the chosen number of cashiers
        utilization = arrival_rate / (best_cashiers * service_rate_per_cashier) if best_cashiers > 0 else 1.0
        wait_time = calculate_expected_wait_time(arrival_rate, service_rate_per_cashier, best_cashiers)
        service_level = calculate_service_level(
            arrival_rate, service_rate_per_cashier, best_cashiers, target_wait_time_hours
        )
        
        # Store results
        optimized_schedule['cashiers'].append(best_cashiers)
        optimized_schedule['service_level'].append(service_level)
        optimized_schedule['utilization'].append(utilization)
        optimized_schedule['wait_times_minutes'].append(wait_time * 60)
        
        total_cost += best_cost
    
    optimized_schedule['total_cost'] = total_cost
    
    return optimized_schedule

def demonstrate_queueing_model():
    """
    Demonstrate the queueing model with sample data.
    """
    # Sample hourly customer arrival rates for a store
    customer_arrivals = [5, 10, 15, 25, 40, 50, 55, 60, 65, 60, 50, 40, 30, 20, 10]
    
    print("Queueing Theory Cashier Requirement Demo")
    print("----------------------------------------")
    
    # Basic requirements with default parameters
    print("\n1. Basic Cashier Requirements:")
    basic_requirements = calculate_cashier_requirements(customer_arrivals)
    
    print(f"Hour\tArrivals\tCashiers\tUtilization\tWait Time (min)\tService Level")
    for hour, arrivals in enumerate(customer_arrivals):
        cashiers = basic_requirements['cashiers_required'][hour]
        utilization = basic_requirements['utilization'][hour]
        wait_time = basic_requirements['wait_times'][hour]
        service_level = basic_requirements['service_level'][hour]
        
        print(f"{hour+8}:00\t{arrivals}\t\t{cashiers}\t\t{utilization:.2f}\t\t{wait_time:.2f}\t\t{service_level:.2f}")
    
    # Optimized schedule to minimize cost
    print("\n2. Cost-Optimized Cashier Schedule:")
    optimized_schedule = optimize_cashier_schedule(customer_arrivals)
    
    print(f"Hour\tArrivals\tCashiers\tUtilization\tWait Time (min)\tService Level")
    for hour, arrivals in enumerate(customer_arrivals):
        cashiers = optimized_schedule['cashiers'][hour]
        utilization = optimized_schedule['utilization'][hour]
        wait_time = optimized_schedule['wait_times_minutes'][hour]
        service_level = optimized_schedule['service_level'][hour]
        
        print(f"{hour+8}:00\t{arrivals}\t\t{cashiers}\t\t{utilization:.2f}\t\t{wait_time:.2f}\t\t{service_level:.2f}")
    
    print(f"\nTotal Cost: ${optimized_schedule['total_cost']:.2f}")

# If the module is run directly, demonstrate the queueing model
if __name__ == "__main__":
    demonstrate_queueing_model()