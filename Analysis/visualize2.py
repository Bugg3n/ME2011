import os
import json
from datetime import datetime
import webbrowser

def generate_html(schedule_data):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Schedule Viewer</title>
        <style>
            body { font-family: Arial, sans-serif; }
            .day { cursor: pointer; padding: 10px; border: 1px solid #ccc; margin: 5px; display: inline-block; }
            .schedule { display: none; padding: 10px; border: 1px solid #ccc; margin-top: 10px; background: #f9f9f9; }
            .timeline-container { display: flex; flex-direction: column; margin-left: 120px; }
            .employee-row { display: flex; align-items: center; margin-bottom: 5px; }
            .employee-name { width: 110px; text-align: right; padding-right: 10px; font-weight: bold; position: absolute; left: 0; }
            .timeline { position: relative; width: calc(100% - 120px); height: 40px; background: #eee; margin-left: 120px; }
            .shift { position: absolute; height: 30px; background: #4CAF50; color: white; text-align: center; border-radius: 5px; line-height: 30px; font-size: 12px; }
            .lunch { position: absolute; width: 30px; height: 30px; background: orange; color: white; text-align: center; border-radius: 50%; line-height: 30px; font-size: 12px; }
            .time-axis { display: flex; justify-content: space-between; margin-top: 5px; font-size: 12px; margin-left: 120px; }
            .shift-list { margin-top: 20px; padding: 10px; background: #f1f1f1; border: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <h1>Schedule for March 2025</h1>
        <div id="calendar">
    """
    
    for date in schedule_data.keys():
        day = datetime.strptime(date, "%Y-%m-%d").day
        html += f'<div class="day" onclick="toggleSchedule(\'schedule-{day}\')">{day}</div>'
    
    html += "</div><div id='schedules'>"
    
    for date, shifts in schedule_data.items():
        day = datetime.strptime(date, "%Y-%m-%d").day
        html += f'<div id="schedule-{day}" class="schedule">'
        html += f'<h2>Schedule for {date}</h2>'
        html += '<div class="timeline-container">'
        
        for employee, shift_list in shifts.items():
            html += f'<div class="employee-row">'
            html += f'<div class="employee-name">{employee}</div>'
            html += '<div class="timeline">'
            
            for shift in shift_list:
                start_hour, start_minute = map(int, shift["start"].split(":"))
                end_hour, end_minute = map(int, shift["end"].split(":"))
                lunch_hour, lunch_minute = (map(int, shift["lunch"].split(":")) if shift["lunch"] != "None" else (None, None))
                
                min_time = 8 * 60  # Start of timeline (8:00 AM in minutes)
                max_time = 22 * 60  # End of timeline (10:00 PM in minutes)
                time_range = max_time - min_time
                
                start_pos = ((start_hour * 60 + start_minute - min_time) / time_range) * 100
                end_pos = ((end_hour * 60 + end_minute - min_time) / time_range) * 100
                width = end_pos - start_pos
                
                # Adjust position by subtracting 1 hour offset
                start_pos = max(0, start_pos - (100 / (max_time - min_time) * 60))
                
                html += f'<div class="shift" style="left:{start_pos}%; width:{width}%">{shift["start"]} - {shift["end"]}</div>'
                
                if lunch_hour is not None:
                    lunch_pos = ((lunch_hour * 60 + lunch_minute - min_time) / time_range) * 100
                    lunch_pos = max(0, lunch_pos - (100 / time_range * 60))  # Adjust lunch position
                    html += f'<div class="lunch" style="left:{lunch_pos}%">Lunch</div>'
            
            html += '</div></div>'
        
        html += '</div>'
        
        html += '<div class="time-axis">'
        for hour in range(8, 23):
            html += f'<span>{hour}:00</span>'
        html += '</div>'
        
        # Add shift list
        html += '<div class="shift-list">'
        html += '<h3>Shift List</h3>'
        for employee, shift_list in shifts.items():
            for shift in shift_list:
                html += f'<p><strong>{employee}:</strong> {shift["start"]} - {shift["end"]} (Lunch: {shift["lunch"]})</p>'
        html += '</div>'
        
        html += "</div>"
    
    html += """
        </div>
        <script>
            function toggleSchedule(id) {
                document.querySelectorAll('.schedule').forEach(el => el.style.display = 'none');
                document.getElementById(id).style.display = 'block';
            }
        </script>
    </body>
    </html>
    """

    file_path = "monthly_schedule.html"
    with open(file_path, "w") as file:
        file.write(html)

    print("HTML file 'schedule.html' generated successfully!")

    webbrowser.open(f"file:///{os.path.abspath(file_path)}")


    return html


def main():
    # Load the schedule data
    schedule_data = {
        "2025-03-01": {
            "Alice": [
                {"date": "2025-03-01", "start": "8:00", "end": "16:00", "lunch": "11:00"},
                {"date": "2025-03-01", "start": "17:00", "end": "20:00", "lunch": "None"}
            ],
            "Bob": [
                {"date": "2025-03-01", "start": "14:00", "end": "22:00", "lunch": "17:00"},
                {"date": "2025-03-01", "start": "11:00", "end": "14:00", "lunch": "None"}
            ]
        },
        "2025-03-02": {
            "Alice": [{"date": "2025-03-02", "start": "8:00", "end": "16:00", "lunch": "11:00"}]
        }
    }

    # Generate the HTML content
    html_content = generate_html(schedule_data)


if __name__ == "__main__":
    main()