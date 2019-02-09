import os
import requests
import spotipy

from flask import Flask, render_template, request, session


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
            print("display name")
            return render_template('index.html', name=session['display_name'])
        print('session: %s' % session)
        return render_template('index.html')

    # search results screen
    @app.route('/search_results')
    def search_results():
        spotify = spotipy.Spotify()
        search = spotify.search(request.args.get("search_query"))
        print(search)
        return render_template('search_results.html')


    from . import auth
    app.register_blueprint(auth.bp)

    return app
