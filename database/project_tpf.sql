DELIMITER $$

CREATE TRIGGER calculate_drift_duration
BEFORE INSERT ON drift_event
FOR EACH ROW
BEGIN
    SET NEW.duration_seconds = TIMESTAMPDIFF(SECOND, NEW.event_start, NEW.event_end);
END$$
DELIMITER ;

-- Add a new column to the tab table first
ALTER TABLE tab ADD COLUMN last_activity_at TIMESTAMP NULL;

DELIMITER $$
CREATE TRIGGER trg_update_tab_activity
AFTER INSERT ON activity_event
FOR EACH ROW
BEGIN
    UPDATE tab
    SET last_activity_at = NEW.timestamp
    WHERE tid = NEW.tab_id;
END$$
DELIMITER ;

-- Add a new column to the sessions table first
ALTER TABLE sessions ADD COLUMN last_activity_at TIMESTAMP NULL;

DELIMITER $$
CREATE TRIGGER trg_update_session_activity
AFTER INSERT ON activity_event
FOR EACH ROW
BEGIN
    UPDATE sessions
    SET last_activity_at = NEW.timestamp
    WHERE sid = NEW.session_id;
END$$
DELIMITER ;



DELIMITER $$

CREATE PROCEDURE closeSession(IN p_session_id INT)
BEGIN
    DECLARE v_now TIMESTAMP;
    SET v_now = NOW();

    UPDATE sessions SET end_time = v_now WHERE sid = p_session_id;
    UPDATE tab SET closed_at = v_now WHERE session_id = p_session_id AND closed_at IS NULL;

END$$
DELIMITER ;


DELIMITER $$

CREATE PROCEDURE getOrCreateDomain(IN  p_user_id INT, IN  p_domain_name VARCHAR(255), OUT p_domain_id INT
)
BEGIN
    SELECT id INTO p_domain_id FROM domains WHERE user_id = p_user_id AND domain_name = p_domain_name LIMIT 1;

    IF p_domain_id IS NULL THEN
        INSERT INTO domains (user_id, domain_name)
        VALUES 
        (p_user_id, p_domain_name);
        
        SET p_domain_id = LAST_INSERT_ID();
    END IF;
END$$

DELIMITER ;

DELIMITER $$
CREATE PROCEDURE sp_AnalyzeSessionDrifts(IN p_session_id INT)
BEGIN
    DECLARE v_user_id INT;
    DECLARE v_tab_id INT;
    DECLARE v_event_type VARCHAR(50);
    DECLARE v_timestamp TIMESTAMP(3);
    DECLARE v_url VARCHAR(2083);
    DECLARE v_domain_name VARCHAR(255);
    DECLARE v_domain_category ENUM('Productive','Unproductive','Neutral','Social Media','Entertainment');
    
    -- State variables for loop detection
    DECLARE v_last_domain_category VARCHAR(50) DEFAULT 'Neutral';
    DECLARE v_last_event_time TIMESTAMP(3);
    
    -- Cursor to loop through all events for the session
    DECLARE event_cursor CURSOR FOR
        SELECT 
            ae.user_id, ae.tab_id, ae.event_type, ae.timestamp, ae.url,
            d.domain_name, d.category
        FROM activity_event ae
        JOIN tab t ON ae.tab_id = t.tid
        JOIN domains d ON t.domain_id = d.id
        WHERE ae.session_id = p_session_id
        ORDER BY ae.timestamp;
        
    -- TODO: Add handlers for cursor
    
    OPEN event_cursor;
    
    event_loop: LOOP
        FETCH event_cursor INTO v_user_id, v_tab_id, v_event_type, v_timestamp, v_url, v_domain_name, v_domain_category;
        
        -- PSEUDO-CODE for detection logic:
        
        -- 1. Unproductive Shift Detection
        IF (v_event_type = 'TAB_FOCUS' OR v_event_type = 'URL_CHANGE') THEN
            IF (v_last_domain_category = 'Productive' AND v_domain_category = 'Unproductive') THEN
                -- This is a simple drift. Log it.
                INSERT INTO drift_event (session_id, event_start, event_end, drift_type, description, severity)
                VALUES (p_session_id, v_timestamp, v_timestamp, 'Unproductive Shift', CONCAT('Shifted to ', v_domain_name), 'LOW');
                
                -- Also link the tab
                INSERT INTO drift_involves_tab (tab_id, drift_id) VALUES (v_tab_id, LAST_INSERT_ID());
            END IF;
            
            SET v_last_domain_category = v_domain_category;
        END IF;
        
        -- 2. Idle Detection
        IF (v_last_event_time IS NOT NULL AND TIMESTAMPDIFF(MINUTE, v_last_event_time, v_timestamp) > 5) THEN
            INSERT INTO drift_event (session_id, event_start, event_end, drift_type, description, severity)
            VALUES (p_session_id, v_last_event_time, v_timestamp, 'Idle', 'User idle for 5+ minutes', 'LOW');
        END IF;

        -- 3. TODO: Add logic for other drift types (Rapid Switching, Loops)
        -- This requires more complex state management (e.g., temp tables)
        
        SET v_last_event_time = v_timestamp;
        
    END LOOP event_loop;
    
    CLOSE event_cursor;
END$$
DELIMITR ;


DELIMITER $$
CREATE PROCEDURE sp_UpdateDailySummaries(IN p_user_id INT, IN p_date DATE)
BEGIN
    -- This is a complex query. It calculates the duration of each event
    -- by finding the time until the *next* event on the same tab.
    
    INSERT INTO daily_domain_summary (user_id, domain_id, summary_date, total_seconds_focused, total_events)
    WITH EventDurations AS (
        SELECT
            user_id,
            tab_id,
            timestamp,
            -- Calculate duration as time until next event, max 300s (5min)
            COALESCE(
                LEAST(
                    TIMESTAMPDIFF(SECOND, timestamp, LEAD(timestamp) OVER (PARTITION BY tab_id ORDER BY timestamp)),
                    300
                ),
                10 -- Default 10s for the last event
            ) AS duration_seconds
        FROM activity_event
        WHERE DATE(timestamp) = p_date AND user_id = p_user_id
    )
    SELECT
        ed.user_id,
        t.domain_id,
        p_date,
        SUM(ed.duration_seconds) AS total_seconds_focused,
        COUNT(ed.user_id) AS total_events
    FROM EventDurations ed
    JOIN tab t ON ed.tab_id = t.tid
    GROUP BY ed.user_id, t.domain_id
    
    -- This handles conflicts: if a summary for that day already exists,
    -- it updates it by adding the new values (in case you run it mid-day)
    ON DUPLICATE KEY UPDATE
        total_seconds_focused = total_seconds_focused + VALUES(total_seconds_focused),
        total_events = total_events + VALUES(total_events);
END$$
DELIMITER ;

DELIMITER $$

CREATE FUNCTION extractDomainFromUrl(p_url VARCHAR(2083))
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    DECLARE domain_name VARCHAR(255);

    SET domain_name = SUBSTRING_INDEX(p_url, '://', -1);
    SET domain_name = SUBSTRING_INDEX(domain_name, '/', 1);
    SET domain_name = SUBSTRING_INDEX(domain_name, ':', 1);

    IF LOCATE('www.', domain_name) = 1 THEN
        SET domain_name = SUBSTRING(domain_name, 5);
    END IF;

    RETURN domain_name;
END$$
DELIMITER ;