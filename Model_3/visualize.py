
import matplotlib.pyplot as plt
import numpy as np

# Input data
data = {
    'day': '2025-01-22',
    'store_id': '1',
    'opening_hours': ['08:00', '21:00'],
    'staffing_per_hour': {
        '8:00': 0, '9:00': 1, '10:00': 1, '11:00': 2, '12:00': 2, '13:00': 2,
        '14:00': 3, '15:00': 3, '16:00': 3, '17:00': 3, '18:00': 2, '19:00': 2,
        '20:00': 1, '21:00': 1
    },
    'shift_suggestions': [
        {'start': '8:00', 'end': '9:00', 'staff_needed': 0},
        {'start': '9:00', 'end': '11:00', 'staff_needed': 1},
        {'start': '11:00', 'end': '14:00', 'staff_needed': 2},
        {'start': '14:00', 'end': '18:00', 'staff_needed': 3},
        {'start': '18:00', 'end': '20:00', 'staff_needed': 2},
        {'start': '20:00', 'end': '22:00', 'staff_needed': 1}
    ],
    'metadata': {'delivery_day': True}
}

# Convert time to numerical format (hours as floats)
def time_to_float(time_str):
    h, m = map(int, time_str.replace(':', '.').split('.'))
    return h + m / 60

# Extract shift information
shifts = data['shift_suggestions']
opening_time = time_to_float(data['opening_hours'][0])
closing_time = time_to_float(data['opening_hours'][1])

# Create figure and axis
fig, ax = plt.subplots(figsize=(8, 6))

# Generate shift bars
for shift in shifts:
    start = time_to_float(shift['start'])
    end = time_to_float(shift['end'])
    staff = shift['staff_needed']
    
    ax.barh(y=staff, width=end-start, left=start, height=0.5, align='center', color='skyblue', edgecolor='black')

# Labels and formatting
ax.set_xlabel('Time')
ax.set_ylabel('Staff Needed')
ax.set_title(f"Shift Schedule for {data['day']}")
ax.set_xticks(np.arange(opening_time, closing_time + 1, 1))
ax.set_xticklabels([f"{int(t)}:00" for t in np.arange(opening_time, closing_time + 1, 1)])
ax.set_yticks(range(4))
ax.set_yticklabels(range(4))

plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.show()






