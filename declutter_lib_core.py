# Contains the core logic of DeClutter app

from json import (load as jsonload, dump as jsondump)
import os
import re
import time
# import datetime
# import stat
from shutil import copy2, move, copytree, rmtree
from send2trash import send2trash
# import subprocess
from pathlib import Path
import logging
from fnmatch import fnmatch
from appdirs import user_data_dir
# import sqlite3
# import glob
# import ctypes as _ctypes
# from ctypes.wintypes import HWND as _HWND, HANDLE as _HANDLE,DWORD as _DWORD,LPCWSTR as _LPCWSTR,MAX_PATH as _MAX_PATH
# from ctypes import create_unicode_buffer as _cub 

VERSION = '1.12.2.1'
LITE_MODE = False
APP_FOLDER = user_data_dir("DeClutter", appauthor='', roaming=True)
if not os.path.isdir(APP_FOLDER):
    os.makedirs(APP_FOLDER)
# APP_FOLDER = os.path.join(os.getenv('APPDATA'), "DeClutter")
LOG_FILE = os.path.join(APP_FOLDER, "DeClutter.log")
# DB_FILE = os.path.join(APP_FOLDER, "DeClutter.db")
SETTINGS_FILE = os.path.join(APP_FOLDER, "settings.json")
# ALL_TAGGED_TEXT = 'All tagged files and folders'
# TAGS_CACHE = {}

# logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler(filename=LOG_FILE, encoding='utf-8', mode='a+')],
#                         format="%(asctime)-15s %(levelname)-8s %(message)s")

def load_settings(settings_file = SETTINGS_FILE):
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
        settings['recent_folders'] = settings['recent_folders'] if 'recent_folders' in settings.keys() else [] #TBD implement a better initialization
        settings['current_drive'] = settings['current_drive'] if 'current_drive' in settings.keys() else ""
        settings['current_folder'] = settings['current_folder'] if 'current_folder' in settings.keys() else ""  
        settings['folders'] = settings['folders'] if 'folders' in settings.keys() else []
        settings['tags'] = settings['tags'] if 'tags' in settings.keys() else []
        # settings['filter_tags'] = settings['filter_tags'] if 'filter_tags' in settings.keys() else []
        settings['rules'] = settings['rules'] if 'rules' in settings.keys() else []
        settings['rule_exec_interval'] = settings['rule_exec_interval'] if 'rule_exec_interval' in settings.keys() else 300
        settings['dryrun'] = settings['dryrun'] if 'dryrun' in settings.keys() else False
        # settings['tag_filter_mode'] = settings['tag_filter_mode'] if 'tag_filter_mode' in settings.keys() else "any"
        settings['date_type'] = settings['date_type'] if 'date_type' in settings.keys() else 0
        # settings['view_show_filter'] = settings['view_show_filter'] if 'view_show_filter' in settings.keys() else False
        default_formats = {'Audio':'*.aac,*.aiff,*.ape,*.flac,*.m4a,*.m4b,*.m4p,*.mp3,*.ogg,*.oga,*.mogg,*.wav,*.wma', \
            'Video':'*.3g2,*.3gp,*.amv,*.asf,*.avi,*.flv,*.gif,*.gifv,*.m4v,*.mkv,*.mov,*.qt,*.mp4,*.m4v,*.mpg,*.mp2,*.mpeg,*.mpe,*.mpv,*.mts,*.m2ts,*.ts,*.ogv,*.webm,*.wmv,*.yuv', \
            'Image':'*.jpg,*.jpeg,*.exif,*.tif,*.bmp,*.png,*.webp'}
        settings['file_types'] = settings['file_types'] if 'file_types' in settings.keys() else default_formats
        # settings['launch_on_startup'] = settings['launch_on_startup'] if 'launch_on_startup' in settings.keys() else True
        # settings['launch_on_startup'] = os.path.exists(startup_path) # setting this parameter based on startup shortcut existence - it can be created by Inno Setup, Windows only
    return settings


