import sqlite3

# Connect to the database
conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

# Fetch all employees
cursor.execute("SELECT * FROM employees")
rows = cursor.fetchall()

# Print employee data
for row in rows:
    print(row)

# Close connection
conn.close()