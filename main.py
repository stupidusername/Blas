from flask import abort, Flask, request, Response, send_from_directory, url_for
import imghdr
import inspect
import json
from mutagenwrapper import read_tags
import operator
import os
import re
import urllib


app = Flask('Blas')


@app.route('/api/get-radios')
def get_radios():
    music_category_folders = list_folders(get_folder('music'))
    js = json.dumps(build_categories(music_category_folders))
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
    if not key:
        abort(400)
    messages_path = get_folder('messages')
    audio_files = list_files(
        messages_path, ['aac', 'aiff', 'flac', 'm4a', 'mp3', 'ogg', 'wav'])
    filename = '.'.join([value for value in [key, room] if value])
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
    url = None
    if file:
        url = url_for('get_audio_message_file', file=file, _external=True)
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


@app.route('/api/get-channel-categories')
def get_channel_categories():
    channel_category_folders = list_folders(get_folder('channels'))
    js = json.dumps(build_categories(channel_category_folders))
    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route('/api/get-channels')
def get_channels():
    id = request.args.get('categoryId')
    if not id:
        abort(400)
    js = json.dumps(build_channels(int(id)))
    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route('/get-channel-logo')
def get_channel_logo():
    file = request.args.get('file')
    if not file:
        abort(400)
    return send_from_directory(get_folder('channels'), file)


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
    folders = [name for name in os.listdir(path)
               if os.path.isdir(os.path.join(path, name))]
    return sorted(folders)


def list_files(path, extensions):
    regex = re.compile('^.+\.(' + '|'.join(extensions) + ')$', re.IGNORECASE)
    files = [name for name in os.listdir(path)
             if os.path.isfile(os.path.join(path, name)) and
             regex.match(name)]
    return files


def build_categories(categories):
    return [{'id': idx, 'title': title} for idx, title in enumerate(categories)]


def build_songs(category_id):
    try:
        category_folder = list_folders(get_folder('music'))[int(category_id)]
        category_path = get_folder('music/' + category_folder)
        audio_files = list_files(category_path, ['flac', 'm4a', 'mp3'])
    except IndexError:
        audio_files = []
    songs = []
    for idx, audio_file in enumerate(audio_files):
        path = category_path + '/' + audio_file
        file = category_folder + '/' + audio_file
        # harcoded urls are needed becaus url_for() it's too slow
        song_url = request.url_root + 'get-song?file=' + \
            urllib.quote(file.encode('utf8'))
        try:
            tags = read_tags(path)
            title = tags.find('title')
            album = tags.find('album')
            author = tags.find('artist')
        except:
            tags = None
            title = None
            album = None
            author = None
        albumart_mime = get_albumart_data(tags)[1]
        if albumart_mime:
            extension = albumart_mime.replace('image/', '')
            albumart_file = file + '.' + extension
            albumart_url = request.url_root + 'get-albumart?file=' + \
                urllib.quote(albumart_file.encode('utf8'))
        else:
            extension = None
            albumart_file = None
            albumart_url = None
        songs.append({
            'id': idx,
            'radio_id': category_id,
            'filename': audio_file,
            'title': title,
            'album': album,
            'author': author,
            'albumart_filename': albumart_file,
            'songUrl': song_url,
            'albumartUrl': albumart_url
        })
    return songs


def build_channels(category_id):
    try:
        category_folder = list_folders(get_folder('channels'))[int(category_id)]
        category_path = get_folder('channels/' + category_folder)
        channel_files = list_files(category_path, ['txt', 'jpeg', 'jpg', 'png'])
    except IndexError:
        channel_files = []
    channels = []
    regex = re.compile('^(\d+)\s*-\s*(.+)\.(.+)$')
    for idx, channel_file in enumerate(channel_files):
        match = regex.match(channel_file)
        if match:
            number = int(match.group(1))
            title = match.group(2)
            if match.group(3).lower() in ['jpeg', 'jpg', 'png']:
                logo = channel_file
                logo_file = category_folder + '/' + channel_file
                logo_url = request.url_root + 'get-channel-logo?file=' + \
                    urllib.quote(logo_file.encode('utf8'))
            else:
                logo = None
                logo_url = None
            channels.append({
                'id': idx,
                'channel_category_id': category_id,
                'number': number,
                'title': title,
                'logo_filename': logo,
                'logoUrl': logo_url
            })
    return sorted(channels, key=operator.itemgetter('number'))


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
