#!/usr/bin/env python3
"""
Add Test Module to Database
Adds the test import module to the main training database
"""

import sqlite3
from pathlib import Path

def add_test_module():
    """Add test module to the main database"""
    db_path = Path("training_data.db")
    
    if not db_path.exists():
        print(f"Database {db_path} not found")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if module already exists
        cursor.execute("SELECT id FROM modules WHERE name = ?", ("Test Import Module",))
        if cursor.fetchone():
            print("Test module already exists in database")
            return True
        
        # Add test module
        cursor.execute('''
            INSERT INTO modules (name, description, prerequisites, estimated_duration)
            VALUES (?, ?, ?, ?)
        ''', (
            "Test Import Module",
            "A test module designed to verify the dynamic import functionality of the training system.",
            "",
            30
        ))
        
        conn.commit()
        print("Test module added successfully to database")
        return True
        
    except Exception as e:
        print(f"Error adding test module: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = add_test_module()
    if success:
        print("\n✅ Test module is now available in the training system")
        print("You can run the training system and select 'Test Import Module' from the modules list")
    else:
        print("\n❌ Failed to add test module to database")