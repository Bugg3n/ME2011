# 📅 Work Schedule Optimizer

This tool is developed as part of a master thesis project by **Hugo Westergård** and **Oscar**. It helps retail companies create optimal monthly employee schedules. The tool considers customer flow, employee preferences, and queueing theory to balance workload and ensure proper staffing.

## 👨‍🎓 Thesis Context

This project is a master thesis in Industrial Engineering and Management, focused on optimizing staff scheduling with both operational efficiency and employee satisfaction in mind.

---

## 🚀 Features

- Optimal monthly scheduling based on customer flow and queueing theory
- Handles employee preferences (early/late shifts, weekend preferences, availability, overtime)
- Smart manager shift allocation logic
- Web-based dashboard for visualizing the schedule and coverage
- Exports:
  - ✅ HTML dashboards for visualization
  - ✅ JSON files for structured storage
  - ✅ CSV files for external analysis

---

## 🛠 Installation

1. **Clone the repository**
2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Make sure `employees.db` exists** in the root folder. 
If it does not exist, you can create it by running Model_3/create_employees.py

---

## ▶️ How to Run

```bash
python main.py
```

This will:
- Generate monthly staffing needs (Model 1)
- Create shift schedules (Model 2)
- Assign employees to shifts (Model 3)
- Launch a web server at `http://localhost:8000`

---

## 📁 Folder Structure

```
.
├── main.py
├── employees.db
├── README.md
├── requirements.txt

├── Analysis/
│   ├── analyze_employees.py
│   └── visualize2.py

├── csv-files/
│   └── final_schedule_YYYY_MM.csv       # Exported monthly shift data

├── HTML-files/
│   └── monthly_schedule.html            # Dashboard
│   └── employee_summary.html            # Employee statistics

├── Model_1/
│   └── model1.py

├── Model_2/
│   └── model2.py

├── Model_3/
│   ├── model3.py
│   ├── employees.py
│   ├── read_database.py
│   └── create_employees.py

├── Schedules/
│   └── final_schedule_YYYY_MM.json      # Monthly schedule in JSON format

├── web-output/
│   └── model2_shifts_YYYY-MM-DD.json    # Daily shift suggestions (used by frontend)

└── Webserver/
    └── webserver.py
```

---

## ⚙️ Customization

You can adjust these in `main.py`:

```python
YEAR = 2025
MONTH = 2
SALES_CAPACITY = 12
CUSTOMER_FLOW_PER_HOUR = [...]
DEBUG = False
MAX_DAILY_HOURS = 10
```

---

## ✅ Requirements

See `requirements.txt`:

```
pandas
numpy
scipy
matplotlib
```

---

## 📊 Outputs

- `monthly_schedule.html` – main schedule overview
- `employee_summary.html` – employee statistics
- `final_schedule_YYYY_MM.json` – assigned shifts (per employee)
- `final_schedule_YYYY_MM_by_date.json` – assigned shifts (per day)
- `final_schedule_YYYY_MM.csv` – CSV export for analysis
- `model2_shifts_YYYY-MM-DD.json` – shift suggestions for each day

---

## 🌐 View in Browser

After running the program, the browser will open automatically to:

```
http://localhost:8000
```

Here, you can:
- Interact with the schedule
- Update parameters
- View employee stats
