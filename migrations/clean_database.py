import os
import sqlite3

def clean_database():
    """Remove and recreate the database."""
    db_path = os.path.join('data', 'robosite.db')
    
    # Remove existing database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database at {db_path}")
        except Exception as e:
            print(f"Error removing database: {str(e)}")
            return
    
    print("Database cleaned successfully. Run server.py to initialize a fresh database.")

if __name__ == "__main__":
    clean_database()
