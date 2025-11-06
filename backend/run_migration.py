# backend/run_migration.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection

def run_auth_migration():
    """Run the authentication migration script to add password_hash column."""
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor()
    
    try:
        # Read the migration script
        migration_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'auth_migration.sql')
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        # Execute each statement
        for statement in statements:
            if statement and not statement.startswith('--'):
                print(f"Executing: {statement[:50]}...")
                cursor.execute(statement)
        
        conn.commit()
        print("Authentication migration completed successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = run_auth_migration()
    sys.exit(0 if success else 1)