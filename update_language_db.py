import sqlite3

DB_PATH = "diabetes_tracker.db"

def update_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "language" not in columns:
            print("Adding 'language' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN language VARCHAR DEFAULT 'tr'")
            conn.commit()
            print("Successfully added 'language' column. Default is 'tr'.")
        else:
            print("'language' column already exists in 'users' table.")
            
    except sqlite3.OperationalError as e:
        print(f"Error updating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_db()
