# IBMRS (Image-Based Music Recommendation System)
Monolithic web app that creates Spotify playlists based on the vibe of an uploaded image.

## Spotify OAuth setup

1. Create a Spotify application at [developer.spotify.com](https://developer.spotify.com/dashboard) and enable the **Authorization Code with PKCE** flow.
2. Add `http://localhost:5555/auth/callback` **and** `http://localhost:5555/callback` (or your deployed URL) as allowed redirect URIs.
3. Provide the following variables in a `.env` file:

```
CLIENT_ID=your_spotify_client_id
REDIRECT_URI=http://localhost:5555/auth/callback
FLASK_SECRET_KEY=replace-with-a-long-random-string
```

Once configured, the **Connect Spotify** button on the landing page will start the PKCE OAuth flow, return the authenticated user profile, and allow the app to act on their behalf (read profile + manage playlists).
