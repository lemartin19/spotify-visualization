import os
import requests
import spotipy
import json
from flask import Flask, render_template, request, session, flash, redirect, url_for
from requests.exceptions import SSLError


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # home screen
    @app.route('/')
    def home():
        if 'display_name' in session:
            return render_template('index.html', name=session['display_name'])
        return render_template('index.html')

    # search results screen
    @app.route('/search_results')
    @login_required
    def search_results():
        if 'display_name' in session and 'token' in session:
            spotify = spotipy.Spotify(auth=session['token'])
            try:
                query = request.args.get('search_query')
                results = spotify.search(query)
                tracks = results['tracks']['items']
                return render_template('search_results.html', name=session['display_name'], tracks=tracks)
            except SSLError as err:
                flash("Connection error")
                redirect(url_for('search_results', search_query=query))
        else:
            return redirect(url_for('home'))

    from . import auth
    app.register_blueprint(auth.bp)

    from . import song
    app.register_blueprint(song.bp)

    return app
