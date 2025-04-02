# 📅 Work Schedule Optimizer

This Python-based tool helps retail companies create optimal monthly employee schedules. It balances store staffing needs with employee preferences (like early/late shifts and weekend availability), while also using queueing theory to estimate demand and avoid under/over-staffing.

## 🚀 Features

- Optimal monthly scheduling based on customer flow and queueing theory
- Handles employee preferences (early/late, weekends, availability, overtime)
- Manager assignment logic
- Web-based interactive dashboard for visualizing schedules and metrics
- Generates employee statistics and staffing summary

---

## 🛠 Installation

1. **Clone the repository**
2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Make sure `employees.db` exists** with employee data.
Otherwise, use create_employees.db to create them.

---

## ▶️ How to Run

```bash
python main.py
```

This will:
- Generate monthly staffing needs (Model 1)
- Create shift schedules (Model 2)
- Assign employees to shifts (Model 3)
- Launch a local web server at `http://localhost:8000` to view the results

The output includes:
- `monthly_schedule.html` — main web dashboard
- `final_schedule_YYYY_MM.json` — assigned shifts
- `employee_summary.html` — employee statistics
- Visual graphs and shift visualizations in your browser

---

## ⚙️ Customization

You can tweak the following variables in `main.py`:

```python
YEAR = 2025
MONTH = 2
SALES_CAPACITY = 12
CUSTOMER_FLOW_PER_HOUR = [...]
DEBUG = False
MAX_DAILY_HOURS = 10
```

---

## 📁 Project Structure

```
├── main.py                # Main entrypoint
├── model1.py              # Staffing requirements (queueing theory)
├── model2.py              # Shift generation logic
├── model3.py              # Employee assignment logic
├── employees.py           # Employee object and DB integration
├── analyze_employees.py   # Analysis and summary reports
├── visualize2.py          # HTML generation and visualization
├── webserver.py           # Local web server
├── requirements.txt       # Required Python packages
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
