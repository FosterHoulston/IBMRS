from flask import Flask

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return "<h1>This is the home page</h1>"

@app.route('/login',)
def login():
    return "<h1>This is the Spotify login page</h1>"

@app.route('/uploadImage')
def uploadImage():
    return "<h1>This page is for upoading an image</h1>"

@app.route('/takePhoto')
def takePicture():
    return "<h1>This page is for using a camera to upload an image</h1>"

@app.route('/playlists')
def playlists():
    return "<h1>This page displays all playlists created with the app for the current spotify user</h1>"

@app.route('/playlists/<playlistName>')
def newPlaylist():
    return "<h1>This page displays a specific playlist</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
