import  spotipy
from flask import (
    Blueprint, redirect, render_template, request, session, url_for, flash
)
from requests.exceptions import SSLError

bp = Blueprint('song', __name__, url_prefix='/')

@bp.route('/song', methods=['GET'])
def song():
    sp = spotipy.Spotify(auth=session['token'])
    id = request.args.get('id')
    try:
        analysis = sp.audio_analysis(id)
        features = sp.audio_features(id)
        track = sp.track(id)
        return render_template('song.html', name=session['display_name'], track=track,
            features=features[0], analysis=analysis)
    except SSLError as err:
        flash("Connection error")
        return redirect(url_for('song.song', id=id))
