#!/usr/bin/env python3
"""
Drift Analysis Script
Analyzes activity events to detect various types of drift behavior.
Run this script periodically (e.g., via cron) to detect drifts from recent activity.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import database module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def analyze_drifts_for_session(session_id):
    """Analyze a specific session for drift events."""
    conn = get_db_connection()
    if not conn:
        print(f"Failed to connect to database for session {session_id}")
        return
    
    cursor = conn.cursor()
    
    try:
        # Get user_id for this session
        cursor.execute("SELECT user_id FROM sessions WHERE sid = %s", (session_id,))
        session_result = cursor.fetchone()
        if not session_result:
            print(f"No session found with ID {session_id}")
            return
        user_id = session_result[0]
        
        # Get all activity events for this session, ordered by timestamp
        query = """
            SELECT 
                ae.event_id, ae.user_id, ae.tab_id, ae.event_type, 
                ae.timestamp, ae.url,
                d.domain_name, d.category
            FROM activity_event ae
            JOIN tab t ON ae.tab_id = t.tid
            JOIN domains d ON t.domain_id = d.id
            WHERE ae.session_id = %s
            ORDER BY ae.timestamp ASC
        """
        cursor.execute(query, (session_id,))
        events = cursor.fetchall()
        
        if not events:
            print(f"No events found for session {session_id}")
            return
        
        # Convert to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        events = [dict(zip(columns, row)) for row in events]
        
        # State tracking
        last_category = None
        last_event_time = None
        last_event = None
        tab_switches = []  # Track recent tab switches
        
        print(f"Analyzing {len(events)} events for session {session_id}...")
        
        # First, run the 4 new drift type analyses
        analyze_focus_breaks(cursor, user_id, session_id, events)
        analyze_drift_triggers(cursor, user_id, session_id, events)
        analyze_search_to_unproductive(cursor, user_id, session_id, events)
        analyze_task_abandonment(cursor, user_id, session_id, events)
        
        # Then run the existing analyses
        for i, event in enumerate(events):
            event_time = event['timestamp']
            event_type = event['event_type']
            domain_category = event['category'] or 'Neutral'
            
            # 1. Detect Unproductive Shift
            if event_type in ('TAB_FOCUS', 'URL_CHANGE'):
                if last_category == 'Productive' and domain_category in ('Unproductive', 'Social Media', 'Entertainment'):
                    # Create drift event
                    description = f"Shifted from productive to {domain_category} domain: {event['domain_name']}"
                    insert_drift(cursor, session_id, last_event['timestamp'], event_time, 
                                'Unproductive Shift', description, 'LOW', event['tab_id'])
                    print(f"  ✓ Detected Unproductive Shift: {description}")
                
                last_category = domain_category
            
            # 2. Detect Idle/Away (5+ minutes gap)
            if last_event_time:
                time_diff = (event_time - last_event_time).total_seconds()
                if time_diff > 300:  # 5 minutes = 300 seconds
                    minutes_idle = int(time_diff / 60)
                    description = f"User idle for {minutes_idle} minutes"
                    insert_drift(cursor, session_id, last_event_time, event_time,
                                'Idle / Away', description, 'LOW', None)
                    print(f"  [OK] Detected Idle/Away: {description}")
            
            # 3. Track tab switches for rapid switching detection
            if event_type == 'TAB_FOCUS':
                tab_switches.append(event_time)
                # Keep only last 30 seconds of switches
                tab_switches = [ts for ts in tab_switches if (event_time - ts).total_seconds() <= 30]
                
                # Detect Rapid Tab Switching (5+ switches in 30 seconds)
                if len(tab_switches) >= 5:
                    description = f"Rapidly switched between {len(tab_switches)} tabs in 30 seconds"
                    insert_drift(cursor, session_id, tab_switches[0], event_time,
                                'Rapid Tab Switching', description, 'MODERATE', event['tab_id'])
                    print(f"  [OK] Detected Rapid Tab Switching: {description}")
                    tab_switches = []  # Reset after detection
            
            # 4. Detect Unproductive Loop (revisiting same unproductive domains)
            # This requires more complex tracking - simplified version here
            if domain_category in ('Unproductive', 'Social Media', 'Entertainment'):
                # Check if we've seen this domain recently (within last 10 minutes)
                recent_unproductive = [e for e in events[max(0, i-20):i] 
                                     if e.get('domain_name') == event['domain_name'] 
                                     and e.get('category') in ('Unproductive', 'Social Media', 'Entertainment')]
                if len(recent_unproductive) >= 3:  # Visited same site 3+ times
                    description = f"Repeatedly visited {event['domain_name']} ({len(recent_unproductive)+1} times)"
                    insert_drift(cursor, session_id, recent_unproductive[0]['timestamp'], event_time,
                                'Unproductive Loop', description, 'MODERATE', event['tab_id'])
                    print(f"  [OK] Detected Unproductive Loop: {description}")
            
            last_event_time = event_time
            last_event = event
        
        conn.commit()
        print(f"[OK] Analysis complete for session {session_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error analyzing session {session_id}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def insert_drift(cursor, session_id, event_start, event_end, drift_type, description, severity, tab_id=None, event_meta=None):
    """Insert a drift event into the database."""
    # Calculate duration in seconds
    duration = int((event_end - event_start).total_seconds())
    
    # Check if this drift already exists (avoid duplicates)
    check_query = """
        SELECT drift_id FROM drift_event 
        WHERE session_id = %s 
        AND drift_type = %s 
        AND ABS(TIMESTAMPDIFF(SECOND, event_start, %s)) < 10
        LIMIT 1
    """
    cursor.execute(check_query, (session_id, drift_type, event_start))
    existing = cursor.fetchone()
    
    if existing:
        return  # Already exists, skip
    
    # Insert the drift event
    insert_query = """
        INSERT INTO drift_event 
        (session_id, event_start, event_end, duration_seconds, drift_type, description, severity)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (session_id, event_start, event_end, duration, drift_type, description, severity))

