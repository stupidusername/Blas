from flask import abort, Flask, request
app = Flask('Blas')


@app.route('/api/get-radios')
def get_radios():
    return ''


@app.route('/api/get-radio-songs')
def get_radio_songs():
    id = request.args.get('id')
    if not id:
        abort(400)
    return id


@app.route('/api/get-audio-message')
def get_audio_message():
    key = request.args.get('key')
    room = request.args.get('room')
    suffix = request.args.get('suffix')
    if not key:
        abort(400)
    return key
