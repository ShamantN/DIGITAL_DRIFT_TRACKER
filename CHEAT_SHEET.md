# Digital Drift Tracker - Quick Command Cheat Sheet

## 🚀 Start Everything

### Terminal 1: Backend
```bash
cd "d:\5TH SEM\DBMS\DBMS_PROJECT\backend"
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

### Terminal 2: Dashboard
```bash
cd "d:\5TH SEM\DBMS\DBMS_PROJECT\dashboard"
npm start
```

### Terminal 3: Test
```bash
cd "d:\5TH SEM\DBMS\DBMS_PROJECT\backend"
.\venv\Scripts\Activate.ps1
python jobs\simulate_activity.py
```

## 📍 Important URLs

| Service | URL |
|---------|-----|
| Backend API | http://127.0.0.1:8000 |
| API Docs (Swagger) | http://127.0.0.1:8000/docs |
| API Docs (ReDoc) | http://127.0.0.1:8000/redoc |
| Dashboard | http://localhost:3000 |
| Chrome Extensions | chrome://extensions/ |

## 🔧 Common Commands

### Backend
```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Start server
uvicorn main:app --reload

# Test simulation
python jobs\simulate_activity.py

# Run drift analysis
python jobs\run_drift_analysis.py

# Run daily summary
python jobs\run_daily_summary.py
```

### Dashboard
```bash
# Install (first time only)
npm install

# Start dev server
npm start

# Build for production
npm run build
```

## ⚙️ Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| .env | Database config | `backend\.env` |
| manifest.json | Extension config | `extension\manifest.json` |
| package.json | Node dependencies | `dashboard\package.json` |
| requirements.txt | Python dependencies | `backend\requirements.txt` |

## 🗄️ Database

```sql
-- Check database
USE ddt;
SHOW TABLES;

-- View users
SELECT * FROM user;

-- View sessions
SELECT * FROM sessions;

-- View drifts
SELECT * FROM drift_event ORDER BY event_start DESC;

-- View activity
SELECT * FROM activity_event ORDER BY timestamp DESC LIMIT 10;
```

## 🐛 Troubleshooting

```bash
# Check if MySQL is running (Windows)
net start MySQL80

# Check Python version
python --version

# Check Node version
node --version

# Reinstall backend dependencies
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Reinstall dashboard dependencies
cd dashboard
npm install
```

## 📊 File Locations

```
backend\           ← Python backend
├── main.py       ← Start here
├── database.py   ← DB connection
└── jobs\         ← Analysis scripts

dashboard\         ← React frontend
├── src\
│   ├── App.js    ← Main app
│   └── components\  ← Charts & UI

extension\         ← Chrome extension
├── manifest.json
├── background.js  ← Main logic
└── popup\         ← UI

database\          ← SQL files
├── ddt_schema.sql
└── project_tpf.sql
```

## 🎯 Success Indicators

✅ **Backend**: Terminal shows "Uvicorn running on http://127.0.0.1:8000"  
✅ **Dashboard**: Browser shows charts and data  
✅ **Extension**: Icon visible in Chrome toolbar  
✅ **Database**: Has test data in tables  
✅ **API**: http://127.0.0.1:8000/docs loads successfully  

## 🔗 Useful Links

- [Full README](README.md)
- [Quick Start Guide](QUICK_START.md)
- [Project Summary](PROJECT_SUMMARY.md)
- [Start Here](START_HERE.md)
- [Implementation Checklist](IMPLEMENTATION_CHECKLIST.md)

---

**Keep this file open for quick reference!** 📝

