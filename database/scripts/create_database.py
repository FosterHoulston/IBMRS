"""
Script to create the toonifyDB database
"""
import sys
import os
import pymysql
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables
load_dotenv()

DB_NAME = os.getenv('DB_NAME', 'toonifyDB')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '55005'))


def create_database():
    """
    Create the toonifyDB database if it doesn't exist
    """
    connection = None

    try:
        print("Connecting to MySQL server...")

        # Connect without specifying database
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        print("✓ Connected to MySQL server")

        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✓ Database '{DB_NAME}' created or already exists")

            # Use the database
            cursor.execute(f"USE `{DB_NAME}`")
            print(f"✓ Using database '{DB_NAME}'")

        connection.commit()
        print("\n✓ Database setup complete!\n")
        return True

    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

    finally:
        if connection:
            connection.close()
            print("✓ Database connection closed")


if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)
