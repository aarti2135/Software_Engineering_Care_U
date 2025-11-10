# 🩺 CareU – Health & Wellness Analytics Platform  
**Final Sprint 2 – Software Engineering Project**  
*Concordia University 
**Course:** COEN 6311 – Software Engineering  
**Team Members:**  
- **Anas El Fali** 
- **Mikelange Ngakala**
- **Rafsan Khan**
- **Aarti Aarti**
- **Mohamad Jawad** 

---

## 🚀 Overview

**CareU** is a Django-based web platform designed to help users track and visualize their daily health data — including **nutrition**, **sleep**, **activity**, and **glucose levels**.  
It integrates multiple modules such as **User Management**, **Analytics Dashboard**, **Reminders**, and **Proactive AI Recommendations**, creating a comprehensive and intelligent health-tracking ecosystem.

This final sprint focused on:
- Adding a fully functional **Analytics Dashboard** (Glucose, Sleep, Steps)  
- Improving **UI consistency** across all dashboards  
- Enhancing **project structure** and **documentation clarity**  

---

## 🧩 Project Structure

care_u/
├── analytics/ # App for data visualization & health insights
│ ├── management/commands/ # Custom command: load_demo_analytics
│ ├── migrations/
│ ├── templates/analytics/
│ │ ├── analytics_dashboard.html
│ │ ├── _cards.html
│ │ └── insights.html
│ ├── models.py
│ ├── services.py
│ ├── urls.py
│ └── views.py
│
├── healthdata/ # Core data models: Glucose, Sleep, Activity
├── proactive_feat/ # AI-powered proactive health suggestions
├── usermanagement/ # Handles authentication & profile data
├── static/ # Global static files (CSS, JS, images)
├── templates/ # Shared HTML layouts
├── manage.py
└── db.sqlite3


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/CareU.git
cd CareU

### 2️⃣ Create a virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# or
source .venv/bin/activate   # macOS/Linux

### 3️⃣ Install dependencies
pip install -r requirements.txt

### 4️⃣ Apply migrations
python manage.py migrate

### 5️⃣ (Optional) Load demo analytics data
python manage.py load_demo_analytics

### 6️⃣ Run the Django development server
python manage.py runserver


Now visit http://127.0.0.1:8000
 to access the platform.

------------------------------------------------

##🧠 Features Implemented in Final Sprint 2
✅ Analytics Dashboard

Interactive visualizations for Glucose, Sleep, and Steps

Uses Chart.js for dynamic front-end rendering

REST-style JSON endpoint at /analytics/charts/data/

Consistent UI matching the Reminders Dashboard

✅ Structural Improvements

Clear project hierarchy between apps (analytics, healthdata, usermanagement)

Added management/commands/load_demo_analytics.py for seeding test data

Simplified imports using apps.get_model() to prevent circular dependencies

✅ UI Enhancements

Sidebar navigation consistent with all dashboards

New “View Analytics Dashboard” button on home page

Fully responsive layouts with Bootstrap 5.3

✅ Technical Documentation

Expanded inline comments across models and views

Added API endpoint list with usage examples

Updated README for setup, data loading, and screenshots
--------------------------------------------
##🧪 API Endpoints
Endpoint	Method	Description
/analytics/	GET	Renders Analytics Dashboard
/analytics/charts/data/?days=14	GET	Returns JSON containing glucose, sleep, and step data
/analytics/insights/	GET	Displays health highlights (e.g., low sleep, high glucose)
/analytics/insights/fragment/	GET	Partial template rendering for dashboard widgets
/analytics/insights/dismiss/	POST	Dismisses a highlight for 48 hours
-----------------------------------------------
Example JSON Response:

{
  "labels": ["Nov 01", "Nov 02", "Nov 03"],
  "glucose": [160, 145, 170],
  "sleep": [6.5, 7.1, 5.8],
  "steps": [8900, 7600, 10200]
}
-----------------------------------------------
##💡 Demo Data Command

To easily populate your database with realistic demo entries:

python manage.py load_demo_analytics
-----------------------------------------------