def analyze_recent_sessions(user_id, hours=24):
    """Analyze all active sessions for a given user from the last N hours."""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return
    
    cursor = conn.cursor()
    
    try:
        # Get all active sessions from the last N hours for the given user
        cutoff_time = datetime.now() - timedelta(hours=hours)
        query = """
            SELECT sid, start_time FROM sessions 
            WHERE user_id = %s
            AND start_time >= %s 
            AND (end_time IS NULL OR end_time >= %s)
            ORDER BY start_time DESC
        """
        cursor.execute(query, (user_id, cutoff_time, cutoff_time))
        sessions = cursor.fetchall()
        
        print(f"Found {len(sessions)} active sessions to analyze for user {user_id}...\n")
        
        for row in sessions:
            session_id = row[0]
            analyze_drifts_for_session(session_id)
            print()  # Blank line between sessions
        
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

import json

def analyze_focus_breaks(cursor, user_id, session_id, events):
    """Analyze focus breaks (micro-drifts) for a session."""
    query = """
        WITH FocusedEvents AS (
            SELECT 
                ae.session_id, ae.timestamp, d.category, ae.tab_id, 
                LAG(d.category, 1) OVER(PARTITION BY ae.session_id ORDER BY ae.timestamp) AS prev_category, 
                LEAD(d.category, 1) OVER(PARTITION BY ae.session_id ORDER BY ae.timestamp) AS next_category, 
                TIMESTAMPDIFF(SECOND, ae.timestamp, LEAD(ae.timestamp, 1) OVER(PARTITION BY ae.session_id ORDER BY ae.timestamp)) AS time_on_this_tab 
            FROM activity_event ae 
            JOIN tab t ON ae.tab_id = t.tid 
            JOIN domains d ON t.domain_id = d.id 
            WHERE ae.event_type = 'TAB_FOCUS' AND ae.user_id = %s 
              AND ae.session_id = %s
        )
        SELECT 
            session_id, timestamp AS drift_start_time, time_on_this_tab AS drift_duration, tab_id
        FROM FocusedEvents 
        WHERE 
            prev_category = 'Productive' 
            AND category = 'Unproductive' 
            AND next_category = 'Productive' 
            AND time_on_this_tab < 180
    """
    cursor.execute(query, (user_id, session_id))
    results = cursor.fetchall()
    
    for row in results:
        session_id, drift_start_time, drift_duration, tab_id = row
        severity = 'HIGH' if drift_duration > 120 else 'MEDIUM' if drift_duration > 60 else 'LOW'
        description = f"Focus break for {drift_duration}s"
        event_meta = json.dumps({"drift_duration": drift_duration, "tab_id": tab_id})
        insert_drift(cursor, session_id, drift_start_time, 
                    drift_start_time + timedelta(seconds=drift_duration),
                    'FOCUS_BREAK', description, severity, tab_id, event_meta)
        print(f"  [OK] Detected Focus Break: {description}")

