#!/usr/bin/env python3
"""
Daily Summary Job

Calls the stored procedure sp_UpdateDailySummaries to aggregate
activity into daily_domain_summary for a given date (defaults to today).
"""

import sys
import os
from datetime import date

# Add parent directory to path to import database module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection


def run_daily_summary(target_date: date | None = None) -> None:
    if target_date is None:
        target_date = date.today()

    conn = get_db_connection()
    if conn is None:
        print("ERROR: Database connection failed")
        sys.exit(1)

    cursor = conn.cursor()
    try:
        print(f"Running daily summary for {target_date}...")
        # Call stored procedure
        cursor.callproc('sp_UpdateDailySummaries', [target_date])
        # Consume any result sets to keep connector happy
        try:
            for _ in cursor.stored_results():
                pass
        except Exception:
            pass
        conn.commit()
        print("✓ Daily summary updated")
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Optional CLI arg: YYYY-MM-DD
    arg_date = None
    if len(sys.argv) > 1:
        try:
            arg_date = date.fromisoformat(sys.argv[1])
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    run_daily_summary(arg_date)
