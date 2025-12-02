"""
User model for Toonify application
Stores Spotify OAuth user information
"""
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from database.config import Base
import uuid
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    # Primary key
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Spotify OAuth fields
    spotify_id = Column(String(255), unique=True, nullable=False, index=True)
    spotify_access_token = Column(Text, nullable=True, comment='Spotify OAuth access token - should be encrypted in production')
    spotify_refresh_token = Column(Text, nullable=True, comment='Spotify OAuth refresh token - should be encrypted in production')

    # User profile fields (from Spotify)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    profile_image = Column(Text, nullable=True)
    country = Column(String(2), nullable=True)
    spotify_uri = Column(String(255), nullable=True, comment='Spotify URI for the user')

    # Timestamps
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    playlists = relationship('Playlist', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, spotify_id={self.spotify_id})>"

    def update_spotify_tokens(self, access_token, refresh_token):
        """
        Update Spotify OAuth tokens for the user

        Args:
            access_token (str): Spotify access token
            refresh_token (str): Spotify refresh token
        """
        self.spotify_access_token = access_token
        self.spotify_refresh_token = refresh_token
        self.last_login = datetime.utcnow()

    def get_public_profile(self):
        """
        Get user's public profile (safe for API responses)

        Returns:
            dict: Public user profile without sensitive data
        """
        return {
            'id': self.id,
            'display_name': self.display_name,
            'email': self.email,
            'profile_image': self.profile_image,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def to_dict(self):
        """
        Convert user to dictionary (includes all fields except tokens)

        Returns:
            dict: User data
        """
        return {
            'id': self.id,
            'spotify_id': self.spotify_id,
            'email': self.email,
            'display_name': self.display_name,
            'profile_image': self.profile_image,
            'country': self.country,
            'spotify_uri': self.spotify_uri,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
