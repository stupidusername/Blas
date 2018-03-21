Blas
====

Blas: Little Audio Server

Requirements
------------

* Pip packages listed on requirements.txt

Configuration
-------------

This app needs a `config.json` file. Use `config.json.example` for reference. Directory structure for media files folder must be as follows:
```
| - files_root_folder/
  | - channels/
  | - channel_category_1/
  | | | - 1 - channel_1.png
  | | | - ...
  | | - channel_category_2/
  | | - ...
  | | - channel_category_n/
  | - music/
  | | - music_category_1/
  | | | - song.mp3
  | | | - ...
  | | - music_category_2/
  | | - ...
  | | - music_category_n/
  | - messages/
    | - 1.mp3
    | - ...
```
Channel and music category titles are defined by the name of their folders. Audio message files must be named after their corresponding audio message key.
Chanel files must be named like this ```<number> - <title>.<extension>```. For example "1 - Channel 1.png". No logo image will be provided if extension is "txt".

Supported file extensions
-------------------------

* For channel files: txt, jpeg, jpg, png
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
command = gunicorn -w 9 -b 0.0.0.0:5000 main:app
directory = /home/pi/blas
autostart = true
autorestart = true
```
* Update supervisor configuration.
```
$ sudo supervisorctl update
```
