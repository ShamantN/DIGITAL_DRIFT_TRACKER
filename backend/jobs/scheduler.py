import schedule
import time
import subprocess
import os
import sys

# Add parent directory to path to import database module
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(script_dir))

from database import get_db_connection

def get_all_user_ids():
    """Get all user IDs from the database."""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return []
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT uid FROM user ORDER BY uid")
        user_ids = [row[0] for row in cursor.fetchall()]
        return user_ids
    except Exception as e:
        print(f"Error fetching user IDs: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def run_drift_analysis_job():
    """Runs the drift analysis script for all users."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting drift analysis job...")
    
    # Get all user IDs from database
    user_ids = get_all_user_ids()
    
    if not user_ids:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No users found in database")
        return
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Found {len(user_ids)} users to analyze")
    
    # Run drift analysis for each user
    for user_id in user_ids:
        try:
            result = subprocess.run(["python", os.path.join(script_dir, "run_drift_analysis.py"), "--user", str(user_id)], 
                                    capture_output=True, text=True, check=True)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Drift analysis completed for user {user_id}")
        except subprocess.CalledProcessError as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error in drift analysis for user {user_id}: {e}")
            print(f"Stderr: {e.stderr}")
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Drift analysis job finished.")

def run_daily_summary_job():
    """Runs the daily summary script for all users."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting daily summary job...")
    # Run for today's date - the script now handles all users internally
    try:
        result = subprocess.run(["python", os.path.join(script_dir, "run_daily_summary.py")], 
                                capture_output=True, text=True, check=True)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Daily summary output: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error in daily summary: {e}")
        print(f"Stderr: {e.stderr}")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Daily summary job finished.")

if __name__ == "__main__":
    # Schedule the jobs - updated for more frequent testing
    schedule.every(30).seconds.do(run_drift_analysis_job)  # Every 30 seconds for testing
    schedule.every(1).minute.do(run_daily_summary_job)     # Every 1 minute for testing

    print("Scheduler started. Running pending jobs...")
    
    # Run any pending jobs immediately
    schedule.run_pending()
    
    # Main scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(1)