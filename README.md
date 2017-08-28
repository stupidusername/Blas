Blas
====

Blas: Little Audio Server

Requirements
------------

* Pip packages listed on requirements.txt

Configuration
-------------

This app needs a `config.json` file. Use `config.json.example` for reference. Directory structure for the audio files folder must be as follows:
```
| - files_root_folder/
  | - music/
  | | - music_category_1/
  | | | - song.mp3
  | | - music_category_2/
  | | - ...
  | | - music_category_n/
  | - messages/
    | - 1.mp3
```
Music category titles are defined by the name of their folders. Audio message files must be named after their corresponding audio message key.

Supported audio extensions
--------------------------

* For music files: flac, m4a, mp3
* For message files: aac, aiff, flac, m4a, mp3, ogg, wav

Installation on Raspberry Pi
----------------------------

These instructions are for installing Blas on a Raspberry Pi.
The chosen OS is Raspbian Jessie Lite. It's assumed that git and pip are installed on the system.

* Clone app repo.
```
$ git clone https://github.com/stupidusername/Blas.git ~/blas
```
* Install app requirements.
```
$ sudo pip install -r ~/blas/requirements.txt
```
* (Optional) Install usbmount.
```
$ sudo apt-get install usbmount
```
* Configure app by editing ~/blas/config.json.
If the files are beign read from an usb device and usbmount is running then the property "files_root_folder" should take the value "/media/usb".
```
$ cp ~/blas/config.json.example ~/blas/config.json
$ nano ~/blas/config.json
```
* Install supervisor.
```
$ sudo apt-get install supervisor
```
* Add Blas as a supervisor process.
```
$ sudo nano /etc/supervisor/supervisord.conf
```
add these lines at the end of the file
```
[program:blas]                                                                  
environment = FLASK_APP=main.py  
command = python -m flask run
directory = /home/pi/blas
autostart = true
autorestart = true
```
* Update supervisor configuration.
```
$ sudo supervisorctl update
```
