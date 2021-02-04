import os, platform
#from platform import system
import PySimpleGUIWx as sg
from declutter_lib import apply_all_rules, load_settings, save_settings
import subprocess
from time import time
from pathlib import Path

#from apscheduler.schedulers.background import BackgroundScheduler
#from apscheduler.triggers.interval import IntervalTrigger

import logging

APP_FOLDER = os.path.join(os.getenv('APPDATA'), "DeClutter")
LOG_FILE = os.path.join(APP_FOLDER, "DeClutter.log")
if not Path(APP_FOLDER).is_dir():
    Path(APP_FOLDER).mkdir()
logging.basicConfig(level=logging.DEBUG, filename= LOG_FILE, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")

logging.info("DeClutter service started")

#SETTINGS_FILE = os.path.join(os.getcwd(), r'settings.json')
SETTINGS_FILE = os.path.join(os.getenv('APPDATA'), "Declutter\\settings.json")
settings = load_settings(SETTINGS_FILE)

#icon = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAsQAAALEBxi1JjQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMTSURBVEiJnZVpSBRhGMd/M7uzlzupmWW2aWVaeHTZUoKVaREIRQcUdFNCdFBRQn3oIKEig6KTMIIOjIyk6ID8kLYdxNqBZZG13aSlnYiZOrtOH0xya2d37P9leN93nv/veZ73nXcEAsiRPf90WuKgjEBrofSg5oW53nU6tnNsDPSSWTJa186bMeB/AIXHz76pd/0Z+wGGTs07LttsttpPX51nrlbocxQEREEgIS6W9KGJ/yz7AZypQ7JO7siP707Gmw6eYlZOJntPlIYGaKm24QvVnjfINivO1CRMkn+YqqqoGrFBAY1NzawrLCKih0xKQjyen3UcKL7ItOwM5uZOAEBRvOw6VoLRYAjoIWqZq6pK3tZ9LJg6icyRKRRfLqfC/ZDtqxfz6Nlrzpff6TAQBeZMmUh7e2cNgqALcMnlJss5DEefXjS3tJLY34H62yNv5hTOld3skkzH0/O2Tnn94WN1Vx/NFpW7HzJ9Ygaz83cQExXJ8KTBfGtqYu2uIiRJJGVwPG/rGmhpVThaegXZZuHa3ar6V+/rF+qqoKW1DUEQMBoMRMh2LJJEhBxGjzAriuJFFATavF6MBpHJY0f/6YxB8ttvzQrSk5N4+e4jheuXUlXzipoX76lt+Ez+kllYTRJ7Tp5nkCMGlY790jpGmhUsnJZNSZkLi8lEdGQ4954+52tjI7HRPblx7wnOtCEYRJE2xcuFitsoPl9AH80KzCaJw1tWsbLgEFmjh1OwYgHfm36ws6iE3tGR7FyzCID9G5cBMH/DbppbFP0AgARHDFeObKPs9n3uPnmObLeyecVcBvbrEyxMPwDAIIrkjnOSO86p2zQk4Jq7isvXK3UZ7M5fqvkVawLi+vZmgjNNF0AUNM+JNsAsSUTIdl2AUAoI8Lyr1d2izFHJiHSzRTljRpAzZgSXXG58vvaAgUnx/UhOiAuZQNBTFG4P63JL+stiNvmNFcWHV/XZugUYn54aMsNO3al++lm22iqxSq1BAaqq9W8Krqhw+62q0sMz/p73A1Q+9kQtLzj4838AkmS0BJr/Bb4+9K8YBHimAAAAAElFTkSuQmCC'
icon = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAMAAADXqc3KAAAAA3NCSVQICAjb4U/gAAAACXBIWXMAAAYnAAAGJwFNVNjHAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAGxQTFRFccCFzrFe2ox0R1FrS1VwTFZxTVhzVWCAWWWCXGiIXGmGXmmKYWyNYm+OccKFdcSJeIWof4yvhMqWh8yYipi8kM+gyujS5MBc5cJh6Mly6Mp26s6A8JNy8JZ28qKF8qSI86uR9ejC+dfK////MhGzaAAAAAN0Uk5T5OTkyeisKwAAAHVJREFUKFPl0TsSwjAMBcBV7PBpcv9zQgPENhRxUsD4BKhZvVEhzSgWW127czeLjPIWE9phdlpwe0oXPIqUUEtW76i0hkab0MRox9T9qf8dxHdzeO5N6ebDfMKrmGasbc9ZJITN0o3x8uEgq8X22hXNnodXfQDfaiZPQ1CqhAAAAABJRU5ErkJggg=='
#sg.theme('SystemDefaultForReal')
sg.set_global_icon(icon)
sg.theme('SystemDefault1')
sg.theme_button_color(('Black', 'Light Gray'))

dryrun = bool(settings['dryrun'])
jobs_paused = False
delay = frequency_in_seconds = int(settings['rule_exec_interval']) # default interval is 5 minutes

logging.info("DRYRUN mode is " + ("ON" if dryrun else "OFF"))

def build_menu(dryrun, jobs_paused):
    return ['BLANK', ['&Dryrun is ' + ("ON" if dryrun else "OFF"), '---', '&Reschedule', ('&Resume' if jobs_paused else '&Pause') + ' jobs','&Launch once', '---', '&Launch GUI', '---', '&Open log file', '---', 'E&xit']]

#menu_def = ['BLANK', ['&Dryrun is ON', '---', '&Reschedule', '&Pause jobs','&Launch once', '---', '&Launch GUI', '---', 'E&xit']]
menu_def = build_menu(dryrun, jobs_paused)
#tray = sg.SystemTray(menu=menu_def, filename=r'24x24.png', tooltip = "DeClutter service")

tray = sg.SystemTray(menu=menu_def, data_base64 = icon, tooltip='DeClutter service' + (' [DRYRUN]' if dryrun else '') + f' runs every {frequency_in_seconds/60} minutes')

starting_seconds = time()

details = []

# def get_rules_table_values():
#     rules_values = ["          "]
#     if settings['rules']: # and len(settings['rules']) > 0:
#         rules_values = []
#         for r in settings['rules']:
#             row = []
#             row.append(r['name'])
#             row.append(r['enabled'])
#             row.append(r['action'])
#             row.append(', '.join(r['folders']))
#             rules_values.append(row)
#     return rules_values

# print(get_rules_table_values())

# layout_rules = [[sg.Table(values = get_rules_table_values(), 
#                 headings=['Name', 'Enabled', 'Action', 'Folders'], 
#                 justification = 'left',
#                 key="_RULES_", select_mode=sg.TABLE_SELECT_MODE_BROWSE, 
#                 #def_col_width=20, max_col_width=50,
#                 auto_size_columns = True)],
#                 [sg.Button("+", tooltip = "Add"), sg.Button("X", tooltip = "Delete"), sg.Button("E", tooltip = "Edit"), 
#                 sg.Button("Test Rule"), sg.Button("Apply Rule"), sg.Button('Enable', key = '_en_dis_button_')]
#                 ]
# window_rules = sg.Window('Rules', layout_rules, finalize = True, return_keyboard_events=True)
# window_rules['_RULES_'].bind('<Double-Button-1>', '_double_clicked')

# window_rules.read()

while True:  # The event loop
    menu_item = tray.read(timeout=delay*1000)
    delta_from_last = time() - starting_seconds
    if delta_from_last >= frequency_in_seconds:
        starting_seconds = time()
        delta_from_last = 0
        if not jobs_paused:
            settings = load_settings(SETTINGS_FILE)
            report, details = apply_all_rules(settings, dryrun) #TBD vN: should we also read dryrun value from settings?
            msg = ""
            for key in report.keys():
                msg+= key + ": " + str(report[key]) + "\n" if report[key] > 0 else ""
            if len(msg)>0:
                tray.show_message("DeClutter", "Processed files and folders:\n" + msg)

    if menu_item == 'Exit':
        #job.remove()
        break
    elif menu_item == '__MESSAGE_CLICKED__':
        if details:
            sg.popup_scrolled(str(len(details)) + " file(s) processed", *details)
            details = []
    elif menu_item == 'Dryrun is ON':
        dryrun = False
        settings['dryrun'] = False
        save_settings(SETTINGS_FILE, settings)
        logging.info("DRYRUN mode is OFF")
        tray.ShowMessage("Beware!", "Going live!")
        menu_def = build_menu(dryrun, jobs_paused)
        tray.update(tooltip='DeClutter service' + f' runs every {frequency_in_seconds/60} minutes')
        tray.update(menu = menu_def)
    elif menu_item == 'Dryrun is OFF':
        dryrun = True
        settings['dryrun'] = True
        save_settings(SETTINGS_FILE, settings)        
        logging.info("DRYRUN mode is ON")  # TBD too much
        tray.ShowMessage("Note", "Switching to DRYRUN mode (don't touch files, only log intentions)")
        menu_def = build_menu(dryrun, jobs_paused)
        tray.update(tooltip='DeClutter service [DRYRUN]' + f' runs every {frequency_in_seconds/60} minutes')
        tray.update(menu = menu_def)        
    elif menu_item == 'Launch GUI':
        try:
            subprocess.Popen("DeClutter_gui.exe")
        except Exception as e:
            tray.ShowMessage("Error", "GUI executable not found!")
            logging.exception(f'exception {e}')
            logging.error('No DeClutter_gui.exe file found')
    elif menu_item == 'Resume jobs':
        #job.resume()
        jobs_paused = False
        logging.info("Jobs resumed")
        menu_def = build_menu(dryrun, jobs_paused)
        tray.update(menu = menu_def)
    elif menu_item == 'Pause jobs':
        #job.pause()
        jobs_paused = True
        logging.info("Jobs paused")
        menu_def = build_menu(dryrun, jobs_paused)
        tray.update(menu = menu_def)
    elif menu_item == 'Launch once':
        settings = load_settings(SETTINGS_FILE)
        report, details = apply_all_rules(settings, dryrun)
        if report:
            msg = ""
            for key in report.keys():
                msg+= key + ": " + str(report[key]) + "\n" if report[key] > 0 else ""
            if len(msg)>0:
                tray.show_message("DeClutter", "Processed files and folders:\n" + msg)
        #print(ev)
    elif menu_item == 'Reschedule':
        freq = sg.popup_get_text(f'Currently the rules are executed every {frequency_in_seconds/60} minutes\n'+
                            'Enter new frequency in minutes', 'Change rule execution schedule', icon = icon)
        if freq:
            try:
                frequency_in_seconds = int(float(freq)*60)
                starting_seconds = time()
                delta_from_last = 0
                tray.update(tooltip='DeClutter service' + (' [DRYRUN]' if dryrun else '') + f', runs every {frequency_in_seconds/60} minutes')
                settings['rule_exec_interval'] = frequency_in_seconds
                save_settings(SETTINGS_FILE, settings)
            except:
                sg.popup_error(f'Invalid value: {freq}', f'Keeping old frequency of {frequency_in_seconds/60} minutes', icon = icon)

    elif menu_item == "Open log file":
        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', LOG_FILE)) #TBD v2 opens first selected element which is not always good
            elif platform.system() == 'Windows':    # Windows
                os.startfile(LOG_FILE)
            else:                                   # linux variants
                subprocess.call(('xdg-open', LOG_FILE))
        except Exception as e:
            logging.exception(f'exception {e}')  

        # i = sg.PopupGetText("Enter interval in minutes", default_text = interval, icon = icon)
        # if i and int(i) > 0:
        #     interval = int(i)

    delay = frequency_in_seconds - delta_from_last

tray.close()