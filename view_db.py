import sqlite3
import pandas as pd
import os

db_path = os.path.join(os.getcwd(), 'backend', 'instance', 'database.db')

def view_database():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"\n--- Database Viewer: {os.path.basename(db_path)} ---")
    
    for table_name in tables:
        table_name = table_name[0]
        if table_name == 'sqlite_sequence':
            continue
            
        print(f"\nTable: {table_name}")
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            if df.empty:
                print(" (Table is empty)")
            else:
                print(df.to_string(index=False))
        except Exception as e:
            print(f" Error reading table {table_name}: {e}")

    conn.close()

if __name__ == "__main__":
    view_database()
