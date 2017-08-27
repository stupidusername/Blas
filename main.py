from flask import abort, Flask, request
import inspect
import json
from mutagenwrapper import read_tags
import os
import re
app = Flask('Blas')


@app.route('/api/get-radios')
def get_radios():
    music_category_folders = list_folders(get_folder('music'))
    return json.dumps(build_music_categories(music_category_folders))


@app.route('/api/get-radio-songs')
def get_radio_songs():
    id = request.args.get('id')
    if not id:
        abort(400)
    return str(build_songs(int(id)))


@app.route('/api/get-audio-message')
def get_audio_message():
    key = request.args.get('key')
    room = request.args.get('room')
    suffix = request.args.get('suffix')
    if not key:
        abort(400)
    return key


def get_files_root_folder():
    try:
        script_dir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        config_file = open(script_dir + '/config.json')
        config_file.seek(0)
        config = json.load(config_file)
        files_root_folder = config['files_root_folder'].strip('/')
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
        audio_files = list_audio_files(category_path, ['flac', 'mp3', 'm4a'])
    except IndexError:
        audio_files = []
    return [read_tags(category_path + '/' + audio_file)['title']
            for audio_file in audio_files]
