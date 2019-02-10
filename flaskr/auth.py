from base64 import b64encode
from configparser import ConfigParser
import functools
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, app
)
from requests.exceptions import SSLError, ConnectionError, RequestException
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
    try:
        session.clear()
        return redirect(SP_OAUTH.get_authorize_url())
    except ConnectionError as e:
        flash("Connection error")


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
        sp = spotipy.Spotify(auth=session['token'])
        try:
            cu = sp.current_user()
            session['display_name'] = cu['display_name']
        except RequestException as e:
            flash("Error logging in, please try again.")
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
