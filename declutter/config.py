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
    # startup_path = get_startup_shortcut_path()
    if not os.path.isfile(settings_file):
        settings = {}
        settings['version'] = VERSION
        settings['current_folder'] = ''
        settings['current_drive'] = ''
        settings['folders'] = []
        settings['tags'] = []
        # settings['filter_tags'] = []
        settings['rules'] = []
        settings['recent_folders'] = []
        settings['rule_exec_interval'] = 300
        settings['dryrun'] = False
        # settings['tag_filter_mode'] = "any"
        settings['date_type'] = 0
        # settings['launch_on_startup'] = os.path.exists(startup_path)
        # settings['view_show_filter'] = False
        save_settings(settings_file, settings)
    else:
        settings = {}
        try:
            with open(settings_file, 'r') as f:
                settings = jsonload(f)
        except Exception as e:
            logging.exception(f'exception {e}')
            logging.error('No settings file found')
            pass
        settings['version'] = VERSION
        settings['recent_folders'] = settings['recent_folders'] if 'recent_folders' in settings.keys(
        ) else []  # TBD implement a better initialization
        settings['current_drive'] = settings['current_drive'] if 'current_drive' in settings.keys(
        ) else ""
        settings['current_folder'] = settings['current_folder'] if 'current_folder' in settings.keys() else ""
        settings['folders'] = settings['folders'] if 'folders' in settings.keys() else [
        ]
        settings['tags'] = settings['tags'] if 'tags' in settings.keys() else [
        ]
        # settings['filter_tags'] = settings['filter_tags'] if 'filter_tags' in settings.keys() else []
        settings['rules'] = settings['rules'] if 'rules' in settings.keys() else [
        ]
        settings['rule_exec_interval'] = settings['rule_exec_interval'] if 'rule_exec_interval' in settings.keys() else 300
        settings['dryrun'] = settings['dryrun'] if 'dryrun' in settings.keys() else False
        # settings['tag_filter_mode'] = settings['tag_filter_mode'] if 'tag_filter_mode' in settings.keys() else "any"
        settings['date_type'] = settings['date_type'] if 'date_type' in settings.keys(
        ) else 0
        # settings['view_show_filter'] = settings['view_show_filter'] if 'view_show_filter' in settings.keys() else False
        default_formats = {'Audio': '*.aac,*.aiff,*.ape,*.flac,*.m4a,*.m4b,*.m4p,*.mp3,*.ogg,*.oga,*.mogg,*.wav,*.wma',
                           'Video': '*.3g2,*.3gp,*.amv,*.asf,*.avi,*.flv,*.gif,*.gifv,*.m4v,*.mkv,*.mov,*.qt,*.mp4,*.m4v,*.mpg,*.mp2,*.mpeg,*.mpe,*.mpv,*.mts,*.m2ts,*.ts,*.ogv,*.webm,*.wmv,*.yuv',
                           'Image': '*.jpg,*.jpeg,*.exif,*.tif,*.bmp,*.png,*.webp'}
        settings['file_types'] = settings['file_types'] if 'file_types' in settings.keys(
        ) else default_formats
    return settings

def save_settings(settings_file, settings):
    if not Path(settings_file).parent.is_dir():
        try:
            Path(settings_file).parent.mkdir()
        except Exception as e:
            logging.exception(f'exception {e}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f, indent=4)