def save_settings(settings_file, settings):
    if not Path(settings_file).parent.is_dir():
        try:
            Path(settings_file).parent.mkdir()
        except Exception as e:
            logging.exception(f'exception {e}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f, indent=4)


def apply_rule(rule, dryrun = False):
    report = {'copied':0, 'moved':0, 'moved to subfolder':0, 'deleted':0, 'trashed':0, 'renamed':0}
    details = []
    if rule['enabled']:
        files = get_files_affected_by_rule(rule)
        if files:
            logging.debug("Processing rule" + (" [DRYRUN mode]" if dryrun else "") + ": " + rule['name'])
            for f in files:
                msg = ""
                p = Path(f)
                if rule['action'] == 'Copy':
                    target_folder = resolve_path(rule['target_folder'],p)
                    target = Path(target_folder) / str(p).replace(':','') if ('keep_folder_structure' in rule.keys() and rule['keep_folder_structure']) else Path(target_folder) / p.name
                    try:                        
                        if p.is_dir():
                            if target.is_dir():
                                if get_size(target) != get_size(f): # TBD replaces only if size differs
                                    if not dryrun:
                                        rmtree(target)
                                        result = copytree(f, target)
                                        # hide_dc(result) # TBD only for sidecar files
                                    msg = "Replaced " + str(result) + " with " + f
                                    report['copied'] += 1
                            else:
                                if not dryrun:
                                    result = copytree(f, target)  # TBD will probably crash if target exists!
                                    # hide_dc(result) # TBD only for sidecar files
                                msg = "Copied " + f + " to " + str(result)                          
                                report['copied'] += 1
                        else: 
                            if target.is_file() and os.stat(target).st_size == os.stat(f).st_size: # TBD comparing sizes may be not enough                                
                                msg = "File " + f + " already exists in the target location and has the same size, skipping"
                                #result = target
                            else:
                                if not dryrun:
                                    result = advanced_copy(f, target, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                                else:
                                    msg = "Copied " + f + " to " + str(result)
                                if result:
                                    report['copied'] += 1
                                    msg = "Copied " + f + " to " + str(result)
                        # if rule['keep_tags']:
                        #     tags = get_tags(f)
                        #     if set_tags(result, tags):
                        #         #logging.info("Copied tags for " + f)
                        #         msg += ", tags copied too"
                        #     else:
                        #         msg += ", tags not copied"
                        #         #logging.info("not copying tags for " + f)
                    except Exception as e:
                        logging.exception(f'exception {e}')
                elif rule['action'] == 'Move':                    
                    if not dryrun:
                        # tags = get_tags(f)
                        target_folder = resolve_path(rule['target_folder'],p)
                        # print(p)
                        # print(target_folder)
                        target = Path(target_folder) / str(p).replace(':','') if ('keep_folder_structure' in rule.keys() and rule['keep_folder_structure']) else Path(target_folder) / p.name 
                        try:
                            # if not Path(target.parent).is_dir():
                            #     os.makedirs(target.parent)
                            # result = move(f, target)
                            result = advanced_move(f, target, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                            if result:
                                msg = "Moved " + f + " to " + str(result)
                                report['moved'] += 1
                                # remove_all_tags(f)
                                # if rule['keep_tags'] and tags: # TBD implement removing tags if keep_tags == False
                                #     set_tags(result, tags)
                                #     # if Path(get_tag_file_path(f)).is_file(): # TBD bring this back for sidecar files
                                #     #     os.remove(get_tag_file_path(f))
                                #     msg += ", with tags"
                        except Exception as e:
                            logging.exception(f'exception {e}')
                    else:
                        msg = "Moved " + f + " to " + target_folder
                elif rule['action'] == 'Rename':
                    if 'name_pattern' in rule.keys() and rule['name_pattern']:
                        newname = rule['name_pattern'].replace('<filename>', p.name)
                        newname = newname.replace('<folder>', p.parent.name)
                        rep = re.findall("<replace:(.*):(.*)>", newname)  # TBD what if there are multiple replace tokens?
                        newname = re.sub("<replace(.*?)>", '', newname)
                        #print(rep)
                        for r in rep:
                            newname = newname.replace(r[0], r[1])
                        #print(newname)
                        if not dryrun:
                            try:
                                #os.chdir(p.parent)                      
                                #print('renaming ' + str(p) + ' to ' + str(Path(p.parent) / newname))
                                result = advanced_move(p, Path(p.parent) / newname, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                                if result:
                                    newfullname = Path(p.parent / newname)
                                    if newfullname.is_dir(): # if renamed a folder check if its children are in the list, and if they are update their paths
                                        for i in range(len(files)):
                                            if p in Path(files[i]).parents:
                                                files[i] = files[i].replace(str(p),str(newfullname))
                                    # tf = get_tag_file_path(f) # TBD bring this back for sidecar files
                                    # if tf.is_file():
                                    #     os.chdir(tf.parent)
                                    #     os.rename(tf.name, newname + '.json')
                                    # tags = get_tags(f)
                                    # if tags:
                                    #     remove_all_tags(f)
                                    #     set_tags(newfullname, tags)
                                    report['renamed'] += 1
                                    msg = 'Renamed ' + f + ' to ' + str(result)
                            except Exception as e:
                                logging.exception(e)
                        else:
                            msg = 'Renamed ' + f + ' to ' + newname
                    else:
                        msg = 'Error: name pattern is missing for rule ' + rule['name']
                        logging.error("Name pattern is missing for rule " + rule['name'])
                elif rule['action'] == 'Move to subfolder':
                    # print('here')
                    # tags = get_tags(f)
                    target_subfolder = resolve_path(rule['target_subfolder'],p)
                    # print(f,tags,target_subfolder)
                    if p.parent.name != target_subfolder: # check if we're not already in the subfolder
                        #target = Path(rule['target_subfolder']) / p.name
                        if not dryrun:
                            result = advanced_move(f, p.parent / Path(target_subfolder) / p.name, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                            if result:
                                # remove_all_tags(f)
                                report['moved to subfolder'] += 1
                                msg = "Moved " + f + " to subfolder: " + str(target_subfolder)

                                # if rule['keep_tags'] and tags: # TBD implement removing tags if keep_tags == False
                                #     set_tags(result, tags)
                                #     msg += ", with tags"                                
                            #print("going to copy" + f + " to " + rule['target_folder'])
                        else:
                            msg = "Moved " + f + " to subfolder: " + str(target_subfolder)
                elif rule['action'] == 'Delete':
                    msg = "Deleted " + f
                    if not dryrun:
                        report['deleted'] += 1
                        os.remove(f)
                        # remove_all_tags(f)
                        # if get_tag_file_path(f).is_file(): # TBD implement this for sidecar files
                        #     os.remove(get_tag_file_path(f))
                elif rule['action'] == 'Send to Trash':
                    msg = "Sent to trash " + f
                    if not dryrun:
                        report['trashed'] += 1
                        send2trash(f)
                        # remove_all_tags(f)
                        # if get_tag_file_path(f).is_file(): # TBD implement this for sidecar files
                        #     os.remove(get_tag_file_path(f))
                # elif rule['action'] == 'Tag':            
                #     #if not dryrun:
                #     if rule['tags'] and not set(rule['tags']).issubset(set(get_tags(f))):
                #         add_tags(f, rule['tags'])
                #         msg = "Tagged " + f + " with " + str(rule['tags'])
                #         report['tagged'] += 1
                # elif rule['action'] == 'Remove tags':            
                #     #if not dryrun:
                #     if rule['tags'] and set(rule['tags']).issubset(set(get_tags(f))):
                #         remove_tags(f, rule['tags'])
                #         msg = "Removed these tags from  " + f + ": " + str(rule['tags'])
                #         report['untagged'] += 1
                # elif rule['action'] == 'Clear all tags':
                #     #if not dryrun:
                #     if get_tags(f):
                #         remove_all_tags(f)
                #         msg = "Cleared tags for  " + f
                #         report['cleared tags'] += 1                        
                if msg:
                    details.append(msg)
                    logging.debug(msg)
    # else:
    #     logging.debug("Rule "+rule['name'] + " disabled, skipping.")
    return report, details

# resolves patterns in taget_folder name 
# <group:group_name> replaced with the first tag that path is tagged with; if path has no tags in this group, replaced with None
# <type> replaced with the type of path (uses types from settings), if the type can't be resolved, replaced with None
# TBD: replacing with None should be optional

def resolve_path(target_folder, path):
    return target_folder.replace('<type>', get_file_type(path))

# returns file type based on settings, returns "Other" if type is not identified
def get_file_type(path):
    settings = load_settings()
    for ft in settings['file_types']:
        for p in settings['file_types'][ft].split(','):
            if fnmatch(path,p.strip()):
                return ft
    return 'Other'

def apply_all_rules(settings):
    report = {}
    details = []
    for rule in settings['rules']: # TBD this doesn't respect the order by id
        rule_report, rule_details = apply_rule(rule, settings['dryrun']) # TBD vN doesn't look optimal
        #print(rule_report)
        report = {k: report.get(k, 0) + rule_report.get(k, 0) for k in set(report) | set(rule_report)}
        details.extend(rule_details)
    return report, details

def get_files_affected_by_rule(rule, allow_empty_conditions = False):

    if (not 'conditions' in rule.keys() or not rule['conditions']) and not allow_empty_conditions:
        return([])
    found = []
    for f in rule['folders']:
        if Path(f).is_dir():
            found.extend(get_files_affected_by_rule_folder(rule, f, []))
        else:
            logging.error('Folder ' + f + ' in rule ' + rule['name'] + ' doesn\'t exist, skipping')
    if 'ignore_newest' in rule.keys() and rule['ignore_newest']:
        folders = {}
        result = []
        for f in found:
            if os.path.isfile(f):
                folder = Path(f).parent
                if not folder in folders.keys():
                    folders[folder] = []
                folders[folder].append(f)
            else:
                result.append(f)
        
        for val in folders.values():
            unsorted_files = {}
            for sf in val:
                unsorted_files[sf] = get_file_time(sf)
            sorted_files = {k: v for k, v in sorted(unsorted_files.items(), key=lambda item: -item[1])}
            target_list = list(sorted_files)[int(rule['ignore_N']):]
            result.extend(target_list)
            
        return result
    else:
        return sorted(list(set(found))) # returning only unique results
    #return found

def get_files_affected_by_rule_folder(rule, dirname, files_found = []):
    # check_files() # this is required to clean up the missing or incorrect file paths, TBD optimize this
    # files = [get_actual_filename(f) for f in get_all_files_from_db()] if dirname == ALL_TAGGED_TEXT else os.listdir(dirname) # TBD not sure if we need get_actual_filename() here
    files = os.listdir(dirname)
    out_files = files_found
    for f in files:
        if f != '.dc': # ignoring .dc folder TBD can be removed for now and brough back for sidecar files
            fullname = os.path.join(dirname,f)
            if rule['action'] == 'Move to subfolder' and ((Path(fullname).parent).name == rule['target_subfolder'] or (Path(fullname).is_dir() and f == rule['target_subfolder'])):
                conditions_met = False
            else:
                conditions_met = False if rule['condition_switch'] == 'any' else True
                conditions_met = True if rule['action'] == 'Filter' and rule['conditions'] == [] else conditions_met # return all files in tagger when no filters are added
                for c in rule['conditions']:
                    condition_met = False
                    if c['type'] == 'tags':
                        # TBD the basic version shouldn't work with tags so we're considering all tag-related conditions as not met - but this may be not correct in case where "none of" conditions apply
                        condition_met = False
                        # tags = get_tags(fullname)
                        # common_tags = [value for value in tags if value in c['tags']]                    
                        # if c['tag_switch'] == 'any':
                        #     condition_met = len(common_tags) > 0 # or better bool(common_tags)?
                        # elif c['tag_switch'] == 'all':
                        #     condition_met = set(common_tags) == set(c['tags']) and tags # tags must be not empty
                        # elif c['tag_switch'] == 'none':
                        #     condition_met = common_tags == []
                        # elif c['tag_switch'] == 'no tags':
                        #     condition_met = tags == []
                        # elif c['tag_switch'] == 'any tags':
                        #     condition_met = len(tags)>0
                        # elif c['tag_switch'] == 'tags in group':
                        #     condition_met = c['tag_group'] in get_tag_groups(fullname)
                    elif c['type'] == 'date':
                        try:
                            settings = load_settings(SETTINGS_FILE)
                            if c['age_switch'] == '>=':
                                if (float(time.time()) - get_file_time(fullname, settings['date_type']))/(3600*24) >= convert_to_days(float(c['age']), c['age_units']):
                                    condition_met = True
                            elif c['age_switch'] == '<':
                                if (float(time.time()) - get_file_time(fullname, settings['date_type']))/(3600*24) < convert_to_days(float(c['age']), c['age_units']):
                                    condition_met = True
                        except Exception as e:
                            logging.exception(e)
                    # elif c['type'] == 'newest N' and os.path.isfile(fullname): # TBD delete this!
                    #     condition_met = True
                    elif c['type'] == 'size' and os.path.isfile(fullname):                
                        factor = {'B': 1, 'KB' : 1024 ** 1, 'MB' : 1024 ** 2, 'GB' : 1024 ** 3, 'TB' : 1024 ** 4}
                        fsize = os.stat(fullname).st_size
                        target_size = float(c['size']) * factor[c['size_units']]
                        if c['size_switch'] == '>=':
                            condition_met = fsize >= target_size
                        elif c['size_switch'] == '<':
                            condition_met = fsize < target_size
                    elif c['type'] == 'name':
                        if not 'name_switch' in c.keys(): # TBD this is temporary to support old conditions that don't have this switch yet
                            c['name_switch'] = 'matches'
                        for m in c['filemask'].split(','):  # TBD need to reflect this in help - it works like this: 'matches any' or 'doesn't match all'
                            condition_met = condition_met or fnmatch(f, m.strip())
                            if condition_met:
                                break
                        condition_met = condition_met == (c['name_switch'] == 'matches')
                    elif c['type'] == 'type' and os.path.isfile(fullname):
                        condition_met = (get_file_type(fullname) == c['file_type']) == (c['file_type_switch'] == 'is')
                    
                    # if condition_met:
                    #     print(c['type'] + ' condition met for ' + fullname)

                    if rule['condition_switch'] == 'any':
                        conditions_met = conditions_met or condition_met
                        if conditions_met:
                            break
                    elif rule['condition_switch'] == 'all':
                        conditions_met = conditions_met and condition_met
                        if not conditions_met:
                            break
                    elif rule['condition_switch'] == 'none':
                        conditions_met = conditions_met and not condition_met
                        if not conditions_met:                    
                            break

            #print(fullname)
            #print(conditions_met)
            if conditions_met:
                out_files.append(os.path.normpath(fullname))
            
            # Important: it recurses for 'Rename' action, but doesn't recurse for other actions if the folder matches the conditions
            # That's because the whole folder will be copied/moved/trashed and it doesn't make sense to check its files
            # if (rule['action'] in ('Rename', 'Tag', 'Remove tags', 'Clear all tags') or not conditions_met) and os.path.isdir(fullname) and rule['recursive']:
            if (rule['action'] == 'Rename' or not conditions_met) and os.path.isdir(fullname) and rule['recursive']:
                get_files_affected_by_rule_folder(rule, fullname, out_files)
    return out_files

def get_file_time(filename, date_type = 0):
    if Path(filename).exists():
        if date_type == 0: # earliest of modified & created
            return min(os.path.getmtime(filename), os.path.getctime(filename))
        elif date_type == 1: # modified
            return os.path.getmtime(filename)
        elif date_type == 2: # created
            return os.path.getctime(filename)        
        elif date_type == 3: # latest of modified & created
            return max(os.path.getmtime(filename), os.path.getctime(filename))        
        elif date_type == 4: # last access
            return os.path.getatime(filename)   
    else:
        logging.error('File not found: ' + filename)

def convert_to_days(value, units):
    if units == 'days':
        return value
    elif units == 'weeks':
        return value * 7
    elif units == 'months':
        return value * 30.43 # TBD vN this is a bit rough
    elif units == 'years':
        return value * 365.25 # TBD vN this is a bit rough

def get_folder_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def get_size(filepath):
    if Path(filepath).is_dir():
        return get_folder_size(filepath)
    elif Path(filepath).is_file():     
        #print(os.path.getsize(filepath))   
        return os.path.getsize(filepath)
    else:
        return 0 #TBD maybe return an error?

def get_rule_by_name(name):
    settings = load_settings(SETTINGS_FILE)
    for r in settings['rules']:
        if r['name'] == name:
            return r

def get_rule_by_id(rule_id, rules = []):
    if not rules:
        rules = load_settings(SETTINGS_FILE)['rules']
    for r in rules:
        if int(r['id']) == rule_id:
            return r

def advanced_copy(source_path, target_path, overwrite = False):  
    return advanced_move(source_path, target_path, overwrite, True)

def copy_file_or_dir(source_path, target_path):
    if Path(source_path).is_file():
        res = copy2(source_path,target_path)
    elif Path(source_path).is_dir():
        res = copytree(source_path, target_path)
    else:
        res = False
    return res

def remove_file_or_dir(filepath):
    if Path(filepath).is_dir():
        rmtree(filepath)
    elif Path(filepath).is_file():
        os.remove(filepath)
    else:
        return False

def advanced_move(source_path, target_path, overwrite = False, copy = False):  # copy = False means move = TBD improve this
    # print('advanced move')
    # print(source_path)
    # print(target_path)
    # print(overwrite)
    # print(copy)
    if not os.path.exists(source_path):
        return False
    if not os.path.exists(target_path):
        #p Target path doesnt exist, simply moving/copying
        try:
            if not Path(target_path).parent.exists():
                os.makedirs(Path(target_path).parent)
            if copy:
                res = copy_file_or_dir(source_path, target_path)
            else:
                res = move(source_path, target_path)
            return res
        except Exception as e:
            logging.exception(e)
            return False  
    else:
        #print('sps ' + str(get_size(source_path)))
        #print('tps ' + str(get_size(target_path)))
        if get_size(source_path) == get_size(target_path): # file/folder with the same size exists         
            #print('its file/dir with the same size, skipping')
            #remove_file_or_dir(source_path)
            if not copy:
                remove_file_or_dir(source_path) # if we're moving the file/folder and it's already there just delete the source file/folder
                return target_path
            else:                
                return False 
        else:
            # It's a file/dir with different size
            if overwrite:
                try:
                    remove_file_or_dir(target_path)
                    if copy:
                        res = copy_file_or_dir(source_path, target_path)
                    else:
                        res = move(source_path, target_path)
                    return res
                except Exception as e:
                    logging.exception(e)
                    return False
            else:
                # Getting an available name
                new_name = get_nonexistent_path(source_path, target_path)
                if new_name:
                    try:
                        if copy:
                            res = copy_file_or_dir(source_path, new_name)
                        else:
                            res = move(source_path, new_name)
                        return res
                    except Exception as e:
                        logging.exception(e)
                        return False
                else:
                    return False

def get_nonexistent_path(src, dst):
    if not os.path.exists(dst): #based on how we call it we should never get here
        return dst
    filename, file_extension = os.path.splitext(dst)
    match = re.findall("^(.+)\s\((\d+)\)$", filename)
    i = 1
    if match: #filename already has (i) in it
        filename = match[0][0]
        i = int(match[0][1])+1
       
    new_fname = "{} ({}){}".format(filename, i, file_extension)
    while os.path.exists(new_fname):
        if get_size(src) == get_size(new_fname):
            return False
        i += 1
        new_fname = "{} ({}){}".format(filename, i, file_extension)
    return new_fname


if not Path(APP_FOLDER).is_dir():
    Path(APP_FOLDER).mkdir()