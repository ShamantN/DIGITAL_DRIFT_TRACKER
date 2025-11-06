# How to Generate Drift Events

Drift events are **automatically detected** by analyzing your browsing activity. Here's how it works:

## 📋 Process Overview

1. **Browse normally** with the extension installed → Activity is collected
2. **Run the drift analysis script** → Detects drift patterns
3. **View results** in the dashboard → See detected drifts

## 🚀 Quick Start

### Step 1: Ensure Extension is Running

1. Open Chrome and go to `chrome://extensions/`
2. Make sure "Digital Drift Tracker" is enabled
3. Open DevTools (F12) → Console tab
4. Look for: `Session started: <number>`

### Step 2: Generate Activity (Choose One Method Below)

#### Method A: Unproductive Shift (Easiest)

1. Visit a **productive** site first:
   - `github.com`
   - `stackoverflow.com`
   - `wikipedia.org`
   - Move mouse, scroll, wait 10-20 seconds

2. Then visit an **unproductive** site:
   - `youtube.com`
   - `facebook.com`
   - `reddit.com`
   - `twitter.com`
   
   **Result:** The system detects you shifted from productive → unproductive

#### Method B: Idle/Away Drift

1. Visit any website
2. **Stop all activity** for 5+ minutes (no mouse movement, clicks, or scrolling)
3. Move mouse or click again

   **Result:** System detects you were idle for 5+ minutes

#### Method C: Rapid Tab Switching

1. Open 5+ tabs
2. Quickly switch between them (click through tabs rapidly within 30 seconds)

   **Result:** System detects rapid tab switching behavior

#### Method D: Unproductive Loop

1. Visit the same unproductive site (youtube, reddit, etc.) 3+ times
2. Navigate away, then come back repeatedly

   **Result:** System detects you're looping on unproductive content

### Step 3: Run Drift Analysis

After generating activity, run the analysis script:

```bash
# Navigate to backend directory
cd "d:\5TH SEM\DBMS\DBMS_PROJECT\backend"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run analysis (analyzes last 24 hours by default)
python jobs\run_drift_analysis.py

# Or analyze a specific session
python jobs\run_drift_analysis.py --session-id 1

# Or analyze last 1 hour
python jobs\run_drift_analysis.py --hours 1
```

**Expected Output:**
```
Found 1 active sessions to analyze...

Analyzing 45 events for session 1...
  ✓ Detected Unproductive Shift: Shifted from productive to Unproductive domain: youtube.com
✓ Analysis complete for session 1
```

### Step 4: View Results

1. **In Dashboard:**
   - Open `http://localhost:3000`
   - Check the "Recent Drift Events" table
   - View charts showing drift timeline

2. **In Extension Popup:**
   - Click the extension icon
   - See recent drifts listed

3. **In Database:**
   ```sql
   SELECT * FROM drift_event ORDER BY event_start DESC LIMIT 10;
   ```

## 🔍 Domain Categories

For drift detection to work, domains must have categories set:

- **Productive:** `github.com`, `stackoverflow.com`, `wikipedia.org`
- **Unproductive:** `youtube.com`, `reddit.com`, `facebook.com`
- **Social Media:** Automatically categorized
- **Entertainment:** Automatically categorized

**Note:** If you visit a site for the first time, it defaults to "Neutral". You can update categories via the API or database.

## ⚙️ Automatic Detection Types

The system detects these drift types:

1. **Unproductive Shift** - Moving from productive → unproductive site
2. **Idle / Away** - No activity for 5+ minutes
3. **Rapid Tab Switching** - 5+ tab switches in 30 seconds
4. **Unproductive Loop** - Revisiting same unproductive site 3+ times

## 💡 Tips

- **Generate enough activity first** - Visit multiple sites, interact with pages
- **Wait for events to batch** - Events are sent every 30 seconds or 20 events
- **Run analysis regularly** - Run `run_drift_analysis.py` every few minutes for testing
- **Check session ID** - Use the session ID from extension console in analysis

## 🐛 Troubleshooting

**No drifts detected?**
- Make sure you have activity events: `SELECT COUNT(*) FROM activity_event;`
- Check domain categories: `SELECT * FROM domains WHERE user_id = 1;`
- Verify session exists: `SELECT * FROM sessions WHERE sid = 1;`

**Extension not tracking?**
- Check extension console for errors
- Verify backend is running at `http://127.0.0.1:8000`
- Check that you're visiting `http://` or `https://` URLs (not chrome://)

**Analysis script errors?**
- Ensure database connection works: Check `backend/.env` file
- Verify tables exist: `SHOW TABLES;`
- Check Python dependencies are installed

## 📅 Scheduling Analysis

To run analysis automatically, you can:

**Windows (Task Scheduler):**
```powershell
# Create a scheduled task that runs every 15 minutes
python "d:\5TH SEM\DBMS\DBMS_PROJECT\backend\jobs\run_drift_analysis.py"
```

**Linux/Mac (Cron):**
```bash
# Add to crontab (runs every 15 minutes)
*/15 * * * * cd /path/to/backend && python jobs/run_drift_analysis.py
```

---

**That's it!** Browse normally, run the analysis script, and drift events will be detected and stored in your database.

