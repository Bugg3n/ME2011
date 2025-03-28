This document describes the first model (model1), 




Function: calculate_cashier_requirements
This function calculates the required number of cashiers for each hour based on queueing theory (M/M/c model).

Input Parameters:
customer_arrival_rates (list):

A list containing the expected number of customers arriving each hour.
Example: [5, 10, 15, 25, 40] means 5 customers in hour 1, 10 in hour 2, etc.
Units: Customers per hour
avg_service_time_minutes (float, default=3.0):

The average time it takes a cashier to serve one customer.
Lower values mean faster service and potentially fewer cashiers needed.
Units: Minutes
target_wait_time_minutes (float, default=5.0):

The maximum acceptable waiting time for customers in the queue.
Sets a service quality standard - how long customers should wait at most.
Units: Minutes
target_utilization (float, default=0.8):

The target workload for each cashier (between 0 and 1).
Value of 0.8 means cashiers should be busy 80% of their time.
Higher values increase efficiency but risk burnout and reduced service quality.
Units: Decimal percentage (0.0 to 1.0)
confidence_level (float, default=0.95):

Statistical confidence level for handling variability in customer arrivals.
Higher values (e.g., 0.99) add more buffer cashiers to handle unexpected surges.
Lower values (e.g., 0.90) optimize for efficiency but accept higher risk.
Units: Decimal percentage (0.0 to 1.0)
Output Dictionary:
cashiers_required (list):

Number of cashiers needed for each hour to meet all requirements.
Units: Count of cashiers (integer)
utilization (list):

Expected utilization rate of cashiers for each hour.
Values closer to 1.0 indicate cashiers are very busy.
Units: Decimal percentage (0.0 to 1.0)
wait_times (list):

Expected average waiting time for customers in each hour.
Units: Minutes
service_level (list):

Probability that customers wait less than the target wait time.
Higher values indicate better customer service.
Units: Decimal percentage (0.0 to 1.0)
Function: calculate_expected_wait_time
Calculates the expected waiting time for customers using the M/M/c queueing model.

Input Parameters:
arrival_rate (float):

Rate at which customers arrive.
Units: Customers per hour
service_rate (float):

Rate at which each cashier can serve customers.
Units: Customers per hour
num_cashiers (int):

Number of cashiers available to serve customers.
Units: Count (integer)
Output:
Expected waiting time (float):
Average time customers spend waiting in queue before being served.
Returns infinity if the system is unstable (arrival rate exceeds service capacity).
Units: Hours
Function: calculate_service_level
Calculates the probability that customers wait less than the target time.

Input Parameters:
arrival_rate (float):

Rate at which customers arrive.
Units: Customers per hour
service_rate (float):

Rate at which each cashier can serve customers.
Units: Customers per hour
num_cashiers (int):

Number of cashiers available.
Units: Count (integer)
target_time (float):

Target maximum waiting time.
Units: Hours
Output:
Service level (float):
Probability that a customer waits less than the target time.
Value between 0.0 (poor service) and 1.0 (excellent service).
Units: Decimal percentage (0.0 to 1.0)



Function: optimize_cashier_schedule
Finds the minimum number of cashiers needed for each hour to meet service level targets while minimizing cost.

Input Parameters:
customer_arrival_rates (list):

Expected number of customers arriving each hour.
Units: Customers per hour
avg_service_time_minutes (float, default=3.0):

Average time to serve one customer.
Units: Minutes
cost_per_cashier_hour (float, default=150):

Hourly cost of employing one cashier.
Units: Currency (e.g., SEK, USD)
target_service_level (float, default=0.90):

Minimum acceptable service level (probability that wait time < 5 min).
Units: Decimal percentage (0.0 to 1.0)
min_cashiers (int, default=1):

Minimum number of cashiers that must be scheduled per hour.
Used for safety or policy requirements.
Units: Count (integer)
max_cashiers (int, default=10):

Maximum number of available cashiers.
Resource constraint or physical limitation.
Units: Count (integer)
Output Dictionary:
cashiers (list):

Optimized number of cashiers for each hour.
Units: Count (integer)
service_level (list):

Expected service level for each hour with the optimized staffing.
Units: Decimal percentage (0.0 to 1.0)
utilization (list):

Expected utilization rate of cashiers for each hour.
Units: Decimal percentage (0.0 to 1.0)
wait_times_minutes (list):

Expected average waiting time for customers in each hour.
Units: Minutes
total_cost (float):

Total cost of the optimized cashier schedule.
Units: Currency (same as cost_per_cashier_hour)
These functions work together to create a staffing solution that balances operational efficiency, service quality, and cost.







TEMPORARY VISUALIZATION FUNCTION 

# main.py
import os
import json
from datetime import datetime
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading

# Your queueing theory calculation (in Python)
def calculate_schedule(params):
    """Replace this with your actual queueing theory logic"""
    print("Calculating schedule with:", params)
    
    # Example modified schedule based on inputs
    return {
        "2025-03-01": {
            "Alice": [{"start": "8:00", "end": str(8+params['shift_duration'])+":00", "lunch": "12:00"}],
            "Bob": [{"start": "12:00", "end": str(12+params['shift_duration'])+":00", "lunch": "15:00"}]
        }
    }

def generate_html(schedule_data):
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Schedule Optimizer</title>
    <style>
        /* Your existing CSS styles */
        body {{ font-family: Arial, sans-serif; }}
        .control-panel {{ 
            background: #f5f5f5; 
            padding: 20px; 
            margin: 20px 0; 
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <h1>Schedule Optimizer</h1>
    
    <!-- Initial Schedule -->
    <div id="scheduleContainer">
        {json.dumps(schedule_data)}  <!-- Embedded initial data -->
    </div>
    
    <!-- Control Panel -->
    <div class="control-panel">
        <h2>Adjust Parameters</h2>
        <input type="number" id="serviceRate" placeholder="Service Rate" value="10">
        <button onclick="fetchNewSchedule()">Recalculate</button>
    </div>

    <script>
        // Render initial schedule
        const initialData = JSON.parse(document.getElementById('scheduleContainer').textContent);
        renderSchedule(initialData);
        
        // Fetch updated schedule
        async function fetchNewSchedule() {{
            const params = {{
                service_rate: document.getElementById('serviceRate').value,
                // Add other parameters
            }};
            
            try {{
                const response = await fetch('/calculate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(params)
                }});
                const newSchedule = await response.json();
                renderSchedule(newSchedule);
            }} catch (error) {{
                console.error('Error:', error);
            }}
        }}
        
        function renderSchedule(data) {{
            // Your existing rendering logic
            console.log("Rendering:", data);
        }}
    </script>
</body>
</html>
    """
    
    with open("schedule.html", "w") as f:
        f.write(html)
    return html

# HTTP Server for handling calculations
class CalculationHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/calculate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data)
            
            # Call your Python calculation function
            new_schedule = calculate_schedule(params)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(new_schedule).encode())

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CalculationHandler)
    print("Server running on port 8000")
    httpd.serve_forever()

def main():
    # Generate initial schedule
    initial_params = {
        'service_rate': 10,
        'shift_duration': 8
    }
    initial_schedule = calculate_schedule(initial_params)
    
    # Start web server in background thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Generate and open HTML interface
    generate_html(initial_schedule)
    webbrowser.open("http://localhost:8000/schedule.html")

if __name__ == "__main__":
    main()