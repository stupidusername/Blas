from flask import abort, Flask, request, Response, send_from_directory, url_for
import imghdr
import inspect
import json
from mutagenwrapper import read_tags
import os
import re
import urllib
app = Flask('Blas')


@app.route('/api/get-radios')
def get_radios():
    music_category_folders = list_folders(get_folder('music'))
    js = json.dumps(build_music_categories(music_category_folders))
    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route('/api/get-radio-songs')
def get_radio_songs():
    id = request.args.get('id')
    if not id:
        abort(400)
    js = json.dumps(build_songs(int(id)))
    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route('/get-song')
def get_song():
    file = request.args.get('file')
    if not file:
        abort(400)
    return send_from_directory(get_folder('music'), file)


@app.route('/get-albumart')
def get_albumart():
    file = request.args.get('file')
    if not file:
        abort(400)
    # remove image extensions
    file = os.path.splitext(file)[0]
    path = get_folder('music') + '/' + file
    try:
        data, mimetype = get_albumart_data(read_tags(path))
    except:
        data, mimetype = None, None
    if not data or not mimetype:
        abort(404)
    resp = Response(data, status=200, mimetype=mimetype)
    return resp


@app.route('/api/get-audio-message')
def get_audio_message():
    key = request.args.get('key')
    room = request.args.get('room')
    suffix = request.args.get('suffix')
    if not key:
        abort(400)
    messages_path = get_folder('messages')
    audio_files = list_audio_files(
        messages_path, ['aac', 'aiff', 'flac', 'm4a', 'mp3', 'ogg', 'wav'])
    filename = '.'.join([value for value in [key, room, suffix] if value])
    file = None
    for audio_file in audio_files:
        if filename == os.path.splitext(audio_file)[0]:
            file = audio_file
            break
    if not file:
        for audio_file in audio_files:
            if key == os.path.splitext(audio_file)[0]:
                file = audio_file
                break
    key = int(key)
    url = urllib.unquote_plus(url_for(
        'get_audio_message_file', file=file, _external=True)) if file else None
    audio_message = {
        'id': key,
        'key': key,
        'name': str(key),
        'name_spanish': str(key),
        'filename': file,
        'kind': int(room is not None),
        'audio_output': 0,  # room audio output
        'delay': 0,
        'manual': False,
        'audioMessageUrl': url
    }
    js = json.dumps(audio_message)
    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route('/get-audio-message')
def get_audio_message_file():
    file = request.args.get('file')
    if not file:
        abort(400)
    return send_from_directory(get_folder('messages'), file)


def get_files_root_folder():
    try:
        script_dir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        config_file = open(script_dir + '/config.json')
        config_file.seek(0)
        config = json.load(config_file)
        files_root_folder = config['files_root_folder'].rstrip('/')
        return files_root_folder
    except:
        abort(500)


def get_folder(folder):
    folder = folder.strip('/')
    return get_files_root_folder() + '/' + folder


def list_folders(path):
    return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]


def list_audio_files(path, extensions):
    regex = '^.+\.(' + '|'.join(extensions) + ')$'
    return [name for name in os.listdir(path)
            if os.path.isfile(os.path.join(path, name)) and
            re.match(regex, name, re.IGNORECASE)]


def build_music_categories(categories):
    return [{'id': idx, 'title': title} for idx, title in enumerate(categories)]


def build_songs(category_id):
    try:
        category_folder = list_folders(get_folder('music'))[int(category_id)]
        category_path = get_folder('music/' + category_folder)
        audio_files = list_audio_files(category_path, ['flac', 'm4a', 'mp3'])
    except IndexError:
        audio_files = []
    songs = []
    for idx, audio_file in enumerate(audio_files):
        path = category_path + '/' + audio_file
        file = category_folder + '/' + audio_file
        song_url = urllib.unquote_plus(
            url_for('get_song', file=file, _external=True))
        try:
            tags = read_tags(path)
        except:
            tags = None
        albumart_mime = get_albumart_data(tags)[1]
        if albumart_mime:
            extension = albumart_mime.replace('image/', '')
            albumart_file = file + '.' + extension
            albumart_url = urllib.unquote_plus(
                url_for('get_albumart', file=albumart_file, _external=True))
        else:
            extension = None
            albumart_file = None
            albumart_url = None
        songs.append({
            'id': idx,
            'radio_id': category_id,
            'filename': audio_file,
            'title': tags.find('title') if tags else None,
            'album': tags.find('album') if tags else None,
            'author': tags.find('artist') if tags else None,
            'albumart_filename': albumart_file,
            'songUrl': song_url,
            'albumartUrl': albumart_url
        })
    return songs


def get_albumart_data(tags):
    tags = tags.raw_tags if tags else None
    data, mimetype = None, None
    # try flac tag
    if hasattr(tags, 'pictures'):
        for picture in tags.pictures:
            # search for front cover
            if picture.type == 3:
                data = picture.data
                mimetype = picture.mime
    elif tags:
        for tag, value in tags.iteritems():
            # try mp3 tags
            if tag.startswith('APIC:'):
                # search for front cover
                if value.type == 3:
                    data = value.data
                    mimetype = value.mime
                    break
            # try m4a tag
            elif tag == 'covr':
                data = value[0] if value else None
                mimetype = 'image/' + imghdr.what(None, data)
                break
    return data, mimetype