def analyze_drift_triggers(cursor, user_id, session_id, events):
    """Analyze drift triggers (domains that precede high-severity drifts)."""
    query = """
        WITH HighSeverityDrifts AS (
            SELECT session_id, event_start, drift_id
            FROM drift_event
            WHERE severity = 'HIGH' 
              AND session_id IN (SELECT sid FROM sessions WHERE user_id = %s)
        ),
        LastActivityBeforeDrift AS (
            SELECT 
                hsd.event_start,
                hsd.drift_id,
                (SELECT ae.tab_id 
                 FROM activity_event ae 
                 WHERE ae.session_id = hsd.session_id AND ae.timestamp < hsd.event_start 
                 ORDER BY ae.timestamp DESC 
                 LIMIT 1 
                ) AS last_tab_id
            FROM HighSeverityDrifts hsd
        )
        SELECT 
            d.domain_name, d.category, COUNT(*) AS drift_trigger_count,
            labd.drift_id, labd.last_tab_id
        FROM LastActivityBeforeDrift labd
        JOIN tab t ON labd.last_tab_id = t.tid 
        JOIN domains d ON t.domain_id = d.id 
        WHERE d.category = 'Productive' 
        GROUP BY d.domain_name, d.category, labd.drift_id, labd.last_tab_id
        ORDER BY drift_trigger_count DESC
    """
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    
    for row in results:
        domain_name, category, drift_trigger_count, drift_id, last_tab_id = row
        description = f"{domain_name} triggered {drift_trigger_count} high-severity drifts"
        event_meta = json.dumps({"drift_trigger_count": drift_trigger_count, 
                               "domain_name": domain_name, "tab_id": last_tab_id})
        insert_drift(cursor, session_id, events[0]['timestamp'], events[-1]['timestamp'],
                    'DRIFT_TRIGGER', description, 'HIGH', last_tab_id, event_meta)
        print(f"  [OK] Detected Drift Trigger: {description}")

