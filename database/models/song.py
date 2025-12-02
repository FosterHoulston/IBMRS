"""
Song model for Toonify application
Music tracks (from Spotify or custom)
"""
from sqlalchemy import Column, String, Text, Integer, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from database.config import Base
import uuid
from datetime import datetime


class Song(Base):
    __tablename__ = 'songs'

    # Primary key
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Spotify integration
    spotify_track_id = Column(String(255), unique=True, nullable=True, index=True, comment='Spotify track ID for tracks imported from Spotify')

    # Song metadata
    title = Column(String(500), nullable=False, index=True)
    artist = Column(String(500), nullable=False, index=True)
    album = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True, comment='Duration in seconds')
    genre = Column(String(100), nullable=True, index=True)

    # Media URLs
    audio_url = Column(Text, nullable=False, comment='Spotify URI or direct audio URL')
    thumbnail_url = Column(Text, nullable=True, comment='Album artwork or track thumbnail')
    preview_url = Column(Text, nullable=True, comment='Spotify 30-second preview URL')

    # Additional metadata
    release_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    playlists = relationship('Playlist', secondary='playlist_songs', back_populates='songs', overlaps="playlist_songs")
    playlist_songs = relationship('PlaylistSong', back_populates='song', cascade='all, delete-orphan', overlaps="playlists,songs")

    def __repr__(self):
        return f"<Song(id={self.id}, title={self.title}, artist={self.artist})>"

    def get_formatted_duration(self):
        """
        Format duration from seconds to MM:SS

        Returns:
            str: Formatted duration (e.g., "3:45")
        """
        if not self.duration:
            return "0:00"
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

    def is_spotify_track(self):
        """
        Check if song is from Spotify

        Returns:
            bool: True if song has Spotify track ID
        """
        return bool(self.spotify_track_id)

    def to_dict(self):
        """
        Convert song to dictionary

        Returns:
            dict: Song data
        """
        return {
            'id': self.id,
            'spotify_track_id': self.spotify_track_id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'duration_formatted': self.get_formatted_duration(),
            'genre': self.genre,
            'audio_url': self.audio_url,
            'thumbnail_url': self.thumbnail_url,
            'preview_url': self.preview_url,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'is_spotify_track': self.is_spotify_track(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_dict_with_playlists(self):
        """
        Convert song to dictionary including playlist info

        Returns:
            dict: Song data with playlists
        """
        data = self.to_dict()
        data['playlists'] = [
            {
                'id': ps.playlist.id,
                'name': ps.playlist.name,
                'order': ps.order,
                'added_at': ps.added_at.isoformat() if ps.added_at else None
            }
            for ps in self.playlist_songs
        ]
        return data
