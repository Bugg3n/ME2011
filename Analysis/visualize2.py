import os
import json
from datetime import datetime, timedelta
import webbrowser

def calculate_worked_hours(shifts):
    total_seconds = 0
    for shift in shifts:
        start_time = datetime.strptime(shift["start"], "%H:%M")
        end_time = datetime.strptime(shift["end"], "%H:%M")
        shift_duration = (end_time - start_time).total_seconds()
        
        if shift["lunch"] != "None":
            shift_duration -= 3600  # Subtract 1 hour for lunch
        
        total_seconds += max(0, shift_duration)
    
    return round(total_seconds / 3600, 2)

def generate_html(schedule_data, unassigned_shifts=None):
    print("in generate html")
    if unassigned_shifts is None:
        unassigned_shifts = []
    
    # Generate just the schedule visualization content (without controls)
    schedule_content = generate_schedule_content(schedule_data, unassigned_shifts) # Dynamic content
    print("schedule generated")
    
    # In web mode, return ONLY the dynamic content
    if os.environ.get('WEB_MODE') == "1":
        print("In webmode. Returning")
        return schedule_content
    
    # For standalone mode, return full HTML page. Static content
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Work Schedule Viewer</title>
    <style>
    body {{
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        background: #f7f7f7;
        color: #333;
    }}

    .control-panel {{
        background: #ffffff;
        padding: 1rem 2rem;
        border-bottom: 1px solid #ccc;
        margin-bottom: 1rem;
    }}

    .param-group {{
        margin-bottom: 1rem;
    }}

    .param-group label {{
        display: block;
        margin-bottom: 0.3rem;
        font-weight: 500;
    }}

    input[type="number"] {{
        width: 100%;
        padding: 0.4rem;
        font-size: 1rem;
        border: 1px solid #ccc;
        border-radius: 6px;
    }}

    button {{
        background: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
    }}

    button:hover {{
        background: #0056b3;
    }}

    .calendar {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 1rem;
    }}

    .calendar .day {{
        width: 40px;
        height: 40px;
        background: white;
        border: 1px solid #ccc;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background 0.2s ease;
    }}

    .calendar .day:hover {{
        background: #e0e0e0;
    }}

    .schedule {{
        display: none;
        padding: 1rem;
        background: white;
        margin: 1rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}

    .timeline-container {{
        margin-top: 1rem;
        border-left: 1px solid #ccc;
        padding-left: 1rem;
    }}

    .employee-row {{
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }}

    .employee-name {{
        width: 120px;
        font-weight: 600;
    }}

    .timeline {{
        position: relative;
        flex: 1;
        height: 20px;
        background: #f0f0f0;
        border-radius: 4px;
        overflow: hidden;
    }}

    .shift {{
        position: absolute;
        height: 100%;
        background: #007bff;
        border-radius: 4px;
    }}

    .lunch {{
        position: absolute;
        height: 100%;
        background: #cccccc;
        opacity: 0.8;
    }}

    .shift-tooltip {{
        position: absolute;
        top: -20px;
        left: 0;
        font-size: 0.75rem;
        color: #333;
    }}

    .hour-marker {{
        position: absolute;
        height: 10px;
        width: 1px;
        background: #999;
        bottom: -5px;
    }}

    .hour-label {{
        position: absolute;
        bottom: -20px;
        font-size: 0.75rem;
        transform: translateX(-50%);
    }}

    .shift-details {{
        margin-top: 1rem;
    }}

    .shift-entry {{
        margin-bottom: 0.8rem;
    }}

    .stats-card {{
        margin-top: 1rem;
        background: #f2f2f2;
        padding: 0.8rem;
        border-radius: 8px;
    }}

    .stats-value {{
        font-size: 1.2rem;
        font-weight: bold;
    }}

    .stats-label {{
        font-size: 0.9rem;
        color: #666;
    }}
</style>


</head>
<body>
    <div id="staticContent">
        <h1>Work Schedule Optimizer • March 2025</h1>
        
        <!-- Control Panel (static - won't be updated) -->
        <div class="control-panel">
            <h2>Queueing Parameters</h2>
            <div class="param-group">
                <label for="salesCapacity">Sales Capacity (customers/hour):</label>
                <input type="number" id="salesCapacity" value="12" min="1" step="1">
            </div>
            <div class="param-group">
                <label for="serviceTime">Avg. Service Time (minutes):</label>
                <input type="number" id="serviceTime" value="3.0" min="0.5" step="0.1">
            </div>
            <div class="param-group">
                <label for="targetWait">Target Wait Time (minutes):</label>
                <input type="number" id="targetWait" value="5.0" min="1" step="0.5">
            </div>
            <div class="param-group">
                <button id="updateButton" onclick="updateSchedule()">Update Schedule</button>
                <span class="loading" id="loadingIndicator">Calculating...</span>
            </div>
        </div>
    </div>
    
    <!-- Dynamic Schedule Content (will be updated) -->
    <div id="dynamicScheduleContent">
        {schedule_content}
    </div>

    <script>
        let isUpdating = false;
        
        async function updateSchedule() {{
            if (isUpdating) return;
            isUpdating = true;
            
            const button = document.getElementById('updateButton');
            button.disabled = true;
            const loading = document.getElementById('loadingIndicator');
            loading.style.display = 'inline';
            
            // Save current input values
            const currentValues = {{
                salesCapacity: document.getElementById('salesCapacity').value,
                serviceTime: document.getElementById('serviceTime').value,
                targetWait: document.getElementById('targetWait').value
            }};
            
            const params = {{
                sales_capacity: currentValues.salesCapacity,
                average_service_time: currentValues.serviceTime,
                target_wait_time: currentValues.targetWait
            }};
            
            // Validate inputs
            if (!params.sales_capacity || !params.average_service_time || !params.target_wait_time) {{
                alert('Please fill all parameters');
                isUpdating = false;
                button.disabled = false;
                loading.style.display = 'none';
                return;
            }}
            
            try {{
                const response = await fetch('/calculate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(params)
                }});
                
                if (!response.ok) {{
                    throw new Error(await response.text());
                }}
                
                const result = await response.json();
                
                // Only update the dynamic content portion
                if (result && result.content) {{
                    document.getElementById('dynamicScheduleContent').innerHTML = result.content;
                    
                    // Restore input values
                    document.getElementById('salesCapacity').value = currentValues.salesCapacity;
                    document.getElementById('serviceTime').value = currentValues.serviceTime;
                    document.getElementById('targetWait').value = currentValues.targetWait;
                }} else {{
                    throw new Error('Invalid response format from server');
                }}
                
            }} catch (error) {{
                console.error('Error:', error);
                alert('Error updating schedule: ' + error.message);
            }} finally {{
                isUpdating = false;
                button.disabled = false;
                loading.style.display = 'none';
            }}
        }}
        
        function toggleSchedule(id) {{
            document.querySelectorAll('.schedule').forEach(el => {{
                el.style.display = 'none';
            }});
            const schedule = document.getElementById(id);
            if (schedule) {{
                schedule.style.display = 'block';
                window.scrollTo({{
                    top: schedule.offsetTop - 20,
                    behavior: 'smooth'
                }});
            }}
        }}
        
        // Show first schedule by default
        document.addEventListener('DOMContentLoaded', function() {{
            const firstSchedule = document.querySelector('.schedule');
            if (firstSchedule) {{
                firstSchedule.style.display = 'block';
            }}
        }});
    </script>
