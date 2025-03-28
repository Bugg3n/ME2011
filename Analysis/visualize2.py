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

def generate_html(schedule_data, unassigned_shifts=None, staffing_summary=None):
    print("in generate html")
    if unassigned_shifts is None:
        unassigned_shifts = []
    if staffing_summary is None:
        staffing_summary = {}
    
    # Generate just the schedule visualization content (without controls)
    schedule_content = generate_schedule_content(schedule_data, unassigned_shifts, staffing_summary)
    print("schedule generated")
    
    # In web mode, return ONLY the dynamic content
    if os.environ.get('WEB_MODE') == "1":
        print("In webmode. Returning")
        return schedule_content
    
    # For standalone mode, return full HTML page
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Work Schedule Optimizer • March 2025</title>
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

    .param-container {{
        display: flex;
        gap: 2rem;
    }}

    .param-group {{
        margin-bottom: 1rem;
        flex: 1;
    }}

    .param-description {{
        flex: 2;
        padding: 0.5rem;
        background: #f8f9fa;
        border-radius: 6px;
        font-size: 0.9rem;
        line-height: 1.5;
    }}

    .param-description h4 {{
        margin-top: 0;
        color: #007bff;
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

    .error-message {{
        color: #dc3545;
        font-size: 0.8rem;
        margin-top: 0.3rem;
        display: none;
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

    button:disabled {{
        background: #cccccc;
        cursor: not-allowed;
    }}

    .loading {{
        display: none;
        margin-left: 1rem;
        color: #666;
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

    .calendar .day.active {{
        background: #007bff;
        color: white;
    }}

    .schedule {{
        display: none;  /* Hidden by default */
        padding: 1rem;
        background: white;
        margin: 1rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}

    .schedule.active {{
        display: block;
    }}

    .summary-section {{
        margin: 1rem;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}

    .timeline-container {{
        margin-top: 1rem;
        padding-left: 120px;
    }}

    .employee-row {{
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        height: 30px;
    }}

    .employee-name {{
        width: 120px;
        font-weight: 600;
    }}

    .timeline-wrapper {{
        flex: 1;
        position: relative;
        height: 30px;
    }}

    .timeline {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 20px;
        background: #f0f0f0;
        border-radius: 4px;
        overflow: visible;
    }}

    .time-axis {{
        position: relative;
        height: 30px;
        margin-top: 10px;
        margin-left: 120px;
    }}

    .shift {{
        position: absolute;
        top: 0;
        height: 20px;
        background: #007bff;
        border-radius: 4px;
        z-index: 2;
    }}

    .lunch {{
        position: absolute;
        top: 0;
        height: 20px;
        background: #ff9900;
        opacity: 0.8;
        z-index: 3;
    }}

    .hour-marker {{
        position: absolute;
        height: 10px;
        width: 1px;
        background: #999;
        top: 0;
    }}

    .hour-label {{
        position: absolute;
        top: 15px;
        font-size: 0.75rem;
        transform: translateX(-50%);
    }}

    .shift-details {{
        margin-top: 1rem;
    }}

    .shift-entry {{
        margin-bottom: 0.8rem;
        padding: 0.8rem;
        background: #f8f9fa;
        border-radius: 6px;
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

    .unassigned-shifts {{
        background: #fff3cd;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }}

    .unassigned-shifts h3 {{
        margin-top: 0;
        color: #856404;
    }}

    .unassigned-shifts ul {{
        margin-bottom: 0;
    }}

    .staffing-summary {{
        background: #e9ecef;
        padding: 1.5rem;
        margin: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }}

    .staffing-summary h3 {{
        margin-top: 0;
        color: #007bff;
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 0.5rem;
    }}

    .summary-item {{
        margin-bottom: 0.5rem;
        display: flex;
    }}

    .summary-label {{
        font-weight: 600;
        min-width: 180px;
    }}

    .summary-value {{
        flex: 1;
    }}

    .status-positive {{
        color: #28a745;
    }}

    .status-warning {{
        color: #ffc107;
    }}

    .status-negative {{
        color: #dc3545;
    }}
</style>
</head>
<body>
    <div id="staticContent">
        <h1>Work Schedule Optimizer • March 2025</h1>
        
        <div class="control-panel">
            <h2>Queueing Parameters</h2>
            <div class="param-container">
                <div>
                    <div class="param-group">
                        <label for="salesCapacity">Sales Capacity (customers/hour):</label>
                        <input type="number" id="salesCapacity" value="12" min="1" max="50" step="1">
                        <div class="error-message" id="salesCapacityError">Please enter a value between 1 and 50</div>
                    </div>
                    <div class="param-group">
                        <label for="serviceTime">Avg. Service Time (minutes):</label>
                        <input type="number" id="serviceTime" value="3.0" min="0.5" max="30" step="0.1">
                        <div class="error-message" id="serviceTimeError">Please enter a value between 0.5 and 30</div>
                    </div>
                    <div class="param-group">
                        <label for="targetWait">Target Wait Time (minutes):</label>
                        <input type="number" id="targetWait" value="5.0" min="1" max="60" step="0.5">
                        <div class="error-message" id="targetWaitError">Please enter a value between 1 and 60</div>
                    </div>
                    <div class="param-group">
                        <button id="updateButton" onclick="updateSchedule()">Update Schedule</button>
                        <span class="loading" id="loadingIndicator">Calculating...</span>
                    </div>
                </div>
                <div class="param-description">
                    <h4>How Queueing Parameters Affect Scheduling</h4>
                    <p><strong>Sales Capacity:</strong> The maximum number of customers each employee can serve per hour. Higher values will result in fewer required staff.</p>
                    <p><strong>Avg. Service Time:</strong> The average time (in minutes) it takes to serve one customer. Longer service times require more staff to maintain service levels.</p>
                    <p><strong>Target Wait Time:</strong> The maximum desired wait time (in minutes) for customers. Lower target times will require more staff to reduce queue lengths.</p>
                    <p>These parameters are used in queueing theory calculations (M/M/c model) to determine optimal staffing levels throughout the day.</p>
                </div>
            </div>
        </div>
    </div>
    
    <div id="dynamicScheduleContent">
        {schedule_content}
    </div>

    <script>
        let isUpdating = false;
        let currentActiveDay = null;

        function validateInputs() {{
            let isValid = true;
            
            const salesCapacity = document.getElementById('salesCapacity');
            const salesCapacityError = document.getElementById('salesCapacityError');
            if (salesCapacity.value < 1 || salesCapacity.value > 50 || isNaN(salesCapacity.value)) {{
                salesCapacityError.style.display = 'block';
                isValid = false;
            }} else {{
                salesCapacityError.style.display = 'none';
            }}
            
            const serviceTime = document.getElementById('serviceTime');
            const serviceTimeError = document.getElementById('serviceTimeError');
            if (serviceTime.value < 0.5 || serviceTime.value > 30 || isNaN(serviceTime.value)) {{
                serviceTimeError.style.display = 'block';
                isValid = false;
            }} else {{
                serviceTimeError.style.display = 'none';
            }}
            
            const targetWait = document.getElementById('targetWait');
            const targetWaitError = document.getElementById('targetWaitError');
            if (targetWait.value < 1 || targetWait.value > 60 || isNaN(targetWait.value)) {{
                targetWaitError.style.display = 'block';
                isValid = false;
            }} else {{
                targetWaitError.style.display = 'none';
            }}
            
            return isValid;
        }}
        
        async function updateSchedule() {{
            if (isUpdating) return;
            
            if (!validateInputs()) {{
                return;
            }}
            
            isUpdating = true;
            
            const button = document.getElementById('updateButton');
            button.disabled = true;
            const loading = document.getElementById('loadingIndicator');
            loading.style.display = 'inline';
            
            const currentValues = {{
                salesCapacity: document.getElementById('salesCapacity').value,
                serviceTime: document.getElementById('serviceTime').value,
                targetWait: document.getElementById('targetWait').value
            }};
            
            const params = {{
                sales_capacity: parseFloat(currentValues.salesCapacity),
                average_service_time: parseFloat(currentValues.serviceTime),
                target_wait_time: parseFloat(currentValues.targetWait)
            }};
            
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
                
                if (result && result.content) {{
                    document.getElementById('dynamicScheduleContent').innerHTML = result.content;
                    
                    document.getElementById('salesCapacity').value = currentValues.salesCapacity;
                    document.getElementById('serviceTime').value = currentValues.serviceTime;
                    document.getElementById('targetWait').value = currentValues.targetWait;
                    
                    // Reset day selection after update
                    if (currentActiveDay) {{
                        document.querySelectorAll('.calendar .day').forEach(day => {{
                            day.classList.remove('active');
                        }});
                        currentActiveDay = null;
                    }}
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
            // Remove active class from all days
            document.querySelectorAll('.calendar .day').forEach(day => {{
                day.classList.remove('active');
            }});
            
            // Add active class to clicked day
            const clickedDay = document.querySelector(`.calendar .day[onclick*="${{id}}"]`);
            if (clickedDay) {{
                clickedDay.classList.add('active');
            }}
            
            // Hide all schedules
            document.querySelectorAll('.schedule').forEach(el => {{
                el.style.display = 'none';
            }});
            
            // Show the selected schedule
            const schedule = document.getElementById(id);
            if (schedule) {{
                schedule.style.display = 'block';
                currentActiveDay = id;
                window.scrollTo({{
                    top: schedule.offsetTop - 20,
                    behavior: 'smooth'
                }});
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            // Don't show any schedule by default now
            // Just focus on the summary
            
            // Add input validation
            document.getElementById('salesCapacity').addEventListener('blur', validateInputs);
            document.getElementById('serviceTime').addEventListener('blur', validateInputs);
            document.getElementById('targetWait').addEventListener('blur', validateInputs);
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

def generate_schedule_content(schedule_data, unassigned_shifts=None, staffing_summary=None):
    """Generates just the schedule visualization content"""
    if unassigned_shifts is None:
        unassigned_shifts = []
    if staffing_summary is None:
        staffing_summary = {}
    
    content = """
    <div class="summary-section">
        <div class="staffing-summary">
            <h3>Staffing Summary</h3>"""
    
    # Helper function to determine status class
    def get_status_class(value):
        if isinstance(value, str):
            value = value.lower()
            if 'adequate' in value or 'good' in value or 'sufficient' in value:
                return 'status-positive'
            elif 'warning' in value or 'partial' in value:
                return 'status-warning'
            elif 'shortage' in value or 'insufficient' in value:
                return 'status-negative'
        return ''
    
    # Get values with fallbacks for different key naming possibilities
    summary_items = [
        ('Total Scheduled Hours', staffing_summary.get('total_scheduled_hours', 'N/A'), 'hours'),
        ('Total Expected Hours', staffing_summary.get('total_expected_hours', 'N/A'), 'hours'),
        ('Total Required Hours', staffing_summary.get('total_required_hours', 'N/A'), 'hours'),
        ('Staff Balance', staffing_summary.get('staff shortage', staffing_summary.get('staff_shortage', 'N/A')), 'hours'),
        ('Staffing Status', staffing_summary.get('status', 'N/A'), ''),
        ('Store Coverage', staffing_summary.get('store_coverage_%', staffing_summary.get('store_coverage', 'N/A')), '%'),
        ('Coverage Status', staffing_summary.get('coverage_status', 'N/A'), ''),
        ('Note', staffing_summary.get('note', 'N/A'), '')
    ]
    
    for label, value, unit in summary_items:
        status_class = get_status_class(str(value))
        if isinstance(value, (int, float)):
            value = f"{value:.2f}"
        content += f"""
        <div class="summary-item">
            <div class="summary-label">{label}:</div>
            <div class="summary-value {status_class}">{value} {unit if str(value) != 'N/A' else ''}</div>
        </div>"""
    
    content += """
        </div>
    </div>"""
    
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
    
    # Add the schedule visualizations (hidden by default)
    content += '<main id="schedules">'
    for date, shifts in schedule_data.items():
        day = datetime.strptime(date, "%Y-%m-%d").day
        total_worked_hours = 0
        
        content += f'<div id="schedule-{day}" class="schedule">'
        content += f'<h2>{date}</h2>'
        
        # Define time range constants (8:00 AM to 10:00 PM) #OBS THIS WILL HAVE TO BE ADAPTABLE
        min_hour = 8
        max_hour = 22
        total_hours = max_hour - min_hour
        minutes_per_hour = 60
        total_minutes = total_hours * minutes_per_hour
        
        # Timeline container for all employee shifts
        content += '<div class="timeline-container">'
        
        # Employee shifts
        for employee, shift_list in shifts.items():
            employee_hours = calculate_worked_hours(shift_list)
            total_worked_hours += employee_hours
            
            content += f'<div class="employee-row">'
            content += f'<div class="employee-name">{employee}</div>'
            content += '<div class="timeline-wrapper">'
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
                content += f'<div class="shift" style="left:{start_percent}%; width:{width_percent}%"></div>'
                
                # Lunch break (only if specified)
                if shift["lunch"] != "None":
                    lunch_time = datetime.strptime(shift["lunch"], "%H:%M")
                    lunch_min = (lunch_time.hour - min_hour) * 60 + lunch_time.minute
                    lunch_percent = max(0, min(100, (lunch_min / total_minutes) * 100))
                    lunch_width = (60 / total_minutes) * 100  # 1 hour lunch
                    
                    # Ensure lunch doesn't extend beyond shift
                    lunch_end_percent = min(lunch_percent + lunch_width, end_percent)
                    adjusted_lunch_width = lunch_end_percent - lunch_percent
                    
                    if adjusted_lunch_width > 0:
                        content += f'<div class="lunch" style="left:{lunch_percent}%; width:{adjusted_lunch_width}%"></div>'
            
            content += '</div></div></div>'  # Close timeline, timeline-wrapper, and employee-row
        
        # Single time axis at the bottom
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
        
        content += '</div>'  # Close timeline-container
        
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