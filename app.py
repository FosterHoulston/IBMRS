import base64
import hashlib
import os
import secrets
import time
from typing import Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/")

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
