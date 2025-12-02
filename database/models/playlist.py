"""
Playlist model for Toonify application
User-created playlists
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from database.config import Base
import uuid
from datetime import datetime


class Playlist(Base):
    __tablename__ = 'playlists'

    # Primary key
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Playlist fields
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    cover_image = Column(Text, nullable=True)

    # Foreign key to User
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    user = relationship('User', back_populates='playlists')
    songs = relationship('Song', secondary='playlist_songs', back_populates='playlists', overlaps="playlist_songs")
    playlist_songs = relationship('PlaylistSong', back_populates='playlist', cascade='all, delete-orphan', overlaps="songs")

    def __repr__(self):
        return f"<Playlist(id={self.id}, name={self.name}, user_id={self.user_id})>"

    def get_song_count(self):
        """
        Get total number of songs in playlist

        Returns:
            int: Number of songs
        """
        return len(self.songs)

    def to_dict(self, include_songs=False):
        """
        Convert playlist to dictionary

        Args:
            include_songs (bool): Whether to include songs in the response

        Returns:
            dict: Playlist data
        """
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_public': self.is_public,
            'cover_image': self.cover_image,
            'user_id': self.user_id,
            'song_count': self.get_song_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_songs:
            # Sort songs by order in playlist
            sorted_playlist_songs = sorted(self.playlist_songs, key=lambda ps: ps.order)
            data['songs'] = [
                {
                    **ps.song.to_dict(),
                    'order': ps.order,
                    'added_at': ps.added_at.isoformat() if ps.added_at else None
                }
                for ps in sorted_playlist_songs
            ]

        return data

    def to_dict_with_user(self):
        """
        Convert playlist to dictionary including user info

        Returns:
            dict: Playlist data with user
        """
        data = self.to_dict()
        if self.user:
            data['user'] = self.user.get_public_profile()
        return data
