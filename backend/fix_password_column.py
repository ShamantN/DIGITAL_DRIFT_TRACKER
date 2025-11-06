# backend/fix_password_column.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection

def add_password_hash_column():
    """Add password_hash column to user table if it doesn't exist."""
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if password_hash column already exists
        cursor.execute("SHOW COLUMNS FROM user LIKE 'password_hash'")
        result = cursor.fetchone()
        
        if result:
            print("password_hash column already exists")
            return True
        
        # Add password_hash column
        print("Adding password_hash column...")
        cursor.execute("ALTER TABLE user ADD COLUMN password_hash VARCHAR(255) AFTER email")
        
        # Make email unique if not already
        print("Making email unique...")
        cursor.execute("ALTER TABLE user ADD UNIQUE KEY unique_email (email)")
        
        conn.commit()
        print("Password hash column added successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = add_password_hash_column()
    sys.exit(0 if success else 1)