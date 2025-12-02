import base64
import hashlib
import os
import secrets
import time
from typing import Optional
from urllib.parse import urlencode
from LlamaClient import LlamaClient

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for, jsonify

# Database imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.config import SessionLocal, test_connection
from database.models import User, Playlist, Song, PlaylistSong

# Use absolute paths for template and static folders
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
            template_folder=os.path.join(_base_dir, "templates"),
            static_folder=os.path.join(_base_dir, "static"),
            static_url_path="/")

load_dotenv()

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

# Test database connection on startup
if test_connection():
    print("✓ Database connected successfully")
else:
    print("⚠️  Database connection failed - check your .env settings")

SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_REDIRECT_URI = os.getenv("REDIRECT_URI")
SPOTIFY_SCOPES = "user-read-email user-read-private playlist-read-private playlist-modify-public playlist-modify-private"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"
_PENDING_AUTH = {}
_PENDING_AUTH_TTL_SECONDS = 600


def _generate_code_verifier(length: int = 64) -> str:
  """Create a high-entropy string for Proof Key for Code Exchange."""
  verifier = base64.urlsafe_b64encode(os.urandom(length)).decode("utf-8").rstrip("=")
  # Ensure Spotify's min length of 43 characters.
  if len(verifier) < 43:
    verifier = (verifier + verifier[::-1])[:43]
  return verifier[:128]


def _generate_code_challenge(code_verifier: str) -> str:
  hashed = hashlib.sha256(code_verifier.encode("utf-8")).digest()
  return base64.urlsafe_b64encode(hashed).decode("utf-8").rstrip("=")


def _store_token(token_payload: dict) -> None:
  expires_at = time.time() + token_payload.get("expires_in", 3600)
  session["spotify_token"] = {
      "access_token": token_payload.get("access_token"),
      "refresh_token": token_payload.get("refresh_token"),
      "expires_at": expires_at,
  }


def _fetch_spotify_profile(access_token: str) -> Optional[dict]:
  headers = {"Authorization": f"Bearer {access_token}"}
  response = requests.get(f"{SPOTIFY_API_BASE}/me", headers=headers, timeout=10)
  if response.status_code == 200:
    data = response.json()
    return {
        "display_name": data.get("display_name") or data.get("id"),
        "id": data.get("id"),
        "email": data.get("email"),
        "images": data.get("images", []),
    }
  return None


def _ensure_access_token() -> Optional[str]:
  """Return a valid access token, refreshing with the stored refresh_token if expired."""
  token = session.get("spotify_token")
  if not token:
    print("⚠️  No Spotify token in session")
    return None

  now = time.time()
  if token.get("expires_at") and token["expires_at"] - now > 60:
    return token.get("access_token")

  refresh_token = token.get("refresh_token")
  if not refresh_token:
    print("⚠️  No refresh token available")
    return token.get("access_token")

  print("🔄 Refreshing access token...")
  data = {
      "grant_type": "refresh_token",
      "refresh_token": refresh_token,
      "client_id": SPOTIFY_CLIENT_ID,
  }
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  resp = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers, timeout=10)
  if resp.status_code != 200:
    print(f"⚠️  Token refresh failed: {resp.status_code}")
    return token.get("access_token")

  refreshed = resp.json()
  # Spotify may not return a new refresh token; reuse the existing one.
  if "refresh_token" not in refreshed:
    refreshed["refresh_token"] = refresh_token
  _store_token(refreshed)
  print("✓ Access token refreshed")
  return refreshed.get("access_token")


def _mock_pipeline_from_image(_image_file) -> dict:
  """Placeholder pipeline call. Replace with real integration when available."""
  # This uses fixed data while the real AI pipeline is being wired up.
  return {
      "playlist_name": "Neon Skyline",
      "descriptors": ["moody", "city", "night"],
      "songs": [
          {"name": "Blinding Lights", "artist": "The Weeknd"},
          {"name": "Midnight City", "artist": "M83"},
          {"name": "Electric Feel", "artist": "MGMT"},
          {"name": "Lose Yourself to Dance", "artist": "Daft Punk"},
          {"name": "The Less I Know The Better", "artist": "Tame Impala"},
      ],
  }


def _spotify_headers(access_token: str) -> dict:
  return {"Authorization": f"Bearer {access_token}"}


def _resolve_track_uri(access_token: str, name: str, artist: Optional[str] = None) -> Optional[str]:
  q = name
  if artist:
    q = f"{name} artist:{artist}"
  params = {"q": q, "type": "track", "limit": 1}
  resp = requests.get(
      f"{SPOTIFY_API_BASE}/search",
      headers=_spotify_headers(access_token),
      params=params,
      timeout=10,
  )
  if resp.status_code != 200:
    return None
  items = resp.json().get("tracks", {}).get("items", [])
  if not items:
    return None
  return items[0].get("uri")


