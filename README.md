# 🩺 CareU – Health & Wellness Analytics Platform  
**Final Sprint 3 – Software Engineering Project**  
*Concordia University*  
**Course:** COEN 6311 – Software Engineering  
**Team Members:**  
- **Anas El Fali** 
- **Mikelange Ngakala**
- **Rafsan Khan**
- **Aarti Aarti**
- **Mohamad Jawad** 

---

## 🚀 Overview

**CareU** is a Django-based web platform designed to help users track and visualize their daily health data — including **nutrition**, **sleep**, **activity**, **glucose levels**, and **health goals**.  
It integrates multiple modules such as **User Management**, **Analytics Dashboard**, **Home Dashboard**, **Reminders**, and **Proactive AI Recommendations**, creating a comprehensive and intelligent health-tracking ecosystem.

**Sprint 3** focuses on:
- ✅ **Interactive Home Dashboard** with real-time health metrics (Steps, Heart Rate, Goals)
- ✅ **Enhanced Data Management** with improved data loading scripts
- ✅ **Nutrition Dashboard Refinements** with week-view navigation
- ✅ **Consistent UI/UX** across all modules with iOS-inspired design
- ✅ **Comprehensive Testing** with demo data scripts for all features

---

## 🧩 Project Structure

```
CareU/
├── analytics/                    # Data visualization & health insights
│   ├── management/commands/
│   │   └── load_demo_analytics.py    # Loads glucose, sleep, steps data
│   ├── templates/analytics/
│   │   ├── analytics_dashboard.html
│   │   ├── _cards.html
│   │   └── insights.html
│   ├── models.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
│
├── healthdata/                   # Core health data models
│   ├── migrations/
│   ├── templates/healthdata/
│   │   ├── nutrition_dashboard.html
│   │   ├── goal_dashboard.html
│   │   └── reminders_dashboard.html
│   ├── models.py                # ActivityData, HealthMetrics, Goal, NutritionEntry
│   ├── views.py
│   └── urls.py
│
├── ai_agent/                     # AI-powered chat assistant
│   └── services.py              # Google Gemini integration
│
├── proactive_feat/              # Proactive health monitoring
│   ├── templates/proactive_feat/
│   │   └── home_dashboard.html
│   └── views.py
│
├── usermanagement/              # User authentication & profiles
│   ├── models.py
│   └── views.py
│
├── static/                      # Global CSS, JS, images
│   ├── css/
│   ├── js/
│   └── img/
│
├── add_test_data.py            # 🔥 NEW: Loads home dashboard demo data
├── manage.py
├── requirements.txt
└── db.sqlite3
```

---

## 🧠 Features Implemented in Sprint 3

### ✅ Interactive Home Dashboard
- **Real-time Health Metrics**: Display today's steps, current heart rate, and active goals
- **Visual Progress Indicators**: Circular charts using Chart.js for steps and heart rate
- **Goal Tracking**: Shows latest active goal with progress and quick access link
- **Quick Access Navigation**: One-click access to all major features

### ✅ Enhanced Data Management
- **Improved Data Loading**: Two specialized scripts for comprehensive demo data
  - `add_test_data.py` - Loads ActivityData, HealthMetrics, and Goals
  - `load_demo_analytics.py` - Loads historical analytics data (14 days)
- **Duplicate Prevention**: Smart data handling to prevent duplicate records
- **Flexible Updates**: Scripts can update existing data or create new entries

### ✅ Nutrition Dashboard Improvements
- **Week View Navigation**: Browse nutrition data day-by-day with visual calendar
- **Daily Totals**: Aggregate calories, protein, carbs, and fat per selected day
- **Data Indicators**: Visual dots show which days have logged entries
- **Improved Action Buttons**: Professional grouped Edit/Delete buttons
- **CSV Import**: Bulk upload nutrition data from CSV files

### ✅ Analytics Dashboard
- **Interactive Visualizations**: Glucose, Sleep, and Steps trends over time
- **Health Insights**: AI-powered highlights for unusual patterns
- **Flexible Time Ranges**: View data for 7, 14, or 30 days
- **REST API Endpoint**: JSON data accessible at `/analytics/charts/data/`

