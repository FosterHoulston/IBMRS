# Playlist Display Updates

## Overview
Updated the playlists page to dynamically display user's playlists from the database instead of showing hardcoded mock data.

## Changes Made

### 1. Backend Route Update ([src/app.py:218-246](src/app.py#L218-L246))

**Before:**
```python
@app.route("/playlists")
def playlists():
  return render_template("playlists.html")
```

**After:**
```python
@app.route("/playlists")
def playlists():
  """Render playlists page with user's playlists from database"""
  user_playlists = []
  user_id = session.get('user_id')

  if user_id:
    db = SessionLocal()
    try:
      user = db.query(User).filter(User.id == user_id).first()
      if user:
        # Get all non-deleted playlists with song counts
        user_playlists = [
          {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'song_count': len([ps for ps in p.playlist_songs if ps.song]),
            'cover_image': p.cover_image,
            'created_at': p.created_at.isoformat() if p.created_at else None
          }
          for p in user.playlists if not p.deleted_at
        ]
        # Sort by most recent first
        user_playlists.sort(key=lambda x: x['created_at'] or '', reverse=True)
    finally:
      db.close()

  return render_template("playlists.html", user_playlists=user_playlists)
```

**What it does:**
- Queries database for user's playlists
- Calculates song count for each playlist
- Sorts playlists by creation date (newest first)
- Passes data to template

### 2. Template Update ([templates/playlists.html](templates/playlists.html))

**Replaced:** 100+ lines of hardcoded playlist HTML

**With:** Dynamic Jinja2 template that:
- Loops through `user_playlists` from database
- Shows message if no playlists exist
- Displays playlist name and song count
- Uses rotating accent colors for visual variety
- Keeps "New playlist" card for creating new playlists

**Key Features:**
```jinja2
{% if user_playlists %}
  {% set accent_colors = ['#1db954', '#ff477e', '#45caff', ...] %}
  {% for playlist in user_playlists %}
    <!-- Display each playlist -->
    <a class="playlist-card" style="--playlist-accent: {{ accent_color }};">
      <h2>{{ playlist.name }}</h2>
      <p>{{ playlist.song_count }} tracks</p>
    </a>
  {% endfor %}
{% else %}
  <!-- Show "Create your first playlist" message -->
{% endif %}
```

### 3. JavaScript Enhancement ([templates/playlists.html:128-153](templates/playlists.html#L128-L153))

**Updated upload handler to:**
- Reload page after successful playlist creation (shows updated database data)
- Added click handler to "New playlist" card
- Simplified code by removing manual card creation (now handled by page reload)

**Before:**
```javascript
const data = await uploadImage(file);
if (grid) {
  const card = createCard(data);
  grid.prepend(card);
}
```

**After:**
```javascript
const data = await uploadImage(file);
// Reload page to show updated playlist from database
window.location.reload();
```

## User Experience

### Empty State
When user has no playlists:
```
┌─────────────────────────────────────┐
│  No playlists yet                   │
│  Create Your First Playlist         │
│  Click the + button above...        │
└─────────────────────────────────────┘
```

### With Playlists
```
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Urban City │ │ Rock Mix   │ │ Chill Out  │
│ 8 tracks   │ │ 12 tracks  │ │ 5 tracks   │
└────────────┘ └────────────┘ └────────────┘
┌────────────┐
│ New        │  ← Always shown at end
│ playlist   │
└────────────┘
```

## Benefits

1. **Real Data:** Shows actual playlists from database
2. **Live Updates:** Page reloads after creating playlist, showing new data
3. **Song Counts:** Displays accurate track count per playlist
4. **Visual Variety:** Rotating accent colors for each playlist card
5. **Empty State:** Helpful message when no playlists exist
6. **Sorted:** Most recent playlists shown first

## Technical Details

### Data Flow
1. User visits `/playlists`
2. Backend queries database for user's playlists
3. Template renders playlist cards dynamically
4. User creates new playlist → page reloads → shows updated list

### Database Query
```python
user.playlists  # SQLAlchemy relationship
  → filters deleted playlists
  → counts songs via playlist_songs relationship
  → sorts by created_at timestamp
```

### Performance
- Single database query per page load
- Efficient relationship loading via SQLAlchemy
- Client-side sorting handled in Python before rendering

## Testing

To verify the changes work:

1. **Empty state:** Login as new user → should see "Create Your First Playlist"
2. **Create playlist:** Upload image → playlist created → page reloads → new playlist appears at top
3. **Multiple playlists:** Create several → should see all in descending order
4. **Song counts:** Verify counts match actual songs in database

## Future Enhancements

Possible improvements:
- Click playlist card to view songs
- Edit/delete playlist functionality
- Playlist cover images from Spotify
- Search/filter playlists
- Infinite scroll for many playlists
- Playlist details modal/page
