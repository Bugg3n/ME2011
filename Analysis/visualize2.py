import os
from datetime import datetime
import webbrowser
import pandas as pd

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

def generate_employee_summary_html(df: pd.DataFrame) -> str:
    """Converts a DataFrame of employee stats to HTML table."""
    return df.to_html(index=False, classes="employee-summary-table", border=0)


def generate_html(schedule_data, unassigned_shifts=None, staffing_summary=None, output_path="HTML-files/monthly_schedule.html"):
    if unassigned_shifts is None:
        unassigned_shifts = []
    if staffing_summary is None:
        staffing_summary = {}
    
    # Generate just the schedule visualization content (without controls)
    schedule_content = generate_schedule_content(schedule_data, unassigned_shifts, staffing_summary)
    
    # In web mode, return ONLY the dynamic content
    if os.environ.get('WEB_MODE') == "1":
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

    /* New Summary Section Styles */
    .summary-section {{
        margin: 1rem;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}

    .metrics-container {{
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }}

    .primary-metrics {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
    }}

    .metric-card {{
        padding: 1rem;
        border-radius: 8px;
        background: #f8f9fa;
    }}

    .metric-card.positive {{
        border-left: 4px solid #28a745;
        background: #e8f5e9;
    }}

    .metric-card.warning {{
        border-left: 4px solid #ffc107;
        background: #fff8e1;
    }}

    .metric-card.negative {{
        border-left: 4px solid #dc3545;
        background: #ffebee;
    }}

    .metric-label {{
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 0.5rem;
    }}

    .metric-value {{
        font-size: 1.2rem;
        font-weight: bold;
    }}

    .secondary-metrics {{
        display: none;
        margin-top: 1rem;
        padding: 1rem;
        background: #f1f1f1;
        border-radius: 8px;
    }}

    .secondary-metrics.visible {{
        display: block;
    }}

    .detail-row {{
        display: flex;
        margin-bottom: 0.5rem;
    }}

    .detail-label {{
        flex: 1;
        font-weight: 500;
    }}

    .detail-value {{
        flex: 1;
    }}

    .toggle-details {{
        background: none;
        border: none;
        color: #007bff;
        cursor: pointer;
        padding: 0.5rem 0;
        text-align: left;
        font-size: 0.9rem;
    }}

    .toggle-details:hover {{
        text-decoration: underline;
    }}

    /* Existing timeline styles */
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
    .shift.unassigned {{
        background: #dc3545 !important; /* Bootstrap danger red */
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
        <div style="margin: 20px;">
            <button onclick="loadEmployeeSummary()">📋 Show Employee Summary</button>
            <div id="employeeStats" style="margin-top: 15px; font-family: monospace; background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 0 5px rgba(0,0,0,0.1);"></div>
        </div>
    </div>
    
    <div id="dynamicScheduleContent">
        {schedule_content}
    </div>

    <script>
        let isUpdating = false;
        let currentActiveDay = null;
        let currentStaffingSummary = null;

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
        
        function toggleDetails() {{
            const details = document.querySelector('.secondary-metrics');
            const button = document.querySelector('.toggle-details');
            if (details && button) {{
                details.classList.toggle('visible');
                button.textContent = details.classList.contains('visible') 
                    ? '▲ Hide Detailed Metrics' 
                    : '▼ Show Detailed Metrics';
            }}
        }}
        
        function attachEventListeners() {{
            // Reattach event listeners to any dynamic elements
            const toggleButton = document.querySelector('.toggle-details');
            if (toggleButton) {{
                toggleButton.removeEventListener('click', toggleDetails); // Remove existing first to prevent duplicates
                toggleButton.addEventListener('click', toggleDetails);
            }}
            
            // Reattach day click handlers - improved version
            document.querySelectorAll('.calendar .day').forEach(day => {{
                // Remove any existing click handlers
                day.onclick = null;
                day.addEventListener('click', function() {{
                    const dayNum = this.textContent.trim();
                    toggleSchedule(`schedule-${{dayNum}}`);
                }});
            }});
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
                    currentStaffingSummary = result.summary;
                    
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
                    
                    // Reattach event listeners to new elements
                    attachEventListeners();
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
            // Add input validation
            document.getElementById('salesCapacity').addEventListener('blur', validateInputs);
            document.getElementById('serviceTime').addEventListener('blur', validateInputs);
            document.getElementById('targetWait').addEventListener('blur', validateInputs);
            
            // Initialize all event listeners
            attachEventListeners();
        }});
        function loadEmployeeSummary() {{
            fetch('employee_summary.html')
                .then(response => {{
                    if (!response.ok) {{
                        throw new Error("Failed to load employee summary");
                    }}
                    return response.text();
                }})
                .then(html => {{
                    document.getElementById('employeeStats').innerHTML = html;
                }})
                .catch(error => {{
                    document.getElementById('employeeStats').innerHTML = `<p style='color:red;'>${{error.message}}</p>`;
                }});
        }}

    </script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html)
    
    # Only open in browser if not in web mode
    if not os.environ.get('WEB_MODE'):
        webbrowser.open(f"file:///{os.path.abspath(output_path)}")

    return html

