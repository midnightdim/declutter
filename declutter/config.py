from json import (load as jsonload, dump as jsondump)
import logging
import os
from pathlib import Path
from appdirs import user_data_dir   

VERSION = '1.13.1'
APP_FOLDER = user_data_dir("DeClutter", appauthor='', roaming=True)
Path(APP_FOLDER).mkdir(parents=True, exist_ok=True)

LOG_FILE = os.path.join(APP_FOLDER, "DeClutter.log")
DB_FILE = os.path.join(APP_FOLDER, "DeClutter.db")
SETTINGS_FILE = os.path.join(APP_FOLDER, "settings.json")
ALL_TAGGED_TEXT = 'All tagged files and folders'

logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler(filename=LOG_FILE, encoding='utf-8', mode='a+')],
                    format="%(asctime)-15s %(levelname)-8s %(message)s")

def load_settings(settings_file=SETTINGS_FILE):
    """Loads application settings from a JSON file. If the file does not exist, it creates a default settings file."""
    
    if not os.path.isfile(settings_file):
        settings = {
            'version': VERSION,
            'current_folder': '',
            'current_drive': '',
            'folders': [],
            'tags': [],
            'rules': [],
            'recent_folders': [],
            'rule_exec_interval': 300,
            'dryrun': False,
            'date_type': 0,
            'file_types': {
                'Audio': '*.aac,*.aiff,*.ape,*.flac,*.m4a,*.m4b,*.m4p,*.mp3,*.ogg,*.oga,*.mogg,*.wav,*.wma',
                'Video': '*.3g2,*.3gp,*.amv,*.asf,*.avi,*.flv,*.gif,*.gifv,*.m4v,*.mkv,*.mov,*.qt,*.mp4,*.m4v,*.mpg,*.mp2,*.mpeg,*.mpe,*.mpv,*.mts,*.m2ts,*.ts,*.ogv,*.webm,*.wmv,*.yuv',
                'Image': '*.jpg,*.jpeg,*.exif,*.tif,*.bmp,*.png,*.webp'
            }
        }
        save_settings(settings_file, settings)
    else:
        settings = {}
        try:
            with open(settings_file, 'r') as f:
                settings = jsonload(f)
        except Exception as e:
            logging.exception(f'exception {e}')
            logging.error('Error loading settings file')
            pass

        # Ensure all expected keys exist, providing default values if missing
        settings.setdefault('current_folder', '')
        settings.setdefault('current_drive', '')
        settings.setdefault('folders', [])
        settings.setdefault('tags', [])
        settings.setdefault('rules', [])
        settings.setdefault('recent_folders', [])
        settings.setdefault('rule_exec_interval', 300)
        settings.setdefault('dryrun', False)
        settings.setdefault('date_type', 0)
        settings.setdefault('file_types', {
            'Audio': '*.aac,*.aiff,*.ape,*.flac,*.m4a,*.m4b,*.m4p,*.mp3,*.ogg,*.oga,*.mogg,*.wav,*.wma',
            'Video': '*.3g2,*.3gp,*.amv,*.asf,*.avi,*.flv,*.gif,*.gifv,*.m4v,*.mkv,*.mov,*.qt,*.mp4,*.m4v,*.mpg,*.mp2,*.mpeg,*.mpe,*.mpv,*.mts,*.m2ts,*.ts,*.ogv,*.webm,*.wmv,*.yuv',
            'Image': '*.jpg,*.jpeg,*.exif,*.tif,*.bmp,*.png,*.webp'
        })
        
        if settings.get('version') != VERSION:
            settings['version'] = VERSION
            save_settings(settings_file, settings)
    
    return settings


def save_settings(settings_file, settings):
    if not Path(settings_file).parent.is_dir():
        try:
            Path(settings_file).parent.mkdir()
        except Exception as e:
            logging.exception(f'exception {e}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f, indent=4)
