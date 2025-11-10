# backend/main.py
from fastapi import FastAPI, HTTPException, Body, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import mysql.connector
from database import get_db_connection
from models import *
import os
from dotenv import load_dotenv

app = FastAPI()

# --- Security Configuration ---
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

import bcrypt
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_db_connection_for_user(user_type='user'):
    """Get database connection based on user type (admin or user)"""
    if user_type == 'admin':
        # Load admin environment variables
        load_dotenv('.env.admin')
    else:
        # Load regular user environment variables
        load_dotenv('.env.user')
    
    # Get connection using the appropriate user credentials
    return get_db_connection()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role", "user")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "email": email, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- Middleware ---
# This allows your extension and dashboard (on different ports)
# to talk to this server. CRITICAL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "Digital Drift Tracker API is running"}

@app.post("/api/session/start", response_model=SessionResponse)
async def session_start(payload: SessionStartPayload, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection_for_user('admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    user_id = current_user["user_id"]
    query = """
        INSERT INTO sessions (user_id, browser_name, browser_version, platform)
        VALUES (%s, %s, %s, %s)
    """
    # Note: You have 'timezone' in your 'user' table, not 'sessions'.
    # This assumes user_id is valid.
    cursor.execute(query, (user_id, payload.browser_name, payload.browser_version, payload.platform))
    sid = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return SessionResponse(sid=sid)

@app.post("/api/session/close")
async def session_close(payload: dict = Body(...)):
    sid = payload.get('sid')
    if not sid:
        raise HTTPException(status_code=400, detail="Missing session ID")

    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        # Call the stored procedure
        cursor.callproc('closeSession', [sid])
        conn.commit()
        return {"status": "ok", "sid_closed": sid}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to close session: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/api/dashboard/insights")
async def get_insights(current_user: dict = Depends(get_current_user)):
    """Return insights data composed of multiple analytic queries."""
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor()
    user_id = current_user["user_id"]

    def rows_to_dicts(rows, cur):
        if not rows or not cur.description:
            return []
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]

    try:
        # Query 5: Unclassified High-Activity Domains (last 30 days)
        q5 = (
            """
            SELECT 
                d.domain_name, d.id AS domain_id, SUM(dds.total_seconds_focused) AS total_time_seconds
            FROM daily_domain_summary dds
            JOIN domains d ON dds.domain_id = d.id
            WHERE 
                dds.user_id = %s
                AND d.category = 'Neutral'
                AND dds.summary_date > (CURDATE() - INTERVAL 30 DAY)
                AND NOT EXISTS (
                    SELECT 1 FROM whitelists w WHERE w.domain_id = d.id AND w.user_id = d.user_id
                )
            GROUP BY d.domain_name, d.id
            ORDER BY total_time_seconds DESC
            LIMIT 5
            """
        )
        cursor.execute(q5, (user_id,))
        unclassified_domains = rows_to_dicts(cursor.fetchall(), cursor)

        # Query 6: Tab Switches vs Productivity (per-session productive minutes)
        # Computes productive_seconds strictly within each session boundaries by summing
        # focus durations on tabs categorized as 'Productive'.
        q6 = (
            """
            SELECT 
                s.sid, s.start_time, TIMESTAMPDIFF(MINUTE, s.start_time, s.end_time) AS total_minutes,
                (SELECT COUNT(*) 
                 FROM activity_event ae 
                 WHERE ae.session_id = s.sid AND ae.event_type = 'TAB_FOCUS'
                ) AS tab_switches,
                (
                    SELECT COALESCE(SUM(
                        TIMESTAMPDIFF(SECOND,
                            ae.timestamp,
                            LEAST(COALESCE(ae.next_ts, s.end_time), s.end_time)
                        )
                    ), 0)
                    FROM (
                        SELECT 
                            ae.session_id, ae.timestamp, ae.tab_id,
                            LEAD(ae.timestamp) OVER (PARTITION BY ae.session_id ORDER BY ae.timestamp) AS next_ts
                        FROM activity_event ae
                        WHERE ae.session_id = s.sid AND ae.event_type = 'TAB_FOCUS'
                    ) AS ae
                    JOIN tab t ON ae.tab_id = t.tid
                    JOIN domains d ON t.domain_id = d.id
                    WHERE d.category = 'Productive'
                ) AS productive_seconds
            FROM sessions s
            WHERE s.user_id = %s AND s.end_time IS NOT NULL
            ORDER BY s.start_time DESC
            """
        )
        cursor.execute(q6, (user_id,))
        session_productivity = rows_to_dicts(cursor.fetchall(), cursor)

        # Query 7: Driftiest Hours of the Day
        q7 = (
            """
            SELECT 
                HOUR(de.event_start) AS drift_hour,
                COUNT(*) AS total_drifts,
                'Unproductive Shift' AS most_common_drift_type
            FROM drift_event de
            JOIN sessions s ON de.session_id = s.sid
            WHERE s.user_id = %s
            GROUP BY HOUR(de.event_start)
            ORDER BY total_drifts DESC
            """
        )
        cursor.execute(q7, (user_id,))
        driftiest_hours = rows_to_dicts(cursor.fetchall(), cursor)

        # Query 8: Stickiest Distractions
        q8 = (
            """
            WITH TabFocusDurations AS (
                SELECT t.domain_id,
                       TIMESTAMPDIFF(SECOND, ae.timestamp, LEAD(ae.timestamp, 1) OVER(PARTITION BY ae.session_id ORDER BY ae.timestamp)) AS focus_duration_seconds
                FROM activity_event ae
                JOIN tab t ON ae.tab_id = t.tid
                WHERE ae.event_type = 'TAB_FOCUS' AND ae.user_id = %s
            )
            SELECT d.domain_name,
                   AVG(tfd.focus_duration_seconds) AS avg_duration_seconds
            FROM TabFocusDurations tfd
            JOIN domains d ON tfd.domain_id = d.id
            WHERE d.user_id = %s
              AND d.category = 'Unproductive'
              AND tfd.focus_duration_seconds IS NOT NULL
              AND tfd.focus_duration_seconds < 1800
            GROUP BY d.domain_name
            ORDER BY avg_duration_seconds DESC
            LIMIT 5
            """
        )
        cursor.execute(q8, (user_id, user_id))
        stickiest_distractions = rows_to_dicts(cursor.fetchall(), cursor)

        return {
            "unclassified_domains": unclassified_domains,
            "session_productivity": session_productivity,
            "driftiest_hours": driftiest_hours,
            "stickiest_distractions": stickiest_distractions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch insights: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@app.post("/api/tab/open", response_model=TabResponse)
async def tab_open(payload: TabPayload, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    user_id = current_user["user_id"]
    
    try:
        # 1. Get the clean domain
        cursor.execute("SELECT extractDomainFromUrl(%s) AS domain_name", (payload.url,))
        result = cursor.fetchone()
        domain_name = result[0] if result else None
        
        if not domain_name:
            raise HTTPException(status_code=400, detail="Invalid URL")

        # 2. Get or create the domain_id and determine category
        # First check if domain exists
        cursor.execute("SELECT id, category FROM domains WHERE user_id = %s AND domain_name = %s", 
                      (user_id, domain_name))
        result = cursor.fetchone()
        
        domain_exists = result is not None
        if domain_exists:
            domain_id = result[0]
            current_category = result[1] if len(result) > 1 else None
        else:
            # Create new domain - category will be set below based on whitelist
            cursor.execute("INSERT INTO domains (user_id, domain_name, category) VALUES (%s, %s, 'Neutral')",
                          (user_id, domain_name))
            domain_id = cursor.lastrowid
            current_category = 'Neutral'
        
        # 3. Check if domain is in whitelist
        cursor.execute("SELECT domain_id FROM whitelists WHERE user_id = %s AND domain_id = %s",
                      (user_id, domain_id))
        is_whitelisted = cursor.fetchone() is not None
        
        # 4. Update category based on whitelist rules:
        # - If in whitelist -> Productive
        # - If not in whitelist and visited (exists or new) -> Unproductive
        # - If not in whitelist and never visited -> Neutral (only for domains not yet visited)
        if is_whitelisted:
            # Domain is whitelisted, set to Productive
            if current_category != 'Productive':
                cursor.execute("UPDATE domains SET category = 'Productive' WHERE id = %s",
                              (domain_id,))
        else:
            # Domain is not whitelisted
            # If it's being visited now (new or existing), it should be Unproductive
            # Only keep Neutral if it truly hasn't been visited yet
            # Since we're in tab_open, this domain is being visited, so set to Unproductive
            if current_category != 'Unproductive':
                cursor.execute("UPDATE domains SET category = 'Unproductive' WHERE id = %s",
                              (domain_id,))

        # 5. Insert the new tab
        query = "INSERT INTO tab (session_id, domain_id, url, title) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (payload.session_id, domain_id, payload.url, payload.title))
        tid = cursor.lastrowid
        
        conn.commit()
        return TabResponse(tid=tid, domain_id=domain_id)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to open tab: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.post("/api/tab/close")
async def tab_close(payload: dict = Body(...)):
    tid = payload.get('tid')
    if not tid:
        raise HTTPException(status_code=400, detail="Missing tab ID")
    
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        query = "UPDATE tab SET closed_at = NOW(), is_active = 0 WHERE tid = %s"
        cursor.execute(query, (tid,))
        conn.commit()
        return {"status": "ok", "tid_closed": tid}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to close tab: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.post("/api/events/batch")
async def events_batch(payload: EventBatchPayload, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    user_id = current_user["user_id"]
    
    insert_data = []
    for event in payload.events:
        insert_data.append((
            payload.session_id,
            user_id,
            event.tab_id,
            event.event_type,
            event.timestamp,
            event.url,
            event.mouse_x,
            event.mouse_y,
            event.scroll_y_pixels,
            event.scroll_y_percent,
            event.target_element_id
        ))

    query = """
        INSERT INTO activity_event (
            session_id, user_id, tab_id, event_type, timestamp, url, 
            mouse_x, mouse_y, scroll_y_pixels, scroll_y_percent, target_element_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.executemany(query, insert_data)
        conn.commit()
        inserted_count = cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database insert failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()
    
    return {"inserted_count": inserted_count}

@app.get("/api/dashboard/analytics")
async def get_analytics(period_days: int = 7, current_user: dict = Depends(get_current_user)):
    """Get comprehensive analytics for the dashboard."""
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    user_id = current_user["user_id"]

    try:
        # Helper function to convert rows to dicts
        def rows_to_dicts(rows, cursor):
            if not rows or not cursor.description:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
        # Get drift events, for area chart
        query_drifts = """
            SELECT drift_id, drift_type, description, event_start, event_end, 
                   duration_seconds, severity
            FROM drift_event
            WHERE session_id IN (SELECT sid FROM sessions WHERE user_id = %s)
            AND event_start > (CURDATE() - INTERVAL %s DAY)
            ORDER BY event_start DESC
        """
        cursor.execute(query_drifts, (user_id, period_days))
        drifts_rows = cursor.fetchall()
        drifts = rows_to_dicts(drifts_rows, cursor)
        
        # Get daily domain summaries, for bar chart
        query_summaries = """
            SELECT d.domain_name, d.category, dds.summary_date,
                   dds.total_seconds_focused, dds.total_events
            FROM daily_domain_summary dds
            JOIN domains d ON dds.domain_id = d.id
            WHERE dds.user_id = %s
            AND dds.summary_date > (CURDATE() - INTERVAL %s DAY)
            ORDER BY dds.summary_date DESC, dds.total_seconds_focused DESC
        """
        cursor.execute(query_summaries, (user_id, period_days))
        summaries_rows = cursor.fetchall()
        summaries = rows_to_dicts(summaries_rows, cursor)
        
        # Get category totals, for pie chart
        query_category_totals = """
            SELECT d.category, SUM(dds.total_seconds_focused) as total_seconds
            FROM daily_domain_summary dds
            JOIN domains d ON dds.domain_id = d.id
            WHERE dds.user_id = %s
            AND dds.summary_date > (CURDATE() - INTERVAL %s DAY)
            GROUP BY d.category
        """
        cursor.execute(query_category_totals, (user_id, period_days))
        category_totals_rows = cursor.fetchall()
        category_totals = rows_to_dicts(category_totals_rows, cursor)
        
        return {
            "drift_events": drifts or [],
            "domain_summaries": summaries or [],
            "category_totals": category_totals or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/api/whitelist")
async def get_whitelist(current_user: dict = Depends(get_current_user)):
    """Get all whitelisted domains for a user."""
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    user_id = current_user["user_id"]
    
    try:
        def rows_to_dicts(rows, cursor):
            if not rows or not cursor.description:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
        query = """
            SELECT w.wid, w.user_id, w.domain_id, w.user_reason, w.created_at,
                   d.domain_name, d.category
            FROM whitelists w
            JOIN domains d ON w.domain_id = d.id
            WHERE w.user_id = %s
            ORDER BY w.created_at DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        whitelist = rows_to_dicts(rows, cursor)
        
        return {"whitelist": whitelist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch whitelist: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.post("/api/whitelist")
async def add_to_whitelist(payload: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Add a domain to the user's whitelist by domain_name."""
    user_id = current_user["user_id"]
    domain_name = payload.get('domain_name')
    user_reason = payload.get('user_reason', '')
    
    if not domain_name:
        raise HTTPException(status_code=400, detail="Missing domain_name")
    
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        # Get or create domain
        cursor.execute("SELECT id FROM domains WHERE user_id = %s AND domain_name = %s",
                      (user_id, domain_name))
        result = cursor.fetchone()
        
        if result:
            domain_id = result[0]
        else:
            # Create new domain
            cursor.execute("INSERT INTO domains (user_id, domain_name, category) VALUES (%s, %s, 'Productive')",
                          (user_id, domain_name))
            domain_id = cursor.lastrowid
        
        # Add to whitelist
        query = """
            INSERT INTO whitelists (user_id, domain_id, user_reason)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE user_reason = VALUES(user_reason)
        """
        cursor.execute(query, (user_id, domain_id, user_reason))
        
        # Update domain category to Productive
        cursor.execute("UPDATE domains SET category = 'Productive' WHERE id = %s", (domain_id,))
        
        conn.commit()
        return {"status": "ok", "whitelisted": True, "domain_id": domain_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to whitelist domain: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/whitelist/{domain_id}")
async def remove_from_whitelist(domain_id: int, current_user: dict = Depends(get_current_user)):
    """Remove a domain from the user's whitelist."""
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    user_id = current_user["user_id"]
    
    try:
        # Remove from whitelist
        cursor.execute("DELETE FROM whitelists WHERE user_id = %s AND domain_id = %s",
                      (user_id, domain_id))
        
        # Update domain category to Unproductive (since it was visited before)
        cursor.execute("UPDATE domains SET category = 'Unproductive' WHERE id = %s AND user_id = %s",
                      (domain_id, user_id))
        
        conn.commit()
        return {"status": "ok", "removed": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove from whitelist: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# --- Authentication Endpoints ---
@app.post("/api/auth/signup", response_model=Token)
async def signup(user: UserSignup):
    """Register a new user."""
    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute("SELECT uid FROM user WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user.password)
        cursor.execute(
            "INSERT INTO user (email, password_hash, created_at, timezone) VALUES (%s, %s, NOW(), %s)",
            (user.email, hashed_password, 'UTC')
        )
        user_id = cursor.lastrowid
        
        conn.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            email=user.email
        )
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return access token."""
    
    try:
        # Check for admin credentials (using database admin user)
        if user_credentials.email == "ddt_admin":
            # Get admin database connection
            conn = get_db_connection_for_user('admin')
            if conn is None:
                raise HTTPException(status_code=500, detail="Database connection failed")
            
            # Verify admin password using hardcoded check (since admin is a special system user)
            if user_credentials.password == "admin123":
                # Create admin access token
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": "admin", "email": "ddt_admin", "role": "admin"},
                    expires_delta=access_token_expires
                )
                return Token(
                    access_token=access_token,
                    token_type="bearer",
                    user_id=0,  # Special admin ID
                    email="ddt_admin"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid admin credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # For regular users, use regular database connection
        conn = get_db_connection_for_user('user')
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        
        # Get user by email
        cursor.execute(
            "SELECT uid, password_hash FROM user WHERE email = %s",
            (user_credentials.email,)
        )
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id, hashed_password = result
        
        # Verify password
        if not verify_password(user_credentials.password, hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_id), "email": user_credentials.email, "role": "user"},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            email=user_credentials.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT uid, email, created_at FROM user WHERE uid = %s",
            (current_user["user_id"],)
        )
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=result[0],
            email=result[1],
            created_at=result[2]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# To run this app:
# In your terminal (with venv activated), run:
# uvicorn main:app --reload

# --- Admin Endpoints ---

def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Dependency to ensure only admin users can access admin endpoints."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_admin_user)):
    """Get system-wide statistics for admin dashboard."""
    conn = get_db_connection_for_user('admin')
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        # Total users
        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]
        
        # Active users (users with sessions in last 30 days)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) 
            FROM sessions 
            WHERE start_time > (CURDATE() - INTERVAL 30 DAY)
        """)
        active_users = cursor.fetchone()[0]
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]
        
        # Total drift events
        cursor.execute("SELECT COUNT(*) FROM drift_event")
        total_drifts = cursor.fetchone()[0]
        
        # Average session duration
        cursor.execute("""
            SELECT AVG(TIMESTAMPDIFF(MINUTE, start_time, end_time))
            FROM sessions 
            WHERE end_time IS NOT NULL
        """)
        avg_session_duration = cursor.fetchone()[0] or 0
        
        # Top domains by total time across all users
        cursor.execute("""
            SELECT d.domain_name, d.category, SUM(dds.total_seconds_focused) as total_time
            FROM daily_domain_summary dds
            JOIN domains d ON dds.domain_id = d.id
            GROUP BY d.domain_name, d.category
            ORDER BY total_time DESC
            LIMIT 10
        """)
        top_domains = []
        for row in cursor.fetchall():
            top_domains.append({
                "domain": row[0],
                "category": row[1],
                "total_seconds": row[2]
            })
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_sessions": total_sessions,
            "total_drifts": total_drifts,
            "avg_session_duration_minutes": round(avg_session_duration, 2),
            "top_domains": top_domains
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get admin stats: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/api/admin/users")
async def get_admin_users(current_user: dict = Depends(get_admin_user)):
    """Get list of all users for admin dashboard."""
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT 
                u.uid, u.email, u.created_at,
                COUNT(DISTINCT s.sid) as session_count,
                COUNT(DISTINCT de.drift_id) as drift_count
            FROM user u
            LEFT JOIN sessions s ON u.uid = s.user_id
            LEFT JOIN drift_event de ON s.sid = de.session_id
            GROUP BY u.uid, u.email, u.created_at
            ORDER BY u.created_at DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        users = []
        for row in results:
            users.append({
                "id": row[0],
                "email": row[1],
                "created_at": row[2].isoformat() if row[2] else None,
                "session_count": row[3] or 0,
                "drift_count": row[4] or 0
            })
        
        return {"users": users}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(get_admin_user)):
    """Delete a user and all associated data (admin only)."""
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    
    try:
        # First, check if the user exists
        cursor.execute("SELECT uid, email FROM user WHERE uid = %s", (user_id,))
        user_result = cursor.fetchone()
        
        if not user_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        user_email = user_result[1]
        
        # Delete the user (this will cascade delete all related data due to foreign key constraints)
        cursor.execute("DELETE FROM user WHERE uid = %s", (user_id,))
        
        # Check if any rows were affected
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        conn.commit()
        
        return {
            "status": "success",
            "message": f"User {user_email} (ID: {user_id}) and all associated data have been deleted",
            "deleted_user_id": user_id,
            "deleted_user_email": user_email
        }
        
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)