### ✅ UI/UX Enhancements
- **Consistent Navigation**: 80px left sidebar across all dashboards
- **iOS-Inspired Design**: Clean, modern interface with rounded corners
- **Responsive Layout**: Works seamlessly on desktop and mobile devices
- **Professional Color Scheme**: Blue (#007AFF), Green (#34C759), Red (#FF3B30)

---

## 💡 Demo Data Commands

### 🏠 Load Home Dashboard Data
Populates today's steps, heart rate, and active goal for immediate testing:

```bash
python add_test_data.py
```

**What it loads:**
- ✅ ActivityData: 7,500 steps for today
- ✅ HealthMetrics: Resting heart rate of 68 bpm
- ✅ Goal: "Walk 10,000 steps daily" (active)

**Output:**
```
✅ Adding test data for user: anas_test
📊 Processing ActivityData...
✅ ActivityData: Created - 7500 steps
❤️  Processing HealthMetrics...
✅ HealthMetrics: Updated - 68 bpm
🎯 Processing Goals...
✅ Goal: Updated - Walk 10,000 steps daily
🎉 Test data added successfully!
```

### 📊 Load Analytics Dashboard Data
Populates 14 days of historical health data for charts and insights:

```bash
python manage.py load_demo_analytics
```

**What it loads:**
- ✅ 14 days of glucose readings (100-180 mg/dL range)
- ✅ 14 days of sleep data (5.5-8.5 hours range)
- ✅ 14 days of activity data (5,000-12,000 steps range)

---

## 🧪 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home dashboard with health metrics |
| `/dashboard/` | GET | Alternative home dashboard route |
| `/analytics/` | GET | Analytics dashboard with charts |
| `/analytics/charts/data/?days=14` | GET | JSON data for glucose, sleep, steps |
| `/analytics/insights/` | GET | Health highlights and patterns |
| `/analytics/insights/fragment/` | GET | Partial template for dashboard widgets |
| `/nutrition/` | GET | Nutrition tracking dashboard |
| `/nutrition/import/` | POST | CSV import endpoint |
| `/goals/` | GET | Goals management dashboard |
| `/reminders/` | GET | Health reminders dashboard |
| `/chats/` | GET | AI chat assistant |

### 📄 Example JSON Response (`/analytics/charts/data/?days=7`)

```json
{
  "labels": ["Nov 15", "Nov 16", "Nov 17", "Nov 18", "Nov 19", "Nov 20", "Nov 21"],
  "glucose": [120, 135, 128, 145, 138, 132, 125],
  "sleep": [7.2, 6.8, 7.5, 6.3, 7.8, 7.1, 6.9],
  "steps": [8900, 10200, 7600, 9400, 11200, 8700, 7500]
}
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/CareU.git
cd CareU
```

### 2️⃣ Create a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply database migrations
```bash
python manage.py migrate
```

### 5️⃣ Create a superuser (optional)
```bash
python manage.py createsuperuser
```

### 6️⃣ Load demo data

**Option A: Load ALL demo data (recommended for testing)**
```bash
# Load home dashboard data (steps, heart rate, goals)
python add_test_data.py

# Load analytics data (14 days of glucose, sleep, activity)
python manage.py load_demo_analytics
```

**Option B: Load specific data only**
```bash
# Just home dashboard
python add_test_data.py

# OR just analytics
python manage.py load_demo_analytics
```

### 7️⃣ Run the development server
```bash
python manage.py runserver
```

Now visit **http://127.0.0.1:8000** to access the platform! 🎉

---

## 🖥️ Key Pages

| Page | URL | Description |
|------|-----|-------------|
| Home Dashboard | `/` | Overview with steps, heart rate, goals |
| Analytics | `/analytics/` | Charts for glucose, sleep, steps |
| Nutrition | `/nutrition/` | Track meals and daily nutrition |
| Goals | `/goals/` | Set and monitor health goals |
| Reminders | `/reminders/` | AI-generated health reminders |
| AI Chat | `/chats/` | Conversational health assistant |

---

## 🎯 Testing the Application

### Home Dashboard
1. Navigate to `/` or `/dashboard/`
2. Verify you see:
   - ✅ Steps Today: 7,500 steps (with circular chart)
   - ✅ Heart Rate: 68 bpm (with circular chart)
   - ✅ Latest Goal: "Walk 10,000 steps daily"

### Analytics Dashboard
1. Navigate to `/analytics/`
2. Verify three line charts appear:
   - 📊 Glucose trend (14 days)
   - 😴 Sleep duration (14 days)
   - 👟 Daily steps (14 days)
3. Test the time range selector (7, 14, 30 days)

### Nutrition Dashboard
1. Navigate to `/nutrition/`
2. Use the week view to browse different days
3. Add a nutrition entry using the form
4. Verify totals update correctly

---

## 🛠️ Troubleshooting

### Issue: Home dashboard shows 0 values
**Solution:**
```bash
# Run the home data loading script
python add_test_data.py
```

### Issue: Analytics charts are empty
**Solution:**
```bash
# Run the analytics data loading script
python manage.py load_demo_analytics
```

### Issue: Duplicate data entries
**Solution:** The `add_test_data.py` script automatically handles duplicates by deleting existing entries for today before creating new ones.

### Issue: Charts not rendering
**Solution:** 
1. Clear browser cache (Ctrl+Shift+Del)
2. Ensure Chart.js is loading (check browser console)
3. Restart the Django server

---

## 🎨 Design System

### Color Palette
- **Primary Blue**: `#007AFF` - Main actions and active states
- **Success Green**: `#34C759` - Positive metrics and achievements
- **Warning Orange**: `#FF9500` - Alerts and notifications
- **Danger Red**: `#FF3B30` - Critical alerts and delete actions
- **Background**: `#F2F2F7` - Light gray for page backgrounds
- **Card White**: `#FFFFFF` - Card and component backgrounds
- **Text Primary**: `#1C1C1E` - Main text color
- **Text Secondary**: `#8E8E93` - Subtle text and labels

### Typography
- **Font Family**: `Inter, -apple-system, BlinkMacSystemFont, sans-serif`
- **Card Radius**: `16px` for consistent rounded corners
- **Sidebar Width**: `80px` for consistent navigation

---

## 📚 Technologies Used

- **Backend**: Django 5.2.6, Python 3.x
- **Frontend**: Bootstrap 5.3, Chart.js 4.x, HTML5, CSS3
- **Database**: SQLite (development), PostgreSQL-ready
- **AI Integration**: Google Gemini API (for chat and insights)
- **Charts**: Chart.js with custom doughnut and line charts
- **Icons**: Custom SVG icons for navigation

---

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is developed as part of Concordia University's Software Engineering course (COEN 6311).

---

## 🙏 Acknowledgments

- Concordia University Department of Computer Science and Software Engineering
- Course Instructor: Dr. [Instructor Name]
- Google Gemini API for AI capabilities
- Bootstrap and Chart.js communities for excellent documentation

---

**Built with ❤️ by the AMMAR Team**  
*Making healthcare data accessible and actionable for everyone*