def generate_schedule_content(schedule_data, unassigned_shifts=None, staffing_summary=None):
    """Generates just the schedule visualization content (without full HTML document structure)"""
    if unassigned_shifts is None:
        unassigned_shifts = []
    if staffing_summary is None:
        staffing_summary = {}
    
    def get_status_class(metric_name, value):
        """Enhanced status classifier"""
        if isinstance(value, str):
            value = value.lower()
            if 'adequate' in value or 'good' in value:
                return 'positive'
            if 'warning' in value or 'partial' in value:
                return 'warning'
            return 'negative'
        elif isinstance(value, (int, float)):
            if 'coverage' in metric_name.lower():
                return 'positive' if value >= 95 else 'warning' if value >= 80 else 'negative'
            elif 'shortage' in metric_name.lower():
                return 'negative' if value > 0 else 'positive'
        return ''
    
    # Primary metrics (always visible)
    primary_metrics = [
        ('Scheduled Hours', staffing_summary.get('total_scheduled_hours', 'N/A'), 'hours'),
        ('Required Hours', staffing_summary.get('total_required_hours', 'N/A'), 'hours'),
        ('Coverage', staffing_summary.get('store_coverage_%', staffing_summary.get('store_coverage', 'N/A')), '%'),
        ('Status', staffing_summary.get('status', 'N/A'), '')
    ]
    
    # Secondary metrics (expandable)
    secondary_metrics = [
        ('Expected Hours', staffing_summary.get('total_expected_hours', 'N/A'), 'hours'),
        ('Staff Shortage', staffing_summary.get('staff shortage', staffing_summary.get('staff_shortage', 'N/A')), 'hours'),
        ('Coverage Status', staffing_summary.get('coverage_status', 'N/A'), ''),
        ('Notes', staffing_summary.get('note', 'N/A'), '')
    ]
    
    # Generate primary metrics HTML
    primary_html = '\n'.join([
        f'<div class="metric-card {get_status_class(label, value)}">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}{unit if str(value) != "N/A" else ""}</div>'
        '</div>'
        for label, value, unit in primary_metrics
    ])
    
    # Generate secondary metrics HTML
    secondary_html = '\n'.join([
        f'<div class="detail-row">'
        f'<div class="detail-label">{label}:</div>'
        f'<div class="detail-value">{value}{unit if str(value) != "N/A" else ""}</div>'
        '</div>'
        for label, value, unit in secondary_metrics
    ])
    
    # Build the complete content
    content = f"""
    <div class="summary-section">
        <div class="staffing-summary">
            <h3>Staffing Summary</h3>
            <div class="primary-metrics">
                {primary_html}
            </div>
            <button class="toggle-details">▼ Show Detailed Metrics</button>
            <div class="secondary-metrics">
                {secondary_html}
            </div>
        </div>
    </div>"""
    
    if unassigned_shifts:
        content += """
        <div class="unassigned-shifts">
            <h3>⚠️ Unassigned Shifts</h3>
            <ul>
        """
        for shift in unassigned_shifts:
            content += f"<li>{shift['date']}: {shift['start']} - {shift['end']}</li>"
        content += """
            </ul>
        </div>
        """
    
    # Add the calendar days
    content += '<div class="calendar">'
    for date in schedule_data.keys():
        day = datetime.strptime(date, "%Y-%m-%d").day
        content += f'<div class="day">{day}</div>'
    content += '</div>'
    
    # Add the schedule visualizations
    content += '<main id="schedules">'
    for date, shifts in schedule_data.items():
        day = datetime.strptime(date, "%Y-%m-%d").day
        total_worked_hours = 0
        
        content += f'<div id="schedule-{day}" class="schedule">'
        content += f'<h2>{date}</h2>'
        
        # Timeline visualization
        min_hour = 8
        max_hour = 22
        total_hours = max_hour - min_hour
        minutes_per_hour = 60
        total_minutes = total_hours * minutes_per_hour
        
        content += '<div class="timeline-container">'
        
        for employee, shift_list in shifts.items():
            employee_hours = calculate_worked_hours(shift_list)
            total_worked_hours += employee_hours
            
            content += f'<div class="employee-row">'
            content += f'<div class="employee-name">{employee}</div>'
            content += '<div class="timeline-wrapper">'
            content += '<div class="timeline">'
            
            for shift in shift_list:
                start_time = datetime.strptime(shift["start"], "%H:%M")
                end_time = datetime.strptime(shift["end"], "%H:%M")
                
                start_min = (start_time.hour - min_hour) * 60 + start_time.minute
                end_min = (end_time.hour - min_hour) * 60 + end_time.minute
                start_percent = max(0, min(100, (start_min / total_minutes) * 100))
                end_percent = max(0, min(100, (end_min / total_minutes) * 100))
                width_percent = max(0, min(100 - start_percent, end_percent - start_percent))
                
                shift_class = "shift unassigned" if shift.get("unassigned") else "shift"
                content += f'<div class="{shift_class}" style="left:{start_percent}%; width:{width_percent}%"></div>'

                
                if shift["lunch"] != "None":
                    lunch_hour = int(shift["lunch"].split(":")[0])
                    lunch_start_percent = max(0, min(100, ((lunch_hour - min_hour) * 60 / total_minutes) * 100))
                    lunch_width_percent = max(0, min(100 - lunch_start_percent, (60 / total_minutes) * 100))
                    
                    content += f'<div class="lunch" style="left:{lunch_start_percent}%; width:{lunch_width_percent}%"></div>'
            
            content += '</div></div></div>'
        
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