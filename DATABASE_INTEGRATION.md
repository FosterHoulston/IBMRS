# Database Integration Summary

## ✅ Completed Integration Steps

### 1. Database Setup
- ✅ Created MySQL database `toonifyDB` on port 55005
- ✅ Initialized all tables (users, playlists, songs, playlist_songs)
- ✅ Seeded with test data (5 users, 20 songs, 10 playlists)

### 2. Flask App Integration
- ✅ Added database imports to `src/app.py`
- ✅ Database connection test on app startup
- ✅ User creation/update after Spotify OAuth
- ✅ Playlist and song saving after AI generation
- ✅ API endpoints for querying database

## 📊 Database Schema

### Tables Created
1. **users** - Spotify OAuth user information
2. **playlists** - User-created playlists
3. **songs** - Music tracks (from Spotify or custom)
4. **playlist_songs** - Many-to-many junction table

### Relationships
- User → Playlists (One-to-Many)
- Playlist ↔ Songs (Many-to-Many)

## 🔧 Integration Points

### 1. User Authentication (`spotify_callback`)
**Location:** [src/app.py:386-425](src/app.py#L386-L425)

When a user logs in via Spotify:
- Checks if user exists in database by `spotify_id`
- **If exists:** Updates tokens, email, display_name, profile_image
- **If new:** Creates new user record
- Stores `user_id` in session for future requests

### 2. Playlist Creation (`create_playlist_from_image`)
**Location:** [src/app.py:282-334](src/app.py#L282-L334)

After creating a playlist on Spotify:
- Saves playlist to database with name, description, user_id
- Saves each song (checks for duplicates by spotify_track_id)
- Creates playlist_song links with proper ordering
- All data persisted for future queries

### 3. New API Endpoints

#### GET `/api/my-playlists`
**Location:** [src/app.py:203-219](src/app.py#L203-L219)

Returns all playlists for the authenticated user:
```json
{
  "playlists": [
    {
      "id": "uuid",
      "name": "Playlist Name",
      "songs": [...],
      "song_count": 10,
      ...
    }
  ],
  "count": 5
}
```

#### GET `/api/playlists/<playlist_id>`
**Location:** [src/app.py:222-233](src/app.py#L222-L233)

Returns detailed info for a specific playlist:
```json
{
  "id": "uuid",
  "name": "Playlist Name",
  "description": "...",
  "songs": [
    {
      "id": "uuid",
      "title": "Song Title",
      "artist": "Artist Name",
      "order": 0,
      "added_at": "2024-12-01T10:30:00"
    }
  ]
}
```

## 🎯 What Works Now

### User Management
- ✅ Users automatically created/updated on Spotify login
- ✅ OAuth tokens stored and refreshed
- ✅ User profile data synced from Spotify

### Playlist Management
- ✅ Playlists saved to database when created
- ✅ Songs deduplicated (no duplicates in database)
- ✅ Song order preserved in playlists
- ✅ Query user's playlist history

### Data Persistence
- ✅ All playlists and songs saved to MySQL
- ✅ Can query playlist history across sessions
- ✅ Can build analytics/stats on user activity

## 📝 Usage Examples

### Frontend: Fetch User's Playlists
```javascript
fetch('/api/my-playlists')
  .then(res => res.json())
  .then(data => {
    console.log(`User has ${data.count} playlists`);
    data.playlists.forEach(playlist => {
      console.log(`${playlist.name}: ${playlist.song_count} songs`);
    });
  });
```

### Frontend: Get Playlist Details
```javascript
fetch('/api/playlists/PLAYLIST_ID')
  .then(res => res.json())
  .then(playlist => {
    console.log(playlist.name);
    playlist.songs.forEach(song => {
      console.log(`${song.order + 1}. ${song.title} - ${song.artist}`);
    });
  });
```

### Python: Direct Database Query
```python
from database.config import SessionLocal
from database.models import User

db = SessionLocal()
user = db.query(User).filter(User.email == 'user@example.com').first()
print(f"User has {len(user.playlists)} playlists")
db.close()
```

## 🔐 Security Notes

### Current Implementation
- ✅ Database credentials in `.env` (not committed)
- ✅ Session-based authentication
- ⚠️  OAuth tokens stored in plain text

### Recommended Improvements
1. **Encrypt OAuth tokens** in production:
   ```python
   from cryptography.fernet import Fernet
   # Encrypt before storing
   ```

2. **Add user authentication middleware**:
   ```python
   def require_auth(f):
       @wraps(f)
       def decorated(*args, **kwargs):
           if 'user_id' not in session:
               return jsonify({'error': 'Unauthorized'}), 401
           return f(*args, **kwargs)
       return decorated
   ```

3. **Rate limiting** on API endpoints
4. **Input validation** on all database writes

## 🚀 Next Steps (Optional Enhancements)

### 1. Add Playlist Deletion
```python
@app.route("/api/playlists/<playlist_id>", methods=["DELETE"])
def delete_playlist(playlist_id):
    # Soft delete by setting deleted_at timestamp
    pass
```

### 2. Add User Statistics
```python
@app.route("/api/stats")
def get_user_stats():
    # Return total playlists, total songs, most used genres, etc.
    pass
```

### 3. Add Search
```python
@app.route("/api/search")
def search_songs():
    query = request.args.get('q')
    # Search songs by title or artist
    pass
```

### 4. Add Playlist Sharing
```python
@app.route("/api/playlists/<playlist_id>/share")
def share_playlist(playlist_id):
    # Toggle is_public flag
    pass
```

## 📚 Database Commands

### View Test Data
```bash
# Connect to MySQL
mysql -h localhost -P 55005 -u root -p

# Use database
USE toonifyDB;

# View users
SELECT email, display_name FROM users;

# View playlists
SELECT p.name, u.email, COUNT(ps.song_id) as song_count
FROM playlists p
JOIN users u ON p.user_id = u.id
LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id
GROUP BY p.id;
```

### Reset Database
```bash
cd /Users/pdavis/Documents/GitHub/Toonify/IBMRS
python database/scripts/reset_db.py
python database/seeders/seed.py
```

## ✅ Integration Complete!

The database is fully integrated with your Flask app. All user activity (logins, playlist creation) is now automatically saved to MySQL.

### Test the Integration:
1. Start the app: `python src/app.py`
2. Visit: `http://127.0.0.1:5555`
3. Login with Spotify
4. Create a playlist from an image
5. Check: `http://127.0.0.1:5555/api/my-playlists`

You should see your created playlists with all song details!
