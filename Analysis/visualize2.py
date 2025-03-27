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
    if unassigned_shifts is None:
        unassigned_shifts = []
    
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Work Schedule Viewer</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #4361ee;
                --primary-light: #e0e7ff;
                --secondary: #3f37c9;
                --success: #4cc9f0;
                --warning: #f8961e;
                --danger: #f94144;
                --light: #f8f9fa;
                --dark: #212529;
                --gray: #6c757d;
                --border-radius: 8px;
                --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --transition: all 0.3s ease;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                line-height: 1.6;
                color: var(--dark);
                background-color: #f5f7fa;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            h1, h2, h3 {
                color: var(--dark);
                font-weight: 600;
            }
            
            h1 {
                font-size: 2rem;
                margin-bottom: 1.5rem;
                color: var(--secondary);
            }
            
            .calendar {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 2rem;
            }
            
            .day {
                cursor: pointer;
                padding: 10px 15px;
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: var(--border-radius);
                font-weight: 500;
                transition: var(--transition);
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            }
            
            .day:hover {
                background: var(--primary-light);
                border-color: var(--primary);
            }
            
            .schedule {
                display: none;
                padding: 25px;
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--box-shadow);
                margin-bottom: 2rem;
            }
            
            .timeline-container {
                display: flex;
                flex-direction: column;
                margin-left: 140px;
                position: relative;
            }
            
            .employee-row {
                display: flex;
                align-items: center;
                margin-bottom: 12px;
                position: relative;
                height: 40px;
            }
            
            .employee-name {
                width: 130px;
                text-align: right;
                padding-right: 15px;
                font-weight: 500;
                position: absolute;
                left: -140px;
            }
            
            .timeline {
                position: relative;
                width: calc(100% - 2px);
                height: 32px;
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: var(--border-radius);
            }
            
            .shift {
                position: absolute;
                top: 0;
                height: 32px;
                background: var(--primary);
                border-radius: var(--border-radius);
                transition: var(--transition);
                z-index: 1;
            }
            
            .shift:hover {
                z-index: 10;
                box-shadow: 0 0 0 2px white, 0 0 0 4px var(--primary);
            }
            
            .shift-tooltip {
                position: absolute;
                bottom: calc(100% + 8px);
                left: 50%;
                transform: translateX(-50%);
                background: var(--dark);
                color: white;
                padding: 6px 12px;
                border-radius: var(--border-radius);
                font-size: 13px;
                white-space: nowrap;
                display: none;
                z-index: 20;
                box-shadow: var(--box-shadow);
            }
            
            .shift:hover .shift-tooltip {
                display: block;
            }
            
            .lunch {
                position: absolute;
                top: 0;
                height: 32px;
                background: rgba(248, 150, 30, 0.9);
                border-radius: var(--border-radius);
                z-index: 2;
            }
            
            .lunch:hover {
                background: rgba(248, 150, 30, 0.5);
                box-shadow: 0 0 0 2px white, 0 0 0 4px var(--primary);
            }
            
            .time-axis {
                position: relative;
                height: 40px;
                margin: 15px 0 25px 140px;
                font-size: 13px;
                width: calc(100% - 140px);
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--box-shadow);
            }
            
            .hour-marker {
                position: absolute;
                top: 0;
                width: 1px;
                height: 12px;
                background: var(--gray);
                transform: translateX(-50%);
            }
            
            .hour-label {
                position: absolute;
                top: 15px;
                transform: translateX(-50%);
                white-space: nowrap;
                font-size: 12px;
                font-weight: 500;
                color: var(--gray);
            }
            
            .shift-details {
                margin-top: 30px;
                padding: 20px;
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--box-shadow);
            }
            
            .shift-entry {
                margin-bottom: 10px;
                padding-bottom: 10px;
                border-bottom: 1px solid #f1f5f9;
            }
            
            .shift-entry:last-child {
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }
            
            .unassigned-shifts {
                background-color: #fff5f5;
                padding: 20px;
                border-radius: var(--border-radius);
                margin-bottom: 2rem;
                box-shadow: var(--box-shadow);
                border-left: 4px solid var(--danger);
            }
            
            .stats-card {
                background: white;
                padding: 20px;
                border-radius: var(--border-radius);
                box-shadow: var(--box-shadow);
                margin-top: 20px;
            }
            
            .stats-value {
                font-size: 1.5rem;
                font-weight: 600;
                color: var(--primary);
            }
            
            .stats-label {
                color: var(--gray);
                font-size: 0.9rem;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Work Schedule • March 2025</h1>
            <div class="calendar">
    """
    
    if unassigned_shifts:
        html += """
        <div class="unassigned-shifts">
            <h3>⚠️ Unassigned Shifts</h3>
            <ul>
        """
        for shift in unassigned_shifts:
            html += f"<li>{shift['date']}: {shift['start']} - {shift['end']}</li>"
        html += """
            </ul>
        </div>
        """
    
    for date in schedule_data.keys():
        day = datetime.strptime(date, "%Y-%m-%d").day
        html += f'<div class="day" onclick="toggleSchedule(\'schedule-{day}\')">{day}</div>'
    
    html += """
            </div>
        </header>
        <main id="schedules">
    """
    
    for date, shifts in schedule_data.items():
        day = datetime.strptime(date, "%Y-%m-%d").day
        total_worked_hours = 0
        
        html += f'<div id="schedule-{day}" class="schedule">'
        html += f'<h2>{date}</h2>'
        
        # Define time range constants (8:00 AM to 10:00 PM)
        min_hour = 8
        max_hour = 22
        total_hours = max_hour - min_hour
        minutes_per_hour = 60
        total_minutes = total_hours * minutes_per_hour
        
        # Timeline visualization
        html += '<div class="timeline-container">'
        
        for employee, shift_list in shifts.items():
            employee_hours = calculate_worked_hours(shift_list)
            total_worked_hours += employee_hours
            
            html += f'<div class="employee-row">'
            html += f'<div class="employee-name">{employee}</div>'
            html += '<div class="timeline">'
            
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
                html += f'<div class="shift" style="left:{start_percent}%; width:{width_percent}%">'
                html += f'<div class="shift-tooltip">{shift["start"]} - {shift["end"]}</div>'
                html += '</div>'
                
                # Lunch break
                if shift["lunch"] != "None":
                    lunch_hour = int(shift["lunch"].split(":")[0])
                    lunch_start_percent = max(0, min(100, ((lunch_hour - min_hour) * 60 / total_minutes) * 100))
                    lunch_width_percent = max(0, min(100 - lunch_start_percent, (60 / total_minutes) * 100))
                    
                    html += f'<div class="lunch" style="left:{lunch_start_percent}%; width:{lunch_width_percent}%"></div>'
            
            html += '</div></div>'
        
        html += '</div>'  # Close timeline-container
        
        # Time axis
        html += '<div class="time-axis">'
        for hour in range(min_hour, max_hour + 1):
            for minute in [0, 30]:
                if hour == max_hour and minute == 30:
                    continue
                time_percent = (((hour - min_hour) * 60 + minute) / total_minutes) * 100
                html += f'<div class="hour-marker" style="left:{time_percent}%"></div>'
                if minute == 0:
                    html += f'<div class="hour-label" style="left:{time_percent}%">{hour}:00</div>'
        html += '</div>'
        
        # Shift details
        html += '<div class="shift-details">'
        html += '<h3>Shift Details</h3>'
        for employee, shift_list in shifts.items():
            html += f'<div class="shift-entry"><strong>{employee}</strong><br>'
            for shift in shift_list:
                html += f'{shift["start"]} - {shift["end"]}'
                if shift["lunch"] != "None":
                    html += f' (Lunch at {shift["lunch"]})'
                html += '<br>'
            html += '</div>'
        html += '</div>'
        
        # Total hours card
        html += f"""
        <div class="stats-card">
            <div class="stats-value">{total_worked_hours} hours</div>
            <div class="stats-label">Total worked hours (excluding lunch breaks)</div>
        </div>
        """
        
        html += "</div>"  # Close schedule div
    
    html += """
        </main>
        <script>
            function toggleSchedule(id) {
                document.querySelectorAll('.schedule').forEach(el => {
                    el.style.display = 'none';
                });
                const schedule = document.getElementById(id);
                if (schedule) {
                    schedule.style.display = 'block';
                    // Scroll to the schedule with some offset
                    window.scrollTo({
                        top: schedule.offsetTop - 20,
                        behavior: 'smooth'
                    });
                }
            }
            
            // Show first schedule by default
            document.addEventListener('DOMContentLoaded', function() {
                const firstSchedule = document.querySelector('.schedule');
                if (firstSchedule) {
                    firstSchedule.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """

    file_path = "monthly_schedule.html"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"HTML file generated successfully at {os.path.abspath(file_path)}")
    webbrowser.open(f"file:///{os.path.abspath(file_path)}")

    return html