import os
import requests

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
        # if logged in
        if session.get('display_name'):
            return render_template('index.html', name=session['display_name'])
        return render_template('index.html')


    from . import auth
    app.register_blueprint(auth.bp)

    return app
