# backend/database.py
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '3306')),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'ddt'),
            auth_plugin='mysql_native_password',
            connect_timeout=10
        )
        return conn
    except mysql.connector.Error as e:
        print(f"MySQL connection error: {e}")
        return None
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None