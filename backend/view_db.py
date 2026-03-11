import sqlite3
import os

# Database Path
db_path = os.path.join(os.getcwd(), 'instance', 'database.db')

def view_database():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"\n" + "="*50)
        print(f"DATABASE VIEW: {os.path.basename(db_path)}")
        print("="*50)
        
        for table_name in tables:
            table_name = table_name[0]
            if table_name == 'sqlite_sequence': continue
                
            print(f"\n>>> Table: {table_name}")
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            if not rows:
                print("    (No data found)")
            else:
                # Print header
                header = " | ".join(columns)
                print("-" * len(header))
                print(header)
                print("-" * len(header))
                
                # Print rows
                for row in rows:
                    print(" | ".join(str(val) for val in row))

        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    view_database()