def analyze_search_to_unproductive(cursor, user_id, session_id, events):
    """Analyze search-to-unproductive drifts."""
    query = """
        WITH UrlChanges AS (
            SELECT 
                ae.session_id, ae.timestamp, ae.url, d.category, ae.tab_id,
                LEAD(ae.timestamp, 1) OVER(PARTITION BY ae.session_id ORDER BY ae.timestamp) AS next_timestamp, 
                LEAD(d.category, 1) OVER(PARTITION BY ae.session_id ORDER BY ae.timestamp) AS next_category 
            FROM activity_event ae 
            JOIN tab t ON ae.tab_id = t.tid 
            JOIN domains d ON t.domain_id = d.id 
            WHERE 
                ae.user_id = %s 
                AND ae.session_id = %s
                AND (ae.event_type = 'URL_CHANGE' OR ae.event_type = 'TAB_FOCUS') 
        )
        SELECT 
            session_id, timestamp AS search_time, next_timestamp AS drift_time, tab_id
        FROM UrlChanges 
        WHERE 
            (url LIKE '%google.com/search%' OR url LIKE '%bing.com/search%') 
            AND next_category = 'Unproductive' 
            AND TIMESTAMPDIFF(MINUTE, timestamp, next_timestamp) < 2
    """
    cursor.execute(query, (user_id, session_id))
    results = cursor.fetchall()
    
    for row in results:
        session_id, search_time, drift_time, tab_id = row
        duration = (drift_time - search_time).total_seconds()
        severity = 'HIGH' if duration < 30 else 'MEDIUM'
        description = f"Search to unproductive in {int(duration)}s"
        event_meta = json.dumps({"search_time": search_time.isoformat(), 
                               "drift_time": drift_time.isoformat(),
                               "duration": duration, "tab_id": tab_id})
        insert_drift(cursor, session_id, search_time, drift_time,
                    'SEARCH_TO_UNPRODUCTIVE', description, severity, tab_id, event_meta)
        print(f"  ✓ Detected Search-to-Unproductive: {description}")

def analyze_task_abandonment(cursor, user_id, session_id, events):
    """Analyze task abandonment patterns."""
    query = """
        WITH TabFocusWithLead AS (
            SELECT 
                ae.session_id, ae.timestamp, d.category, ae.tab_id,
                LEAD(d.category, 1) OVER(PARTITION BY ae.session_id ORDER BY ae.timestamp) AS next_category, 
                TIMESTAMPDIFF(SECOND, ae.timestamp, LEAD(ae.timestamp, 1) OVER(PARTITION BY ae.session_id ORDER BY ae.timestamp)) AS time_on_this_tab 
            FROM activity_event ae 
            JOIN tab t ON ae.tab_id = t.tid 
            JOIN domains d ON t.domain_id = d.id 
            WHERE ae.event_type = 'TAB_FOCUS' AND ae.user_id = %s 
              AND ae.session_id = %s
        )
        SELECT 
            session_id, timestamp AS abandonment_time, time_on_this_tab, tab_id
        FROM TabFocusWithLead 
        WHERE 
            category = 'Productive' 
            AND next_category = 'Unproductive' 
            AND time_on_this_tab < 60
    """
    cursor.execute(query, (user_id, session_id))
    results = cursor.fetchall()
    
    for row in results:
        session_id, abandonment_time, time_on_this_tab, tab_id = row
        severity = 'HIGH' if time_on_this_tab < 30 else 'MEDIUM'
        description = f"Abandoned productive task after {time_on_this_tab}s"
        event_meta = json.dumps({"time_on_task": time_on_this_tab, 
                               "tab_id": tab_id, "abandonment_time": abandonment_time.isoformat()})
        insert_drift(cursor, session_id, abandonment_time, 
                    abandonment_time + timedelta(seconds=time_on_this_tab),
                    'TASK_ABANDONMENT', description, severity, tab_id, event_meta)
        print(f"  ✓ Detected Task Abandonment: {description}")

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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run drift analysis on recent sessions.")
    parser.add_argument("--hours", type=int, default=24, help="Number of hours back to analyze.")
    parser.add_argument("--session", type=int, help="A specific session ID to analyze.")
    parser.add_argument("--user", type=int, help="A specific user ID to analyze.")

    args = parser.parse_args()

    if args.session:
        print(f"Analyzing specific session: {args.session}")
        analyze_drifts_for_session(args.session)
    elif args.user:
        print(f"Analyzing recent sessions for user: {args.user}")
        analyze_recent_sessions(args.user, args.hours)
    else:
        print("Analyzing all recent sessions for all users...")
        # Get all user IDs and analyze sessions for each user
        user_ids = get_all_user_ids()
        if user_ids:
            print(f"Found {len(user_ids)} users to analyze")
            for user_id in user_ids:
                print(f"\n--- Analyzing sessions for user {user_id} ---")
                analyze_recent_sessions(user_id, args.hours)
        else:
            print("No users found in database")

