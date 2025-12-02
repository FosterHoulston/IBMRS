# Toonify Database - SQLAlchemy Setup

This directory contains the complete SQLAlchemy database setup for the Toonify music playlist application with Spotify OAuth integration.

## Database Structure

- **Database Name:** toonifyDB
- **Schema:** Toonify
- **Type:** MySQL
- **Host:** localhost
- **Port:** 55005

## Models

### User (`database/models/user.py`)
Stores Spotify OAuth user information:
- `id` (UUID CHAR(36)) - Primary key
- `spotify_id` (String) - Unique Spotify user ID
- `spotify_access_token` (Text) - OAuth access token (encrypt in production!)
- `spotify_refresh_token` (Text) - OAuth refresh token (encrypt in production!)
- `email` (String) - User email from Spotify
- `display_name` (String) - Display name from Spotify
- `profile_image` (Text) - Spotify avatar URL
- `country` (String) - Country code (ISO 3166-1 alpha-2)
- `spotify_uri` (String) - Spotify user URI
- `last_login` (DateTime) - Last login timestamp
- `created_at`, `updated_at`, `deleted_at` (DateTime) - Timestamps

**Methods:**
- `update_spotify_tokens(access_token, refresh_token)` - Update OAuth tokens
- `get_public_profile()` - Get safe user profile for API responses
- `to_dict()` - Convert to dictionary

### Playlist (`database/models/playlist.py`)
User-created playlists:
- `id` (UUID CHAR(36)) - Primary key
- `name` (String) - Playlist name
- `description` (Text) - Playlist description
- `is_public` (Boolean) - Public/private flag
- `cover_image` (Text) - Cover image URL
- `user_id` (UUID) - Foreign key to User
- `created_at`, `updated_at`, `deleted_at` (DateTime) - Timestamps

**Methods:**
- `get_song_count()` - Get total number of songs
- `to_dict(include_songs=False)` - Convert to dictionary
- `to_dict_with_user()` - Convert with user info

### Song (`database/models/song.py`)
Music tracks (from Spotify or custom):
- `id` (UUID CHAR(36)) - Primary key
- `spotify_track_id` (String) - Spotify track ID (nullable, unique)
- `title` (String) - Song title
- `artist` (String) - Artist name
- `album` (String) - Album name
- `duration` (Integer) - Duration in seconds
- `genre` (String) - Music genre
- `audio_url` (Text) - Spotify URI or audio URL
- `thumbnail_url` (Text) - Album artwork URL
- `preview_url` (Text) - Spotify 30s preview URL
- `release_date` (Date) - Release date
- `created_at`, `updated_at` (DateTime) - Timestamps

**Methods:**
- `get_formatted_duration()` - Format duration as MM:SS
- `is_spotify_track()` - Check if from Spotify
- `to_dict()` - Convert to dictionary
- `to_dict_with_playlists()` - Convert with playlist info

### PlaylistSong (`database/models/playlist_song.py`)
Many-to-many relationship between Playlists and Songs:
- `id` (UUID CHAR(36)) - Primary key
- `playlist_id` (UUID) - Foreign key to Playlist
- `song_id` (UUID) - Foreign key to Song
- `order` (Integer) - Song position in playlist (0-indexed)
- `added_at` (DateTime) - Timestamp when added

**Methods:**
- `get_formatted_added_at()` - Get formatted timestamp
- `to_dict()` - Convert to dictionary
- `to_dict_with_song()` - Convert with song details
- `to_dict_with_playlist()` - Convert with playlist details

## Relationships

- User → Playlists (One-to-Many)
- Playlist → User (Many-to-One)
- Playlist ↔ Songs (Many-to-Many via PlaylistSong)

## Installation

1. **Update `.env` file with database credentials:**
   ```bash
   # In /Users/pdavis/Documents/GitHub/Toonify/IBMRS/.env
   # Add these lines:

   DB_NAME=toonifyDB
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=55005
   DB_LOGGING=False
   ```

2. **Install Python dependencies:**
   ```bash
   cd /Users/pdavis/Documents/GitHub/Toonify/IBMRS
   pip install -r requirements.txt
   ```

3. **Create the database:**
   ```bash
   python database/scripts/create_database.py
   ```

4. **Initialize tables:**
   ```bash
   python database/scripts/init_db.py
   ```

5. **Seed test data:**
   ```bash
   python database/seeders/seed.py
   ```

## Quick Setup

To set up everything at once:

```bash
cd /Users/pdavis/Documents/GitHub/Toonify/IBMRS

# Install dependencies
pip install -r requirements.txt

# Create database and tables, then seed data
python database/scripts/create_database.py && python database/seeders/seed.py
```

## Available Scripts

### Create Database
```bash
python database/scripts/create_database.py
```
Creates the `toonifyDB` database if it doesn't exist.

