# Playlist Cover Images Update

## Overview
Updated the playlist system to store and display the actual uploaded images used to generate playlists, replacing the previous colored square backgrounds.

## Changes Made

### 1. Image Storage ([src/app.py:293-311](src/app.py#L293-L311))

**Added permanent image storage:**
```python
# Save uploaded image to a temporary file for AI processing
with tempfile.NamedTemporaryFile(delete=False, suffix=...) as tmp_file:
    image_file.save(tmp_file.name)
    temp_image_path = tmp_file.name

# Save a permanent copy for the playlist cover
permanent_filename = f"{uuid.uuid4()}{os.path.splitext(image_file.filename)[1]}"
permanent_image_dir = os.path.join(_base_dir, "static", "playlist_covers")
os.makedirs(permanent_image_dir, exist_ok=True)
permanent_image_path = os.path.join(permanent_image_dir, permanent_filename)

# Copy temp file to permanent location
shutil.copy2(temp_image_path, permanent_image_path)

# Store relative path for templates
cover_image_url = f"/playlist_covers/{permanent_filename}"
```

**What it does:**
- Saves uploaded images to `static/playlist_covers/` directory
- Generates unique filename using UUID to prevent conflicts
- Preserves original file extension (jpg, png, etc.)
- Creates relative URL path for use in templates

### 2. Database Integration ([src/app.py:397-402](src/app.py#L397-L402))

**Updated playlist creation to include cover image:**
```python
db_playlist = Playlist(
    name=playlist_name,
    description=playlist_description,
    is_public=False,
    cover_image=cover_image_url,  # New field
    user_id=user_id
)
```

**Database field:**
- The `Playlist` model already has a `cover_image` field (Text type)
- Stores the URL path: `/playlist_covers/{uuid}.jpg`
- Field is nullable (old playlists without images still work)

### 3. Template Display Update ([templates/playlists.html:23-36](templates/playlists.html#L23-L36))

**Before:**
```jinja2
{% set accent_colors = ['#1db954', '#ff477e', ...] %}
{% for playlist in user_playlists %}
  {% set accent_color = accent_colors[loop.index0 % accent_colors|length] %}
  <a class="playlist-card" style="--playlist-accent: {{ accent_color }};">
    <div class="playlist-cover">
      <span class="playlist-cover-chip">{{ playlist.name[:30] }}...</span>
    </div>
  </a>
{% endfor %}
```

**After:**
```jinja2
{% for playlist in user_playlists %}
  <a class="playlist-card" data-playlist-id="{{ playlist.id }}">
    <div class="playlist-cover"
         {% if playlist.cover_image %}
         style="background-image: url('{{ playlist.cover_image }}');
                background-size: cover;
                background-position: center;"
         {% endif %}>
      {% if not playlist.cover_image %}
      <span class="playlist-cover-chip">{{ playlist.name[:30] }}...</span>
      {% endif %}
    </div>
  </a>
{% endfor %}
```

**What changed:**
- Removed accent color cycling
- Display uploaded image as background when available
- Fallback to text chip for playlists without images
- Image scales to fill card with proper centering

## File Structure

```
IBMRS/
├── static/
│   ├── css/
│   └── playlist_covers/          # New directory (auto-created)
│       ├── uuid1.jpg
│       ├── uuid2.png
│       └── uuid3.jpg
├── src/
│   └── app.py                    # Updated image handling
└── templates/
    └── playlists.html            # Updated display logic
```

## User Experience

### Creating a Playlist
1. User uploads an image (e.g., `sunset.jpg`)
2. Image is saved to `static/playlist_covers/a1b2c3d4-...-xyz.jpg`
3. AI generates playlist based on image
4. Playlist saved to database with `cover_image` = `/playlist_covers/a1b2c3d4-...-xyz.jpg`

### Viewing Playlists
1. User visits `/playlists`
2. Template loops through user's playlists
3. For each playlist:
   - **With cover image:** Displays uploaded photo as background
   - **Without cover image:** Shows text chip (backward compatible)

### Example Display

