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
    |    | - music_category_1/
    |    |    | - song.mp3
    |    | - music_category_2/
    |    | - ...
    |    | - music_category_n/
    | - messages/
         | - 1.mp3
```
Music category titles are defined by the name of their folders. Audio message files must be named after their corresponding audio message key.


Installation on Raspberry Pi
----------------------------

These instructions are for installing Eric on a Raspberry Pi.
The chosen OS is Raspbian Jessie Lite.
