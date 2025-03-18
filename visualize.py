import webbrowser
import os

weekly_schedule = [
    [{'start': '8:00', 'end': '16:00', 'lunch': '11:00'}, {'start': '14:00', 'end': '22:00', 'lunch': '18:00'}],
    [{'start': '9:00', 'end': '17:00', 'lunch': '12:00'}, {'start': '15:00', 'end': '22:00', 'lunch': 'None'}],
    [{'start': '8:00', 'end': '16:00', 'lunch': '12:00'}, {'start': '14:00', 'end': '22:00', 'lunch': '18:00'}],
    [{'start': '9:00', 'end': '17:00', 'lunch': 'None'}, {'start': '15:00', 'end': '22:00', 'lunch': 'None'}],
    [{'start': '8:00', 'end': '16:00', 'lunch': '11:00'}, {'start': '14:00', 'end': '22:00', 'lunch': '18:00'}],
    [{'start': '10:00', 'end': '18:00', 'lunch': '13:00'}, {'start': '14:00', 'end': '22:00', 'lunch': '18:00'}],
    [{'start': '8:00', 'end': '14:00', 'lunch': 'None'}, {'start': '12:00', 'end': '18:00', 'lunch': '15:00'}]
]

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Interactive Weekly Schedule</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f4f8;
            padding: 20px;
        }
        .day-container {
            background-color: #fff;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.1);
        }
        .day-title {
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            user-select: none;
        }
        .shift-details {
            margin-top: 10px;
            display: none; /* Initially hidden */
        }
        .shift-row {
            position: relative;
            height: 35px;
            background-color: #e6e6e6;
            margin-bottom: 5px;
            border-radius: 6px;
        }
        .shift-block, .lunch-block {
            position: absolute;
            height: 100%;
            color: white;
            border-radius: 6px;
            font-size: 13px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .shift-block {
            background-color: #4CAF50;
        }
        .lunch-block {
            background-color: #FF9800;
        }
        .time-labels {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-top: 5px;
            padding: 0 5px;
        }
    </style>
    <script>
        function toggleDetails(id) {
            var content = document.getElementById(id);
            if (content.style.display === "none" || content.style.display === "") {
                content.style.display = "block";
            } else {
                content.style.display = "none";
            }
        }
    </script>
</head>
<body>
<div class="schedule-container">
"""

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
start_hour = 8
end_hour = 22
total_minutes = (end_hour - start_hour) * 60

for day_idx, day in enumerate(weekly_schedule):
    day_id = f"day{day_idx}"
    html_content += f'''
    <div class="day-container">
        <div class="day-title" onclick="toggleDetails('{day_id}')">{days[day_idx]}</div>
        <div class="shift-details" id="{day_id}">
    '''
    for shift in day:
        sh, sm = map(int, shift['start'].split(':'))
        eh, em = map(int, shift['end'].split(':'))
        shift_start_pct = ((sh - start_hour) * 60 + sm) / total_minutes * 100
        shift_width_pct = ((eh - sh) * 60 + (em - sm)) / total_minutes * 100

        html_content += '<div class="shift-row">'
        html_content += f'<div class="shift-block" style="left:{shift_start_pct}%; width:{shift_width_pct}%;">{shift["start"]}-{shift["end"]}</div>'
        
        if shift['lunch'] != 'None':
            lh, lm = map(int, shift['lunch'].split(':'))
            lunch_start_pct = ((lh - start_hour) * 60 + lm) / total_minutes * 100
            lunch_width_pct = 30 / total_minutes * 100  # 30-minute lunch
            html_content += f'<div class="lunch-block" style="left:{lunch_start_pct}%; width:{lunch_width_pct}%;">Lunch</div>'

        html_content += '</div>'

    html_content += '<div class="time-labels">'
    for t in range(start_hour, end_hour + 1, 2):
        html_content += f'<span>{t}:00</span>'
    html_content += '</div></div></div>'

html_content += """
</div>
</body>
</html>
"""

file_path = "interactive_schedule.html"
with open(file_path, "w") as file:
    file.write(html_content)

webbrowser.open(f"file:///{os.path.abspath(file_path)}")