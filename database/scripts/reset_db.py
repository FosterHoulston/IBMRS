"""
Script to reset database - drop and recreate all tables
WARNING: This will delete all data!
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.config import drop_db, init_db, test_connection


def reset_database():
    """
    Reset database - drop and recreate all tables
    WARNING: This deletes all data!
    """
    print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!\n")

    # Get confirmation
    response = input("Are you sure you want to reset the database? (yes/no): ")

    if response.lower() != 'yes':
        print("\n✓ Database reset cancelled")
        return False

    print("\nResetting database...\n")

    # Test connection
    if not test_connection():
        print("✗ Cannot proceed without database connection")
        return False

    try:
        # Drop all tables
        drop_db()

        # Recreate all tables
        init_db()

        print("\n✓ Database reset complete! All tables recreated.\n")
        print("Run 'python database/seeders/seed.py' to populate with sample data.\n")
        return True

    except Exception as e:
        print(f"\n✗ Error resetting database: {e}")
        return False


if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