</body>
</html>"""
    
    file_path = "monthly_schedule.html"
    print("Creating file monthly schedule")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html)
    
    # Only open in browser if not in web mode
    print("In webmode")
    return html

def generate_schedule_content(schedule_data, unassigned_shifts=None):
    """Generates just the schedule visualization content (without full HTML document structure)"""
    if unassigned_shifts is None:
        unassigned_shifts = []
    
    content = ""
    
    if unassigned_shifts:
        content += """
        <div class="unassigned-shifts">
            <h3>⚠️ Unassigned Shifts</h3>
            <ul>"""
        for shift in unassigned_shifts:
            content += f"<li>{shift['date']}: {shift['start']} - {shift['end']}</li>"
        content += """
            </ul>
        </div>"""
    
    # Add the calendar days
    content += '<div class="calendar">'
    for date in schedule_data.keys():
        day = datetime.strptime(date, "%Y-%m-%d").day
        content += f'<div class="day" onclick="toggleSchedule(\'schedule-{day}\')">{day}</div>'
    content += '</div>'
    
    # Add the schedule visualizations
    content += '<main id="schedules">'
    for date, shifts in schedule_data.items():
        day = datetime.strptime(date, "%Y-%m-%d").day
        total_worked_hours = 0
        
        content += f'<div id="schedule-{day}" class="schedule">'
        content += f'<h2>{date}</h2>'
        
        # Define time range constants (8:00 AM to 10:00 PM)
        min_hour = 8
        max_hour = 22
        total_hours = max_hour - min_hour
        minutes_per_hour = 60
        total_minutes = total_hours * minutes_per_hour
        
        # Timeline visualization
        content += '<div class="timeline-container">'
        
        for employee, shift_list in shifts.items():
            employee_hours = calculate_worked_hours(shift_list)
            total_worked_hours += employee_hours
            
            content += f'<div class="employee-row">'
            content += f'<div class="employee-name">{employee}</div>'
            content += '<div class="timeline">'
            
            for shift in shift_list:
                # Parse shift times
                start_time = datetime.strptime(shift["start"], "%H:%M")
                end_time = datetime.strptime(shift["end"], "%H:%M")
                
                # Calculate positions
                start_min = (start_time.hour - min_hour) * 60 + start_time.minute
                end_min = (end_time.hour - min_hour) * 60 + end_time.minute
                start_percent = max(0, min(100, (start_min / total_minutes) * 100))
                end_percent = max(0, min(100, (end_min / total_minutes) * 100))
                width_percent = max(0, min(100 - start_percent, end_percent - start_percent))
                
                # Shift block
                content += f'<div class="shift" style="left:{start_percent}%; width:{width_percent}%">'
                content += f'<div class="shift-tooltip">{shift["start"]} - {shift["end"]}</div>'
                content += '</div>'
                
                # Lunch break
                if shift["lunch"] != "None":
                    lunch_hour = int(shift["lunch"].split(":")[0])
                    lunch_start_percent = max(0, min(100, ((lunch_hour - min_hour) * 60 / total_minutes) * 100))
                    lunch_width_percent = max(0, min(100 - lunch_start_percent, (60 / total_minutes) * 100))
                    
                    content += f'<div class="lunch" style="left:{lunch_start_percent}%; width:{lunch_width_percent}%"></div>'
            
            content += '</div></div>'
        
        content += '</div>'  # Close timeline-container
        
        # Time axis
        content += '<div class="time-axis">'
        for hour in range(min_hour, max_hour + 1):
            for minute in [0, 30]:
                if hour == max_hour and minute == 30:
                    continue
                time_percent = (((hour - min_hour) * 60 + minute) / total_minutes) * 100
                content += f'<div class="hour-marker" style="left:{time_percent}%"></div>'
                if minute == 0:
                    content += f'<div class="hour-label" style="left:{time_percent}%">{hour}:00</div>'
        content += '</div>'
        
        # Shift details
        content += '<div class="shift-details">'
        content += '<h3>Shift Details</h3>'
        for employee, shift_list in shifts.items():
            content += f'<div class="shift-entry"><strong>{employee}</strong><br>'
            for shift in shift_list:
                content += f'{shift["start"]} - {shift["end"]}'
                if shift["lunch"] != "None":
                    content += f' (Lunch at {shift["lunch"]})'
                content += '<br>'
            content += '</div>'
        content += '</div>'
        
        # Total hours card
        content += f"""
        <div class="stats-card">
            <div class="stats-value">{total_worked_hours} hours</div>
            <div class="stats-label">Total worked hours (excluding lunch breaks)</div>
        </div>
        """
        
        content += "</div>"  # Close schedule div
    
    content += '</main>'
    
    return content