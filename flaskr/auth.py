from base64 import b64encode
from configparser import ConfigParser
import functools
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, app
)
from requests.exceptions import SSLError
import spotipy
from spotipy import oauth2

bp = Blueprint('auth', __name__, url_prefix='/auth')
config = ConfigParser()
config.read('spotify.cfg')
CLIENT_ID = config.get('SPOTIFY', 'CLIENT_ID').strip("'")
CLIENT_SECRET = config.get('SPOTIFY', 'CLIENT_SECRET').strip("'")
REDIRECT_URI = config.get('SPOTIFY', 'REDIRECT_URI').strip("'")
SCOPE = 'user-read-currently-playing user-library-read playlist-read-private'
SP_OAUTH = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE)


@bp.route('/login')
def login():
    '''
    : Create session and login user
    : PARAMS None
    : RETURN <view>
    '''
    session.clear()
    return redirect(SP_OAUTH.get_authorize_url())

@bp.route('/callback/')
def callback():
    '''
    : Redirect user after login
    : PARAMS None
    : RETURN <view>
    '''
    code = request.args.get('code')
    token = SP_OAUTH.get_access_token(code)
    if token:
        session['token'] = token['access_token']
        session['refresh'] = token['refresh_token']
        sp = spotipy.Spotify(auth=session['token'])
        try:
            cu = sp.current_user()
            session['display_name'] = cu['display_name']
        except SSLError as e:
            flash("Connection error")
    else:
        flash("Cannot get access token")
    return redirect(url_for('home'))

@bp.route('/logout')
def logout():
    '''
    : Clear session and log user out
    : PARAMS None
    : RETURN <view>
    '''
    session.clear()
    return redirect(url_for('home'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):

        if 'refresh' in session:
            refresh = SP_OAUTH.refresh_access_token(session['refresh'])
            session['token'] = refresh['access_token']
            session['refresh'] = refresh['refresh_token']
            sp = spotipy.Spotify(auth=session['token'])
            try:
                cu = sp.current_user()
                session['display_name'] = cu['display_name']
            except SSLError:
                flash("Connection error - please try again.")
            return view(**kwargs)
        else:
            return redirect(url_for('home'))

    return wrapped_view