```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ [Sunset Photo]  │ │ [City Photo]    │ │  Urban Mix      │
│                 │ │                 │ │  (no image)     │
│ Beach Vibes     │ │ City Nights     │ │                 │
│ 12 tracks       │ │ 8 tracks        │ │ 15 tracks       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Technical Details

### Image Handling
- **Format Support:** All formats supported by Flask/PIL (jpg, png, gif, webp)
- **Naming Convention:** `{uuid4()}.{original_extension}`
- **Storage Location:** `static/playlist_covers/`
- **URL Access:** `/playlist_covers/{filename}`

### Flask Static File Serving
```python
app = Flask(__name__,
            static_folder=os.path.join(_base_dir, "static"),
            static_url_path="/")
```
- Static files served from `/static` directory
- Accessible at root URL path `/`
- Images available at `/playlist_covers/filename.jpg`

### Database Schema
```python
# Playlist model
cover_image = Column(Text, nullable=True)  # Stores URL path
```

### Backwards Compatibility
- Old playlists without `cover_image` still display correctly
- Template checks `{% if playlist.cover_image %}` before rendering
- Fallback to text chip ensures graceful degradation

## Benefits

1. **Visual Identity:** Each playlist has unique visual representation
2. **Context Preservation:** See the image that inspired the playlist
3. **Better UX:** More engaging than colored squares
4. **Persistent Storage:** Images saved permanently (not regenerated)
5. **Scalable:** UUID naming prevents filename conflicts
6. **Backward Compatible:** Works with existing playlists

## Testing

### Verify the Update Works

1. **Start the app:**
   ```bash
   python src/app.py
   ```

2. **Create a new playlist:**
   - Visit `http://127.0.0.1:5555/playlists`
   - Click the "+" button
   - Upload an image (jpg, png, etc.)
   - Wait for playlist generation

3. **Check the results:**
   - Playlist card should display your uploaded image
   - Image should fill the card with proper scaling
   - Image should be centered and cropped to fit

4. **Verify file storage:**
   ```bash
   ls -la static/playlist_covers/
   ```
   - Should see image files with UUID names
   - Example: `a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6.jpg`

5. **Check database:**
   ```sql
   SELECT name, cover_image FROM playlists;
   ```
   - Should see `/playlist_covers/{uuid}.jpg` in cover_image column

## Troubleshooting

### Images Not Displaying

**Problem:** Playlist cards show text chips instead of images

**Solutions:**
1. Check if `static/playlist_covers/` directory exists:
   ```bash
   ls -la static/playlist_covers/
   ```

2. Verify image files are in the directory

3. Check browser console for 404 errors

4. Verify database has correct path:
   ```python
   # Should be: /playlist_covers/filename.jpg
   # Not: static/playlist_covers/filename.jpg
   ```

### Permission Errors

**Problem:** Can't save images to static directory

**Solution:**
```bash
chmod 755 static/
mkdir -p static/playlist_covers
chmod 755 static/playlist_covers
```

### Large File Sizes

**Problem:** Images are too large, slowing down page load

**Future Enhancement:**
- Add image compression/resizing on upload
- Create thumbnails for playlist cards
- Lazy load images as user scrolls

## Future Enhancements

### Image Optimization
```python
from PIL import Image

def optimize_playlist_cover(image_path):
    img = Image.open(image_path)
    # Resize to 500x500 for consistency
    img.thumbnail((500, 500), Image.Resampling.LANCZOS)
    # Compress with quality 85
    img.save(image_path, optimize=True, quality=85)
```

### Default Cover Images
```python
# If no image uploaded, use default based on genre
default_covers = {
    'rock': '/static/defaults/rock.jpg',
    'pop': '/static/defaults/pop.jpg',
    'chill': '/static/defaults/chill.jpg'
}
```

### Image Upload Validation
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

### CDN Integration
```python
# For production: Upload to AWS S3 or Cloudinary
import cloudinary
cloudinary.uploader.upload(temp_image_path,
                          public_id=f"playlist_covers/{playlist_id}")
```

## Summary

The playlist system now preserves and displays the uploaded images used to generate playlists. This provides better visual context and a more engaging user experience while maintaining backward compatibility with existing playlists.

**Key Files Modified:**
- [src/app.py](src/app.py) - Image storage and database save
- [templates/playlists.html](templates/playlists.html) - Display logic

**New Directory:**
- `static/playlist_covers/` - Permanent image storage