### Initialize Tables
```bash
python database/scripts/init_db.py
```
Creates all database tables based on models.

### Seed Data
```bash
python database/seeders/seed.py
```
Drops existing tables, recreates them, and populates with test data:
- 5 users with mock Spotify accounts
- 20 songs (various genres from classics to modern hits)
- 10 playlists (Workout Mix, Rock Classics, Party Hits, etc.)
- Playlist-song relationships

### Reset Database
```bash
python database/scripts/reset_db.py
```
**WARNING:** Drops all tables and recreates them (deletes all data).

## Usage Examples

### Import models in your Flask app:

```python
from database.config import SessionLocal, get_db
from database.models import User, Playlist, Song, PlaylistSong

# Create a database session
db = SessionLocal()

# Find user by Spotify ID
user = db.query(User).filter(User.spotify_id == 'spotify_user_001').first()

# Get user's playlists
playlists = user.playlists

# Get playlist with songs
playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
playlist_data = playlist.to_dict(include_songs=True)

# Add song to playlist
playlist_song = PlaylistSong(
    playlist_id=playlist.id,
    song_id=song.id,
    order=0
)
db.add(playlist_song)
db.commit()

# Update user's Spotify tokens
user.update_spotify_tokens(access_token, refresh_token)
db.commit()

# Close session
db.close()
```

### Using with Flask routes:

```python
from flask import Flask, jsonify
from database.config import get_db
from database.models import User, Playlist

app = Flask(__name__)

@app.route('/users/<user_id>/playlists')
def get_user_playlists(user_id):
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        playlists = [p.to_dict() for p in user.playlists]
        return jsonify({'playlists': playlists})
    finally:
        db.close()
```

## Configuration (`database/config.py`)

The configuration file provides:
- `engine` - SQLAlchemy engine with connection pooling
- `SessionLocal` - Session factory for creating database sessions
- `db_session` - Scoped session for thread safety
- `Base` - Base class for all models
- `get_db()` - Dependency for getting database sessions
- `init_db()` - Initialize all tables
- `drop_db()` - Drop all tables
- `test_connection()` - Test database connection

## Security Notes

⚠️ **IMPORTANT:**
- In production, **encrypt** `spotify_access_token` and `spotify_refresh_token` fields
- Never commit `.env` file with real credentials
- Use environment variables for all sensitive configuration
- Implement proper OAuth token rotation
- Add rate limiting and validation on all endpoints
- Use prepared statements (SQLAlchemy does this by default)
- Validate all user inputs before database operations

## File Structure

```
IBMRS/database/
├── models/
│   ├── __init__.py          # Model exports
│   ├── user.py              # User model with Spotify OAuth
│   ├── playlist.py          # Playlist model
│   ├── song.py              # Song model
│   └── playlist_song.py     # Junction table model
├── seeders/
│   └── seed.py              # Seed data script
├── scripts/
│   ├── create_database.py   # Database creation script
│   ├── init_db.py           # Initialize tables script
│   └── reset_db.py          # Reset database script
├── config.py                # SQLAlchemy configuration
└── README.md                # This file
```

## Environment Variables

Add these to your `.env` file in the IBMRS directory:

```bash
# Database Configuration
DB_NAME=toonifyDB
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_HOST=localhost
DB_PORT=55005
DB_LOGGING=False  # Set to True for SQL query logging
```

## Troubleshooting

### Connection Issues

If you get connection errors:
1. Verify MySQL is running on port 55005
2. Check credentials in `.env`
3. Ensure database user has proper permissions
4. Test connection: `mysql -h localhost -P 55005 -u root -p`

### Port Already in Use

If port 55005 is in use, update `DB_PORT` in `.env` to a different port.

### Import Errors

If you get import errors when running scripts:
```bash
# Make sure you're in the IBMRS directory
cd /Users/pdavis/Documents/GitHub/Toonify/IBMRS
python database/seeders/seed.py
```

### Migration Errors

If tables already exist and you want to recreate them:
```bash
python database/scripts/reset_db.py  # WARNING: Deletes all data
python database/seeders/seed.py      # Repopulate with test data
```

## Development

### Adding New Models

1. Create model file in `database/models/`
2. Import and add to `database/models/__init__.py`
3. Run `python database/scripts/init_db.py` to create tables
4. Update seed script if needed

### Modifying Existing Models

1. Update model definition in `database/models/`
2. Run `python database/scripts/reset_db.py` to recreate tables
3. Run `python database/seeders/seed.py` to repopulate data

For production, consider using Alembic for database migrations instead of dropping/recreating tables.

## Next Steps

1. Update MySQL password in `.env`
2. Run installation scripts
3. Integrate models into your Flask application
4. Implement Spotify OAuth flow
5. Create API endpoints for playlist management

## License

This database setup is part of the Toonify project.