def _create_spotify_playlist(access_token: str, user_id: str, name: str, description: str = "") -> Optional[str]:
  # Validate and sanitize playlist name
  if not name or not name.strip():
    name = "New Playlist"
  name = name.strip()[:100]  # Spotify max: 100 characters

  # Validate and sanitize description
  if description:
    description = description.strip()[:300]  # Spotify max: 300 characters

  payload = {"name": name, "description": description, "public": False}

  print(f"Creating playlist with payload: {payload}")

  # Use /me/playlists instead of /users/{user_id}/playlists (deprecated endpoint)
  resp = requests.post(
      f"{SPOTIFY_API_BASE}/me/playlists",
      headers={**_spotify_headers(access_token), "Content-Type": "application/json"},
      json=payload,
      timeout=10,
  )
  if resp.status_code not in (200, 201):
    print(f"Failed to create playlist. Status: {resp.status_code}, Response: {resp.text}")
    print(f"Request headers: {_spotify_headers(access_token)}")
    print(f"Request payload: {payload}")
    return None
  return resp.json().get("id")


def _add_tracks_to_playlist(access_token: str, playlist_id: str, uris: list[str]) -> bool:
  if not uris:
    return True
  resp = requests.post(
      f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks",
      headers={**_spotify_headers(access_token), "Content-Type": "application/json"},
      json={"uris": uris},
      timeout=10,
  )
  return resp.status_code in (200, 201)

@app.context_processor
def inject_spotify_profile():
  return {"spotify_profile": session.get("spotify_profile")}


@app.route("/")
def index():
  return render_template("index.html")

#@app.route('/login')
#def login():
#    authentication_request_params = {
#        'response_type': 'code',
#        'client_id': client_id,
#        'redirect_uri': redirect_uri,
#        'scope': 'user-read-email'
#    }

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


@app.route("/api/my-playlists")
def get_my_playlists():
  """Get user's playlists from database"""
  user_id = session.get('user_id')
  if not user_id:
    return jsonify({"error": "Not authenticated"}), 401

  db = SessionLocal()
  try:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
      return jsonify({"error": "User not found"}), 404

    playlists = [p.to_dict(include_songs=True) for p in user.playlists if not p.deleted_at]
    return jsonify({"playlists": playlists, "count": len(playlists)})
  finally:
    db.close()


@app.route("/api/playlists/<playlist_id>")
def get_playlist_details(playlist_id):
  """Get detailed playlist info from database"""
  db = SessionLocal()
  try:
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
      return jsonify({"error": "Playlist not found"}), 404

    return jsonify(playlist.to_dict(include_songs=True))
  finally:
    db.close()


