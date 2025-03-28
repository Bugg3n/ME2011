""" import os
import json
import webbrowser
import calendar

def calculate_shift_hours(shift):
    """
    Calculate the duration of a shift in hours, excluding lunch time.
    """
    start = list(map(int, shift['start'].split(':')))
    end = list(map(int, shift['end'].split(':')))
    total_hours = (end[0] - start[0]) + (end[1] - start[1]) / 60

    # Subtract 1 hour if there is a lunch break
    if shift['lunch'] != 'None':
        total_hours -= 1  # Assuming lunch is 1 hour

    return total_hours

def calculate_weekly_hours(monthly_schedule):
    """
    Calculate total hours for each week in the monthly schedule.
    """
    weekly_hours = []
    for week in monthly_schedule:
        total_hours = 0
        for day in week:
            for shift in day:
                total_hours += calculate_shift_hours(shift)
        weekly_hours.append(round(total_hours, 2))
    return weekly_hours

def calculate_daily_hours(day):
    """
    Calculate total hours for a single day.
    """
    total_hours = 0
    for shift in day:
        total_hours += calculate_shift_hours(shift)
    return round(total_hours, 2)

def visualize_assigned_shifts(assigned_shifts, shift_date):
    import matplotlib.pyplot as plt
    import numpy as np

    employee_names = list(assigned_shifts.keys())
    num_employees = len(employee_names)

    fig, ax = plt.subplots(figsize=(12, num_employees * 0.6 + 2))

    def time_to_float(time_str):
        """Convert time in 'HH:MM' format to float (e.g., 9:00 -> 9.0)."""
        hours, minutes = map(int, time_str.split(":"))
        return hours + minutes / 60

    y_positions = np.arange(num_employees)

    for i, employee in enumerate(employee_names):
        shifts = assigned_shifts[employee]
        for shift in shifts:
            start_time = time_to_float(shift["start"])
            end_time = time_to_float(shift["end"])
            ax.barh(y_positions[i], end_time - start_time, left=start_time, height=0.4, 
                    color='skyblue', edgecolor='black', label="Shift" if i == 0 else "")

            ax.text((start_time + end_time) / 2, y_positions[i], f"{shift['start']} - {shift['end']}", 
                    va='center', ha='center', fontsize=10, color='black')

    ax.set_yticks(y_positions)
    ax.set_yticklabels(employee_names)
    ax.set_xlabel("Time of Day")
    ax.set_title(f"Assigned Shifts for {shift_date}")

    x_ticks = np.arange(8, 22, 1)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f"{int(t)}:00" for t in x_ticks])

    ax.grid(axis='x', linestyle='--', alpha=0.7)

    plt.show()

################################

def main(year_month, store, monthly_schedule=None, staff_needed=None):
    if monthly_schedule is None:
        store += " - TRIAL"
        monthly_schedule = [
            [[{'start': '8:00', 'end': '16:00', 'lunch': '11:00'}, {'start': '14:00', 'end': '22:00', 'lunch': '18:00'}] for _ in range(7)],
            [[{'start': '9:00', 'end': '17:00', 'lunch': '12:00'}, {'start': '15:00', 'end': '22:00', 'lunch': 'None'}] for _ in range(7)],
            [[{'start': '10:00', 'end': '18:00', 'lunch': '13:00'}, {'start': '12:00', 'end': '20:00', 'lunch': '16:00'}] for _ in range(7)],
            [[{'start': '8:00', 'end': '14:00', 'lunch': 'None'}, {'start': '12:00', 'end': '18:00', 'lunch': '15:00'}] for _ in range(7)]
        ]

    if staff_needed is None:
        staff_needed = [
            [[2, 1, 1, 0, 1, 1, 3, 3, 3, 3, 2, 1, 1, 1] for _ in range(7)] for _ in range(4)
        ]

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_hour, end_hour = 8, 22
    total_minutes = (end_hour - start_hour) * 60

    # Calculate total hours for each week
    weekly_hours = calculate_weekly_hours(monthly_schedule)

    # Convert staff_needed to JSON for JavaScript
    staff_needed_json = json.dumps(staff_needed)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Monthly Schedule Viewer</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background-color: #f0f4f8; 
                padding: 20px; 
                margin: 0; 
            }}
            .container {{ 
                max-width: 1000px; 
                margin: auto; 
                background-color: #fff; 
                border-radius: 10px; 
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
                overflow: hidden; 
            }}
            .header {{ 
                text-align: center; 
                padding: 20px; 
                background: linear-gradient(135deg, #6a11cb, #2575fc); 
                color: white; 
                margin-bottom: 20px; 
            }}
            .header h1 {{ 
                margin: 0; 
                font-size: 28px; 
                font-weight: 600; 
            }}
            .header h2 {{ 
                margin: 5px 0 0; 
                font-size: 20px; 
                font-weight: 400; 
            }}
            .section {{ 
                margin-bottom: 20px; 
                border-radius: 10px; 
                overflow: hidden; 
                background-color: #fff; 
                box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1); 
            }}
            .section .section {{ 
                margin-bottom: 10px; 
            }}
            .section-title {{ 
                padding: 15px; 
                cursor: pointer; 
                user-select: none; 
                display: flex; 
                align-items: center; 
                transition: background-color 0.3s ease; 
            }}
            .week-title {{
                background-color: #e3f2fd; 
                font-size: 20px; 
                font-weight: bold; 
                border-bottom: 2px solid #90caf9; 
            }}
            .day-title {{
                background-color: #f8f9fa; 
                font-size: 16px; 
                font-weight: 600; 
                border-bottom: 1px solid #dee2e6; 
            }}
            .hours {{
                color: #666; 
                font-weight: 600; 
                margin-left: 8px; 
                font-size: 0.85em; 
                font-style: italic; 
                opacity: 0.9; 
            }}
            .week-title:hover {{ background-color: #bbdefb; }}
            .day-title:hover {{ background-color: #e9ecef; }}
            .content {{ 
                display: none; 
                padding: 15px; 
                transition: opacity 0.3s ease; 
            }}
            .shift-row {{ 
                position: relative; 
                height: 35px; 
                background-color: #e6e6e6; 
                margin-bottom: 5px; 
                border-radius: 6px; 
            }}
            .shift-block, .lunch-block {{ 
                position: absolute; 
                height: 100%; 
                color: white; 
                border-radius: 6px; 
                font-size: 13px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
            }}
            .shift-block {{ background-color: #4CAF50; }}
            .lunch-block {{ background-color: #FF9800; }}
            button {{ 
                margin-top: 10px; 
                padding: 8px 16px; 
                font-size: 14px; 
                cursor: pointer; 
                background-color: #2575fc; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                transition: background-color 0.3s ease; 
            }}
            button:hover {{ background-color: #1a5bbf; }}
            .graph {{ margin-top: 10px; }}
            .graph canvas {{ max-width: 100%; }}
            .explanation {{ 
                margin-top: 15px; 
                padding: 10px; 
                background-color: #f8f9fa; 
                border-radius: 5px; 
                border: 1px solid #dee2e6; 
                font-size: 14px; 
                color: #333; 
            }}
            .timeline {{
                display: flex; 
                justify-content: space-between; 
                margin-top: 10px; 
                font-size: 12px; 
                color: #555; 
            }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            const staffNeeded = {staff_needed_json};

            function toggle(id) {{
                let el = document.getElementById(id);
                if (el.style.display === "none" || el.style.display === "") {{
                    el.style.display = "block";
                }} else {{
                    el.style.display = "none";
                }}
            }}

            function showGraph(weekIdx, dayIdx) {{
                const graphId = `week_${{weekIdx}}_day_${{dayIdx}}_graph`;
                let graphEl = document.getElementById(graphId);

                if (graphEl.style.display === "none" || graphEl.style.display === "") {{
                    // Generate the graph
                    const ctx = document.createElement('canvas');
                    ctx.id = `chart_${{weekIdx}}_${{dayIdx}}`;
                    graphEl.innerHTML = ''; // Clear previous graph
                    graphEl.appendChild(ctx);

                    const data = staffNeeded[weekIdx - 1][dayIdx];
                    new Chart(ctx, {{
                        type: 'bar',
                        data: {{
                            labels: Array.from({{length: data.length}}, (_, i) => `Hour ${{i + 1}}`),
                            datasets: [{{
                                label: 'Staff Needed',
                                data: data,
                                backgroundColor: 'skyblue',
                                borderColor: 'blue',
                                borderWidth: 1
                            }}]
                        }},
                        options: {{
                            scales: {{
                                y: {{
                                    beginAtZero: true,
                                    title: {{
                                        display: true,
                                        text: 'Staff Needed'
                                    }}
                                }},
                                x: {{
                                    title: {{
                                        display: true,
                                        text: 'Hour (from opening time)'
                                    }}
                                }}
                            }},
                            plugins: {{
                                title: {{
                                    display: true,
                                    text: 'Staff Needed per Hour'
                                }}
                            }}
                        }}
                    }});

                    // Add a prewritten explanation text
                    const explanation = document.createElement('div');
                    explanation.className = 'explanation';
                    explanation.innerHTML = `
                        <strong>Explanation:</strong><br>
                        This graph shows the number of staff required per hour (blue bars). 
                        Shifts are indicated by green blocks in the schedule above, and lunch breaks 
                        are highlighted in orange. Adjustments can be made based on real-time demand.
                    `;
                    graphEl.appendChild(explanation);

                    graphEl.style.display = "block";
                }} else {{
                    graphEl.style.display = "none";
                }}
            }}
        </script>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h1>Schedule for Store: {store}</h1>
            <h2>{year_month}</h2>
        </div>
    """

    # Generate monthly schedule (weeks/days)
    for week_idx, week in enumerate(monthly_schedule, 1):
        week_id = f"week_{week_idx}"
        total_weekly_hours = weekly_hours[week_idx - 1]
        html_content += f'''
        <div class="section">
            <div class="section-title week-title" onclick="toggle('{week_id}')">
                Week {week_idx} - <span class="hours">{total_weekly_hours}h</span>
            </div>
            <div class="content" id="{week_id}">
        '''

        for day_idx, day in enumerate(week):
            day_id = f"{week_id}_day_{day_idx}"
            total_daily_hours = calculate_daily_hours(day)
            html_content += f'''
            <div class="section">
                <div class="section-title day-title" onclick="toggle('{day_id}')">
                    {days[day_idx]} - <span class="hours">{total_daily_hours}h</span>
                </div>
                <div class="content" id="{day_id}">
            '''

            # Add a summary of shifts and lunch breaks
            html_content += '<div class="shift-summary">'
            for shift in day:
                shift_summary = f"Shift: {shift['start']} - {shift['end']}"
                if shift['lunch'] != 'None':
                    shift_summary += f" | Lunch: {shift['lunch']}"
                html_content += f'<div>{shift_summary}</div>'
            html_content += '</div>'

            for shift in day:
                sh, sm = map(int, shift['start'].split(':'))
                eh, em = map(int, shift['end'].split(':'))
                shift_start_pct = ((sh - start_hour) * 60 + sm) / total_minutes * 100
                shift_width_pct = ((eh - sh) * 60 + (em - sm)) / total_minutes * 100

                html_content += '<div class="shift-row">'
                html_content += f'<div class="shift-block" style="left:{shift_start_pct}%; width:{shift_width_pct}%;"></div>'

                if shift['lunch'] != 'None':
                    lh, lm = map(int, shift['lunch'].split(':'))
                    lunch_start_pct = ((lh - start_hour) * 60 + lm) / total_minutes * 100
                    lunch_width_pct = 30 / total_minutes * 100
                    html_content += f'<div class="lunch-block" style="left:{lunch_start_pct}%; width:{lunch_width_pct}%;">Lunch</div>'

                html_content += '</div>'

            # Add a timeline at the bottom
            html_content += '<div class="timeline">'
            for hour in range(start_hour, end_hour + 1):
                html_content += f'<div>{hour}:00</div>'
            html_content += '</div>'

            # Add the "Further details" button and the graph container
            html_content += f'''
            <button onclick="showGraph({week_idx}, {day_idx})">Further details</button>
            <div class="graph" id="{day_id}_graph" style="display: none;"></div>
            '''
            html_content += '</div></div>'

        html_content += '</div></div>'

    html_content += """
    </div>
    </body>
    </html>
    """

    file_path = "monthly_schedule.html"
    with open(file_path, "w") as file:
        file.write(html_content)

    webbrowser.open(f"file:///{os.path.abspath(file_path)}")


