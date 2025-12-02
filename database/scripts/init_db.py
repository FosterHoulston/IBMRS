"""
Script to initialize database tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.config import init_db, test_connection


def initialize_database():
    """
    Initialize database - create all tables
    """
    print("Initializing database...\n")

    # Test connection
    if not test_connection():
        print("✗ Cannot proceed without database connection")
        return False

    try:
        # Create all tables
        init_db()
        print("\n✓ Database initialization complete!\n")
        return True

    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        return False


if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)
