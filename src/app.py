from dotenv import load_dotenv
import os
from flask import Flask, render_template

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

@app.route('/')
def index():
    myvalue = ''
    return render_template('index.html')

#@app.route('/login')
#def login():
#    authentication_request_params = {
#        'response_type': 'code',
#        'client_id': client_id,
#        'redirect_uri': redirect_uri,
#        'scope': 'user-read-email'
#    }

@app.route('/playlists')
def playlists():
    user_fname = "John"
    playlist_list = ["calm beach vibes", "grungy street corner", "party in the club"]
    num_playlists = len(playlist_list)

    return render_template('playlists.html', user_fname=user_fname, num_playlists=num_playlists, playlist_list=playlist_list)

#----------------------CUSTOM FILTERS -----------------------------#

#-------------------CUSTOM FILTERS (END)---------------------------#


#----------------------CUSTOM FUNCTIONS -----------------------------#

#-------------------CUSTOM FUNCTIONS (END)---------------------------#


#----------------------TEMPORARY TESTING DATA-----------------------------#

#--------------------TEMPORARY TESTING DATA (END)-------------------------#


      

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5555, debug=True)