def visualize_model3(year, month, store, assigned_shifts, staff_needed):
    """
    Generates an interactive HTML schedule visualization with bar-style shift visualization.

    Args:
        year (int): Year of the schedule.
        month (int): Month of the schedule.
        store (str): Store name or ID.
        assigned_shifts (dict): Employee shift assignments grouped by date.
        staff_needed (dict): Hourly staff requirements.
    """
    
    # Convert staff_needed to JSON for JavaScript
    staff_needed_json = json.dumps(staff_needed)

    # Get number of days in the month
    num_days = calendar.monthrange(year, month)[1]
    month_name = calendar.month_name[month]

    # HTML structure
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Monthly Schedule Viewer</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 1000px;
                margin: auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
            }}
            .header {{
                text-align: center;
                background: #4CAF50;
                color: white;
                padding: 15px;
                border-radius: 10px;
            }}
            .day-section {{
                margin-bottom: 15px;
                padding: 10px;
                background: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            .day-title {{
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                padding: 10px;
                background: #e3f2fd;
                border-radius: 5px;
                margin-bottom: 5px;
            }}
            .shifts-container {{
                display: none;
                padding: 10px;
                background: #f9f9f9;
                border-radius: 5px;
            }}
            .shift-row {{
                position: relative;
                height: 35px;
                background-color: #e6e6e6;
                margin-bottom: 5px;
                border-radius: 6px;
                display: flex;
                align-items: center;
                padding-left: 10px;
                font-weight: bold;
            }}
            .shift-block, .lunch-block {{
                position: absolute;
                height: 100%;
                color: white;
                border-radius: 6px;
                font-size: 13px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .shift-block {{ background-color: #4CAF50; }}
            .lunch-block {{ background-color: #FF9800; }}
            .toggle-btn {{
                margin-top: 10px;
                padding: 8px 16px;
                font-size: 14px;
                cursor: pointer;
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
            }}
            .toggle-btn:hover {{ background: #1976D2; }}
            .timeline {{
                display: flex;
                justify-content: space-between;
                margin-top: 10px;
                font-size: 12px;
                color: #555;
            }}
        </style>
        <script>
            const staffNeeded = {staff_needed_json};

            function toggleSection(id) {{
                let section = document.getElementById(id);
                section.style.display = (section.style.display === "none" || section.style.display === "") ? "block" : "none";
            }}
        </script>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h1>Schedule for Store: {store}</h1>
            <h2>{month_name} {year}</h2>
        </div>
    """

    # Generate the shift visualization
    start_hour, end_hour = 8, 22  # Define the working hours range
    total_minutes = (end_hour - start_hour) * 60  # Convert to total minutes

    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        html_content += f"""
        <div class="day-section">
            <div class="day-title" onclick="toggleSection('day_{day}')">
                {date_str} - Shifts
            </div>
            <div class="shifts-container" id="day_{day}">
        """

        # Display assigned shifts as bar schedule
        if date_str in assigned_shifts:
            for employee, shifts in assigned_shifts[date_str].items():
                html_content += f'<div class="shift-row">{employee}</div>'
                for shift in shifts:
                    # Convert shift time into percentage-based width
                    sh, sm = map(int, shift["start"].split(':'))
                    eh, em = map(int, shift["end"].split(':'))
                    shift_start_pct = ((sh - start_hour) * 60 + sm) / total_minutes * 100
                    shift_width_pct = ((eh - sh) * 60 + (em - sm)) / total_minutes * 100

                    html_content += f'<div class="shift-block" style="left:{shift_start_pct}%; width:{shift_width_pct}%;"></div>'

                    # Add lunch break if applicable
                    if shift['lunch'] != 'None':
                        lh, lm = map(int, shift['lunch'].split(':'))
                        lunch_start_pct = ((lh - start_hour) * 60 + lm) / total_minutes * 100
                        lunch_width_pct = 30 / total_minutes * 100  # Assume 30-minute lunch
                        html_content += f'<div class="lunch-block" style="left:{lunch_start_pct}%; width:{lunch_width_pct}%;">Lunch</div>'

        else:
            html_content += '<div>No shifts assigned for this day.</div>'

        # Add a timeline below the shift visualization
        html_content += '<div class="timeline">'
        for hour in range(start_hour, end_hour + 1):
            html_content += f'<div>{hour}:00</div>'
        html_content += '</div>'

        html_content += "</div></div>"

    html_content += "</div></body></html>"

    # Save HTML file
    file_path = "monthly_schedule.html"
    with open(file_path, "w") as file:
        file.write(html_content)

    # Open file in browser
    webbrowser.open(f"file:///{os.path.abspath(file_path)}")


if __name__ == "__main__":
    main("2025-03", "Store 101") """