"""
PlaylistSong association table for Toonify application
Many-to-many relationship between Playlists and Songs
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from database.config import Base
import uuid
from datetime import datetime


class PlaylistSong(Base):
    __tablename__ = 'playlist_songs'

    # Primary key
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    playlist_id = Column(CHAR(36), ForeignKey('playlists.id', ondelete='CASCADE'), nullable=False, index=True)
    song_id = Column(CHAR(36), ForeignKey('songs.id', ondelete='CASCADE'), nullable=False, index=True)

    # Song order in playlist
    order = Column(Integer, default=0, nullable=False, comment='Position of song in the playlist (0-indexed)')

    # Timestamp
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='Timestamp when the song was added to the playlist')

    # Relationships
    playlist = relationship('Playlist', back_populates='playlist_songs', overlaps="playlists,songs")
    song = relationship('Song', back_populates='playlist_songs', overlaps="playlists,songs")

    # Constraints
    __table_args__ = (
        UniqueConstraint('playlist_id', 'song_id', name='playlist_song_unique'),
        Index('idx_playlist_order', 'playlist_id', 'order'),
    )

    def __repr__(self):
        return f"<PlaylistSong(playlist_id={self.playlist_id}, song_id={self.song_id}, order={self.order})>"

    def get_formatted_added_at(self):
        """
        Get formatted timestamp for when song was added

        Returns:
            str: Formatted date string
        """
        if not self.added_at:
            return None
        return self.added_at.strftime('%b %d, %Y at %I:%M %p')

    def to_dict(self):
        """
        Convert playlist_song to dictionary

        Returns:
            dict: PlaylistSong data
        """
        return {
            'id': self.id,
            'playlist_id': self.playlist_id,
            'song_id': self.song_id,
            'order': self.order,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'added_at_formatted': self.get_formatted_added_at()
        }

    def to_dict_with_song(self):
        """
        Convert playlist_song to dictionary including song info

        Returns:
            dict: PlaylistSong data with song details
        """
        data = self.to_dict()
        if self.song:
            data['song'] = self.song.to_dict()
        return data

    def to_dict_with_playlist(self):
        """
        Convert playlist_song to dictionary including playlist info

        Returns:
            dict: PlaylistSong data with playlist details
        """
        data = self.to_dict()
        if self.playlist:
            data['playlist'] = {
                'id': self.playlist.id,
                'name': self.playlist.name,
                'cover_image': self.playlist.cover_image
            }
        return data
