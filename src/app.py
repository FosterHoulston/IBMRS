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

# Use absolute paths for template and static folders
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
            template_folder=os.path.join(_base_dir, "templates"),
            static_folder=os.path.join(_base_dir, "static"),
            static_url_path="/")

load_dotenv()

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

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
    return None

  now = time.time()
  if token.get("expires_at") and token["expires_at"] - now > 60:
    return token.get("access_token")

  refresh_token = token.get("refresh_token")
  if not refresh_token:
    return token.get("access_token")

  data = {
      "grant_type": "refresh_token",
      "refresh_token": refresh_token,
      "client_id": SPOTIFY_CLIENT_ID,
  }
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  resp = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers, timeout=10)
  if resp.status_code != 200:
    return token.get("access_token")

  refreshed = resp.json()
  # Spotify may not return a new refresh token; reuse the existing one.
  if "refresh_token" not in refreshed:
    refreshed["refresh_token"] = refresh_token
  _store_token(refreshed)
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
  payload = {"name": name, "description": description, "public": False}
  resp = requests.post(
      f"{SPOTIFY_API_BASE}/users/{user_id}/playlists",
      headers={**_spotify_headers(access_token), "Content-Type": "application/json"},
      json=payload,
      timeout=10,
  )
  if resp.status_code not in (200, 201):
    print(f"Failed to create playlist. Status: {resp.status_code}, Response: {resp.text}")
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
  return render_template("playlists.html")


@app.route("/api/playlists/from-image", methods=["POST"])
def create_playlist_from_image():
  access_token = _ensure_access_token()
  profile = session.get("spotify_profile")
  if not access_token or not profile:
    return jsonify({"error": "Not authenticated with Spotify."}), 401

  image_file = request.files.get("image")
  if not image_file:
    return jsonify({"error": "Image file is required."}), 400

  # Save uploaded image to a temporary file
  import tempfile
  with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.filename)[1]) as tmp_file:
    image_file.save(tmp_file.name)
    temp_image_path = tmp_file.name

  try:
    llamaClient_instance = LlamaClient()
    print("LlamaClient instance created")

    # Call the AI pipeline with the temporary file path
    pipeline_result, descriptors = llamaClient_instance.pipeline(temp_image_path)
    print(f"Pipeline completed. Result type: {type(pipeline_result)}, Descriptors: {descriptors}")

    # Generate playlist name with validation
    if descriptors:
        playlist_name = " ".join(str(d).strip() for d in descriptors if str(d).strip())
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
    playlist_description = (
        "Created by IBMRS from an uploaded image. Descriptors: " + ", ".join(str(d) for d in descriptors)
        if descriptors
        else "Created by IBMRS from an uploaded image."
    )
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

  return redirect(url_for("playlists"))

#----------------------CUSTOM FILTERS -----------------------------#

#-------------------CUSTOM FILTERS (END)---------------------------#


#----------------------CUSTOM FUNCTIONS -----------------------------#

#-------------------CUSTOM FUNCTIONS (END)---------------------------#


#----------------------TEMPORARY TESTING DATA-----------------------------#

#--------------------TEMPORARY TESTING DATA (END)-------------------------#


      

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5555, debug=True)
