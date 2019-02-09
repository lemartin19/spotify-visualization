from base64 import b64encode
import functools
import requests
from configparser import ConfigParser
from datetime import timedelta
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, app
)
from urllib.parse import quote

bp = Blueprint('auth', __name__, url_prefix='/auth')
config = ConfigParser()
config.read('spotify.cfg')
CLIENT_ID = config.get('SPOTIFY', 'CLIENT_ID').strip("'")
CLIENT_SECRET = config.get('SPOTIFY', 'CLIENT_SECRET').strip("'")
REDIRECT_URI = config.get('SPOTIFY', 'REDIRECT_URI').strip("'")
SCOPE = 'user-read-currently-playing user-library-read playlist-read-private'

@bp.route('/login')
def login():
    '''
    : Create session and login user
    : PARAMS None
    : RETURN <view>
    '''

    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "client_id": CLIENT_ID
    }

    url_args = "&".join(["%s=%s" % (key, quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "%s/?%s" % ("https://accounts.spotify.com/authorize", url_args)
    return redirect(auth_url)

@bp.route('/callback/')
def callback():
    '''
    : Redirect user after login
    : PARAMS None
    : RETURN <view>
    '''
    auth_token = request.args['code']

    ex = exchange_tokens("authorization_code", auth_token)
    print("ex: %s" % ex)
    if ex:
        authorization_header = {'Authorization':'Bearer %s' % session['token']}
        profile_response = requests.get('https://api.spotify.com/v1/me', headers=authorization_header)
        session['display_name'] = profile_response.json()['display_name']
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
    '''
    : Check for login on given page
    : PARAMS view <view>
    : RETURN <wrapped_view>
    '''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('token') is None:
            return redirect(url_for('auth.login'))
        exchange_tokens("refresh_token", session['refresh'])
        return view(**kwargs)

    return wrapped_view

def exchange_tokens(grant_type, code):
    '''
    : Exchange code for new access token and set session
    : PARAMS grant_type <string> - e.x. "authorization_code" or "refresh_token"
             code       <string> - authorization code or refresh token
    : RETURN <boolean> - successful exchange
    '''
    code_payload = {
        "grant_type": grant_type,
        "code": str(code),
        "redirect_uri": REDIRECT_URI
    }
    client_info = '%s:%s' % (CLIENT_ID, CLIENT_SECRET)
    base64encoded = b64encode(client_info.encode('utf-8'))
    headers = {"Authorization": "Basic %s" % base64encoded.decode('ascii')}
    post_request = requests.post("https://accounts.spotify.com/api/token", data=code_payload, headers=headers)

    print("post_request: %s" % post_request.json())
    if post_request.status_code == 200:
        response_data = post_request.json()
        session.clear()
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=60)
        session['token'] = response_data['access_token']
        session['refresh'] = response_data['refresh_token']
        return True
    return False