@app.route("/api/playlists/from-image", methods=["POST"])
def create_playlist_from_image():
  access_token = _ensure_access_token()
  profile = session.get("spotify_profile")
  if not access_token or not profile:
    return jsonify({"error": "Not authenticated with Spotify."}), 401

  image_file = request.files.get("image")
  if not image_file:
    return jsonify({"error": "Image file is required."}), 400

  # Save uploaded image to a temporary file for processing
  import tempfile
  with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.filename)[1]) as tmp_file:
    image_file.save(tmp_file.name)
    temp_image_path = tmp_file.name

  # Also save a permanent copy for the playlist cover
  import uuid as uuid_lib
  permanent_filename = f"{uuid_lib.uuid4()}{os.path.splitext(image_file.filename)[1]}"
  permanent_image_dir = os.path.join(_base_dir, "static", "playlist_covers")
  os.makedirs(permanent_image_dir, exist_ok=True)
  permanent_image_path = os.path.join(permanent_image_dir, permanent_filename)

  # Copy the temp file to permanent location
  import shutil
  shutil.copy2(temp_image_path, permanent_image_path)

  # Store relative path for use in templates
  cover_image_url = f"/playlist_covers/{permanent_filename}"

  try:
    llamaClient_instance = LlamaClient()
    print("LlamaClient instance created")

    # Call the AI pipeline with the temporary file path
    pipeline_result, descriptors = llamaClient_instance.pipeline(temp_image_path)
    print(f"Pipeline completed. Result type: {type(pipeline_result)}, Descriptors: {descriptors}")

    # Generate playlist name with validation
    if descriptors:
        # Join descriptors and clean up
        playlist_name = " ".join(str(d).strip() for d in descriptors if str(d).strip())

        # Remove newlines and extra whitespace that Spotify doesn't accept
        playlist_name = " ".join(playlist_name.split())

        # Remove any leading text like "Here are 15 keywords..." and get just the actual keywords
        if ":" in playlist_name:
            # Split by colon and take the last part (the actual keywords)
            parts = playlist_name.split(":")
            playlist_name = parts[-1].strip()
    else:
        playlist_name = "New Playlist"

    # Ensure playlist name is not empty and within Spotify's limits (max 100 characters)
    playlist_name = playlist_name.strip()
    if not playlist_name:
        playlist_name = "New Playlist"
    if len(playlist_name) > 100:
        playlist_name = playlist_name[:100].strip()

    print(f"Generated playlist name: '{playlist_name}'")
    print(f"Playlist name length: {len(playlist_name)}")

    # Create the playlist on Spotify.
    if descriptors:
        # Clean descriptors for description (remove newlines and extra whitespace)
        clean_descriptors = [" ".join(str(d).split()) for d in descriptors]
        playlist_description = "Created by IBMRS from an uploaded image. Descriptors: " + ", ".join(clean_descriptors)
    else:
        playlist_description = "Created by IBMRS from an uploaded image."

    # Ensure description doesn't exceed Spotify's limit (300 chars)
    if len(playlist_description) > 300:
        playlist_description = playlist_description[:297] + "..."

    print(f"Playlist description: {playlist_description}")

    playlist_id = _create_spotify_playlist(
        access_token=access_token,
        user_id=profile.get("id"),
        name=playlist_name,
        description=playlist_description,
    )
    print(f"Playlist created with ID: {playlist_id}")

    if not playlist_id:
      return jsonify({"error": "Failed to create playlist on Spotify."}), 502

    # Resolve song URIs and add them.
    track_uris = []
    resolved_tracks = []
    for song in pipeline_result:
      print("Song from pipeline:", song,"Artists:", song.get("artists") if isinstance(song, dict) else None)
      name = song.get("name") if isinstance(song, dict) else None
      artists = song.get("artists") if isinstance(song, dict) else None  # Note: plural "artists"
      if not name:
        continue
      uri = _resolve_track_uri(access_token, name=name, artist=artists)
      if uri:
        track_uris.append(uri)
        resolved_tracks.append({"name": name, "artist": artists, "uri": uri})

    if track_uris:
      added = _add_tracks_to_playlist(access_token, playlist_id, track_uris)
      if not added:
        return jsonify({"error": "Playlist created, but adding tracks failed."}), 502

    # Save playlist and songs to database
    db = SessionLocal()
    try:
        user_id = session.get('user_id')
        if user_id:
            # Create playlist record
            db_playlist = Playlist(
                name=playlist_name,
                description=playlist_description,
                is_public=False,
                cover_image=cover_image_url,
                user_id=user_id
            )
            db.add(db_playlist)
            db.commit()

            # Deduplicate tracks by URI to prevent duplicate playlist entries
            seen_uris = set()
            unique_tracks = []
            for track in resolved_tracks:
                if track['uri'] not in seen_uris:
                    seen_uris.add(track['uri'])
                    unique_tracks.append(track)

            # Add songs to database and link to playlist
            for idx, track in enumerate(unique_tracks):
                # Extract Spotify track ID from URI (format: spotify:track:TRACK_ID)
                spotify_track_id = track['uri'].split(':')[-1] if ':' in track['uri'] else None

                # Check if song exists by Spotify track ID
                song = None
                if spotify_track_id:
                    song = db.query(Song).filter(Song.spotify_track_id == spotify_track_id).first()

                if not song:
                    # Create new song
                    song = Song(
                        spotify_track_id=spotify_track_id,
                        title=track['name'],
                        artist=track.get('artist', 'Unknown Artist'),
                        audio_url=track['uri']
                    )
                    db.add(song)
                    db.commit()

                # Link song to playlist
                playlist_song = PlaylistSong(
                    playlist_id=db_playlist.id,
                    song_id=song.id,
                    order=idx
                )
                db.add(playlist_song)

            db.commit()
            duplicates_removed = len(resolved_tracks) - len(unique_tracks)
            if duplicates_removed > 0:
                print(f"✓ Saved playlist '{playlist_name}' with {len(unique_tracks)} unique songs to database ({duplicates_removed} duplicates removed)")
            else:
                print(f"✓ Saved playlist '{playlist_name}' with {len(unique_tracks)} songs to database")
    except Exception as e:
        print(f"✗ Error saving playlist to database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

    return jsonify(
        {
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
            "descriptors": descriptors,
            "tracks": resolved_tracks,
            "track_count": len(track_uris),
        }
    )
  except Exception as e:
    print(f"Error in create_playlist_from_image: {str(e)}")
    import traceback
    traceback.print_exc()
    return jsonify({"error": f"An error occurred: {str(e)}"}), 500
  finally:
    # Clean up the temporary file
    if os.path.exists(temp_image_path):
      os.unlink(temp_image_path)


@app.route("/auth/login")
def spotify_login():
  if not SPOTIFY_CLIENT_ID or not SPOTIFY_REDIRECT_URI:
    return "Missing Spotify CLIENT_ID or REDIRECT_URI environment variables.", 500

  redirect_uri = SPOTIFY_REDIRECT_URI or url_for("spotify_callback", _external=True)
  code_verifier = _generate_code_verifier()
  code_challenge = _generate_code_challenge(code_verifier)
  state = secrets.token_urlsafe(16)

  session["spotify_code_verifier"] = code_verifier
  session["spotify_auth_state"] = state
  session["spotify_redirect_uri"] = redirect_uri

  _PENDING_AUTH[state] = {
      "code_verifier": code_verifier,
      "redirect_uri": redirect_uri,
      "created_at": time.time(),
  }

  query = urlencode(
      {
          "client_id": SPOTIFY_CLIENT_ID,
          "response_type": "code",
          "redirect_uri": redirect_uri,
          "scope": SPOTIFY_SCOPES,
          "code_challenge_method": "S256",
          "code_challenge": code_challenge,
          "state": state,
      }
  )
  return redirect(f"{SPOTIFY_AUTH_URL}?{query}")


# Support both /auth/callback (documented) and /callback (common default)
@app.route("/auth/callback")
@app.route("/callback")
def spotify_callback():
  error = request.args.get("error")
  if error:
    return f"Spotify authorization failed: {error}", 400

  state = request.args.get("state")
  stored_state = session.pop("spotify_auth_state", None)
  pending_auth = _PENDING_AUTH.pop(state, None) if state else None
  if pending_auth and time.time() - pending_auth.get("created_at", 0) > _PENDING_AUTH_TTL_SECONDS:
    pending_auth = None

  if not state or (stored_state and state != stored_state) or (not stored_state and not pending_auth):
    return "Invalid state parameter.", 400

  redirect_uri = (
      pending_auth.get("redirect_uri")
      if pending_auth
      else session.pop("spotify_redirect_uri", SPOTIFY_REDIRECT_URI)
  )
  code_verifier = (
      pending_auth.get("code_verifier") if pending_auth else session.pop("spotify_code_verifier", None)
  )

  code = request.args.get("code")
  if not code or not code_verifier or not redirect_uri:
    return "Missing authorization code or verifier.", 400

  data = {
      "grant_type": "authorization_code",
      "code": code,
      "redirect_uri": redirect_uri,
      "client_id": SPOTIFY_CLIENT_ID,
      "code_verifier": code_verifier,
  }
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  token_response = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers, timeout=10)
  if token_response.status_code != 200:
    return f"Failed to exchange code: {token_response.text}", 400

  token_payload = token_response.json()
  _store_token(token_payload)

  access_token = token_payload.get("access_token")
  profile = _fetch_spotify_profile(access_token) if access_token else None
  if profile:
    session["spotify_profile"] = profile

    # Save or update user in database
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(User).filter(User.spotify_id == profile['id']).first()

        if user:
            # Update existing user
            user.update_spotify_tokens(
                access_token=access_token,
                refresh_token=token_payload.get('refresh_token')
            )
            user.email = profile.get('email')
            user.display_name = profile.get('display_name')
            user.profile_image = profile['images'][0]['url'] if profile.get('images') else None
            db.commit()
            print(f"✓ Updated user: {user.email}")
        else:
            # Create new user
            user = User(
                spotify_id=profile['id'],
                email=profile.get('email'),
                display_name=profile.get('display_name'),
                profile_image=profile['images'][0]['url'] if profile.get('images') else None,
                spotify_access_token=access_token,
                spotify_refresh_token=token_payload.get('refresh_token'),
                spotify_uri=f"spotify:user:{profile['id']}"
            )
            db.add(user)
            db.commit()
            print(f"✓ Created new user: {user.email}")

        # Store user ID in session for later use
        session['user_id'] = user.id

    except Exception as e:
        print(f"✗ Error saving user to database: {e}")
        db.rollback()
    finally:
        db.close()

  return redirect(url_for("playlists"))

#----------------------CUSTOM FILTERS -----------------------------#

#-------------------CUSTOM FILTERS (END)---------------------------#


#----------------------CUSTOM FUNCTIONS -----------------------------#

#-------------------CUSTOM FUNCTIONS (END)---------------------------#


#----------------------TEMPORARY TESTING DATA-----------------------------#

#--------------------TEMPORARY TESTING DATA (END)-------------------------#


      

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5555, debug=True)
