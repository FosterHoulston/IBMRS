"""
Database configuration for Toonify application
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = os.getenv('DB_NAME', 'toonifyDB')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '55005')
DB_CHARSET = 'utf8mb4'

# Create database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=os.getenv('DB_LOGGING', 'False').lower() == 'true'  # SQL logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread safety
db_session = scoped_session(SessionLocal)

# Base class for all models
Base = declarative_base()

# Dependency for getting database session
def get_db():
    """
    Database session dependency for Flask routes
    Usage:
        from database.config import get_db
        db = next(get_db())
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database - create all tables
    """
    from database.models import User, Playlist, Song, PlaylistSong
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

def drop_db():
    """
    Drop all database tables (use with caution!)
    """
    Base.metadata.drop_all(bind=engine)
    print("✓ Database tables dropped successfully")

def test_connection():
    """
    Test database connection
    """
    try:
        connection = engine.connect()
        connection.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
