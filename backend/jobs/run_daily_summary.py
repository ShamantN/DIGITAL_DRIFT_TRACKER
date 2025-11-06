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
        # Call stored procedure - it only takes date parameter
        cursor.callproc('sp_UpdateDailySummaries', [target_date])
        # Consume any result sets to keep connector happy
        try:
            for _ in cursor.stored_results():
                pass
        except Exception:
            pass
        conn.commit()
        print(f"[OK] Daily summary updated for {target_date}")
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run daily summary job for a specific date and user.')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format. Defaults to today.')
    parser.add_argument('--user', type=int, help='User ID (deprecated - procedure runs for all users).')
    args = parser.parse_args()

    arg_date = None
    if args.date:
        try:
            arg_date = date.fromisoformat(args.date)
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)

    run_daily_summary(target_date=arg_date)
