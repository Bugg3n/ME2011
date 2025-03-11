import matplotlib.pyplot as plt
import numpy as np

# Schedule data
schedule = [
    {'start': '9:00', 'end': '17:00', 'lunch': 'TBD'},
    {'start': '11:00', 'end': '19:00', 'lunch': 'TBD'},
    {'start': '14:00', 'end': '22:00', 'lunch': 'TBD'},
    {'start': '17:00', 'end': '20:00', 'lunch': 'TBD'}
]

# Convert time to float (e.g., '9:00' -> 9.0)
def time_to_float(time_str):
    h, m = map(int, time_str.replace(':', '.').split('.'))
    return h + m / 60

# Extract shift details
shift_labels = [f"Shift {i+1}" for i in range(len(schedule))]
shift_start = [time_to_float(shift['start']) for shift in schedule]
shift_end = [time_to_float(shift['end']) for shift in schedule]
shift_duration = [end - start for start, end in zip(shift_start, shift_end)]

# Create figure
fig, ax = plt.subplots(figsize=(8, 5))

# Plot each shift as a horizontal bar
y_positions = np.arange(len(schedule))
ax.barh(y_positions, shift_duration, left=shift_start, height=0.6, color='skyblue', edgecolor='black')

# Add labels
ax.set_yticks(y_positions)
ax.set_yticklabels(shift_labels)
ax.set_xlabel("Time")
ax.set_title("Work Schedule Visualization")

# Set x-axis to display time labels
time_labels = np.arange(8, 23, 1)  # Time from 8:00 to 22:00
ax.set_xticks(time_labels)
ax.set_xticklabels([f"{int(t)}:00" for t in time_labels])

plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.show()
