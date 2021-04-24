from json import (load as jsonload, dump as jsondump)
import json
import os
import re
import time
import datetime
import stat
from shutil import copy2, move, copytree, rmtree
from send2trash import send2trash
import subprocess
from pathlib import Path
import logging
from fnmatch import fnmatch
import sqlite3
from declutter_sidecar_files import *
import glob

VERSION = '1.09'
APP_FOLDER = os.path.join(os.getenv('APPDATA'), "DeClutter")
LOG_FILE = os.path.join(APP_FOLDER, "DeClutter.log")
DB_FILE = os.path.join(APP_FOLDER, "DeClutter.db")
SETTINGS_FILE = os.path.join(APP_FOLDER, "settings.json")
ALL_TAGGED_TEXT = 'All tagged files and folders'

logging.basicConfig(level=logging.DEBUG, filename= LOG_FILE, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")

def load_settings(settings_file = SETTINGS_FILE):
    if not os.path.isfile(settings_file):
        settings = {}
        settings['version'] = VERSION
        settings['current_folder'] = ''
        settings['current_drive'] = ''
        settings['folders'] = [] # TBD legacy
        settings['tags'] = []
        settings['filter_tags'] = []
        settings['rules'] = []
        settings['recent_folders'] = []
        settings['rule_exec_interval'] = 300
        settings['dryrun'] = False
        settings['tag_filter_mode'] = "any"
        settings['date_type'] = 0
        settings['view_show_filter'] = False
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
        settings['recent_folders'] = settings['recent_folders'] if 'recent_folders' in settings.keys() else []
        settings['current_drive'] = settings['current_drive'] if 'current_drive' in settings.keys() else ""
        settings['current_folder'] = settings['current_folder'] if 'current_folder' in settings.keys() else ""  
        settings['folders'] = settings['folders'] if 'folders' in settings.keys() else []
        settings['tags'] = settings['tags'] if 'tags' in settings.keys() else []
        settings['filter_tags'] = settings['filter_tags'] if 'filter_tags' in settings.keys() else []
        settings['rules'] = settings['rules'] if 'rules' in settings.keys() else []
        settings['rule_exec_interval'] = settings['rule_exec_interval'] if 'rule_exec_interval' in settings.keys() else 300
        settings['dryrun'] = settings['dryrun'] if 'dryrun' in settings.keys() else False
        settings['tag_filter_mode'] = settings['tag_filter_mode'] if 'tag_filter_mode' in settings.keys() else "any"
        settings['date_type'] = settings['date_type'] if 'date_type' in settings.keys() else 0
        settings['view_show_filter'] = settings['view_show_filter'] if 'view_show_filter' in settings.keys() else False
        default_formats = {'Audio':'*.aac,*.aiff,*.ape,*.flac,*.m4a,*.m4b,*.m4p,*.mp3,*.ogg,*.oga,*.mogg,*.wav,*.wma', \
            'Video':'*.3g2,*.3gp,*.amv,*.asf,*.avi,*.flv,*.gif,*.gifv,*.m4v,*.mkv,*.mov,*.qt,*.mp4,*.m4v,*.mpg,*.mp2,*.mpeg,*.mpe,*.mpv,*.mts,*.m2ts,*.ts,*.ogv,*.webm,*.wmv,*.yuv', \
            'Image':'*.jpg,*.jpeg,*.exif,*.tif,*.bmp,*.png,*.webp'}
        settings['file_types'] = settings['file_types'] if 'file_types' in settings.keys() else default_formats
    return settings


def save_settings(settings_file, settings):
    # TBD this should be carefully checked before writing
    #print(settings)
    if not Path(settings_file).parent.is_dir():
        try:
            Path(settings_file).parent.mkdir()
        except Exception as e:
            logging.exception(f'exception {e}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f, indent=4)

# def get_all_tags():
#     #return load_settings(SETTINGS_FILE)['tags']
#     return get_all_tags_from_db()

def get_all_files(dirname, files_found = [], recursive = True):
    files = os.listdir(dirname)
    out_files = files_found
    for f in files:
        if f != '.dc': # ignoring .dc folder, TBD can be removed for now and brought back for sidecar files
            fullname = os.path.join(dirname,f)
            if not os.path.isdir(fullname): # TBD v2 add folders support
                out_files.append(fullname)
            if os.path.isdir(fullname) and recursive:            # if it's a folder and if we have 'recursive' set to true
                get_all_files(fullname, out_files, recursive)
    return out_files

def build_file_tree(parent, dirname, tags_filter = [], recurse = False, filter_mode = 'any'):
    found = {}
    try:
        for f in next(os.walk(dirname))[1]:
            if f != ".dc": #TBD can be removed for now and brough back for sidecar files
                fullname = os.path.join(dirname,f)                       
                tags = get_tags(fullname)
                children = {}
                #children = build_file_tree(fullname, fullname, tags_filter, recurse, filter_mode)
                if children:
                    if recurse:
                        found.update({f:{'type': 'folder', 'path': fullname, 'tags':tags, 'children' : children}})
                    else:
                        found.update({f:{'type': 'folder', 'path': fullname, 'tags':tags}})
                else: #no children but is tagged
                    #found.update({f:{'type': 'folder', 'path' : fullname, 'tags':tags}}) # this doesn't consider tag filter
                    if filter_mode == "any": 
                        if (tags_filter and set(tags_filter).intersection(set(tags))) or tags_filter == []:
                            found.update({f:{'type': 'folder', 'path' : fullname, 'tags':tags}})
                    elif filter_mode == "all":
                        if (tags_filter and set(tags_filter).issubset(set(tags))) or tags_filter == []:
                            found.update({f:{'type': 'folder', 'path' : fullname, 'tags':tags}})                
        for f in next(os.walk(dirname))[2]:
            fullname = os.path.join(dirname,f)
            tags = get_tags(fullname)
            #found.update({f:{'type': 'file', 'path' : fullname, 'tags':tags}}) # this doesn't consider tag filter
            if filter_mode == "any":
                if (tags_filter and set(tags_filter).intersection(set(tags))) or tags_filter == []:
                    found.update({f:{'type': 'file', 'path' : fullname, 'tags':tags}})
            elif filter_mode == "all":
                if (tags_filter and set(tags_filter).issubset(set(tags))) or tags_filter == []:
                    found.update({f:{'type': 'file', 'path' : fullname, 'tags':tags}})
    except Exception as e:
        logging.exception(e)
    return found

def apply_rule(rule, dryrun = False):
    report = {'copied':0, 'moved':0, 'moved to subfolder':0, 'deleted':0, 'trashed':0, 'tagged':0, 'untagged':0, 'cleared tags':0, 'renamed':0}
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
                                # if not Path(target.parent).is_dir(): #not sure if this is needed - not needed because copytree creates the full tree
                                #     os.makedirs(target.parent)
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
                                    # if not Path(target.parent).is_dir():
                                    #     os.makedirs(target.parent)
                                    # result = copy2(f, target)
                                    result = advanced_copy(f, target, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                                else:
                                    msg = "Copied " + f + " to " + str(result)
                                if result:
                                    report['copied'] += 1
                                    msg = "Copied " + f + " to " + str(result)
                        if rule['keep_tags']:
                            tags = get_tags(f)
                            if set_tags(result, tags):
                                #logging.info("Copied tags for " + f)
                                msg += ", tags copied too"
                            else:
                                msg += ", tags not copied"
                                #logging.info("not copying tags for " + f)
                    except Exception as e:
                        logging.exception(f'exception {e}')
                elif rule['action'] == 'Move':                    
                    if not dryrun:
                        tags = get_tags(f)
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
                                remove_all_tags(f)
                                if rule['keep_tags'] and tags: # TBD implement removing tags if keep_tags == False
                                    set_tags(result, tags)
                                    # if Path(get_tag_file_path(f)).is_file(): # TBD bring this back for sidecar files
                                    #     os.remove(get_tag_file_path(f))
                                    msg += ", with tags"
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
                                #os.rename(p.name, newname) #TBD what if file exists?
                                #print('renaming ' + str(p) + ' to ' + str(Path(p.parent) / newname))
                                result = advanced_move(p, Path(p.parent) / newname, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                                if result:
                                    newfullname = Path(p.parent / newname)
                                    if newfullname.is_dir(): # if renamed a folder check if its children are in the list, and if they are update their paths
                                        for i in range(0, len(files)):
                                            if p in Path(files[i]).parents:
                                                files[i] = files[i].replace(str(p),str(newfullname))
                                    # tf = get_tag_file_path(f) # TBD bring this back for sidecar files
                                    # if tf.is_file():
                                    #     os.chdir(tf.parent)
                                    #     os.rename(tf.name, newname + '.json')
                                    tags = get_tags(f)
                                    if tags:
                                        remove_all_tags(f)
                                        set_tags(newfullname, tags)
                                    report['renamed'] += 1
                                    msg = 'Renamed ' + f + ' to ' + result
                            except Exception as e:
                                logging.exception(e)
                        else:
                            msg = 'Renamed ' + f + ' to ' + newname
                    else:
                        msg = 'Error: name pattern is missing for rule ' + rule['name']
                        logging.error("Name pattern is missing for rule " + rule['name'])
                elif rule['action'] == 'Move to subfolder':
                    # print('here')
                    tags = get_tags(f)
                    target_subfolder = resolve_path(rule['target_subfolder'],p)
                    # print(f,tags,target_subfolder)
                    if p.parent.name != target_subfolder: # check if we're not already in the subfolder
                        #target = Path(rule['target_subfolder']) / p.name
                        if not dryrun:
                            result = advanced_move(f, p.parent / Path(target_subfolder) / p.name, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                            if result:
                                remove_all_tags(f)
                                report['moved to subfolder'] += 1
                                msg = "Moved " + f + " to subfolder: " + str(target_subfolder)

                                if rule['keep_tags'] and tags: # TBD implement removing tags if keep_tags == False
                                    set_tags(result, tags)
                                    msg += ", with tags"                                
                            #print("going to copy" + f + " to " + rule['target_folder'])
                        else:
                            msg = "Moved " + f + " to subfolder: " + str(target_subfolder)
                elif rule['action'] == 'Delete':
                    msg = "Deleted " + f
                    if not dryrun:
                        report['deleted'] += 1
                        os.remove(f)
                        remove_all_tags(f)
                        # if get_tag_file_path(f).is_file(): # TBD implement this for sidecar files
                        #     os.remove(get_tag_file_path(f))
                elif rule['action'] == 'Send to Trash':
                    msg = "Sent to trash " + f
                    if not dryrun:
                        report['trashed'] += 1
                        send2trash(f)
                        remove_all_tags(f)
                        # if get_tag_file_path(f).is_file(): # TBD implement this for sidecar files
                        #     os.remove(get_tag_file_path(f))
                elif rule['action'] == 'Tag':            
                    #if not dryrun:
                    if rule['tags'] and not set(rule['tags']).issubset(set(get_tags(f))):
                        add_tags(f, rule['tags'])
                        msg = "Tagged " + f + " with " + str(rule['tags'])
                        report['tagged'] += 1
                elif rule['action'] == 'Remove tags':            
                    #if not dryrun:
                    if rule['tags'] and set(rule['tags']).issubset(set(get_tags(f))):
                        remove_tags(f, rule['tags'])
                        msg = "Removed these tags from  " + f + ": " + str(rule['tags'])
                        report['untagged'] += 1
                elif rule['action'] == 'Clear all tags':
                    #if not dryrun:
                    if get_tags(f):
                        remove_all_tags(f)
                        msg = "Cleared tags for  " + f
                        report['cleared tags'] += 1                        
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
    final_path = target_folder.replace('<type>', get_file_type(path))
    # final_path = re.sub("<group:(.*)>", get_file_tag_by_group('\1'), target_folder)
    # final_path = re.sub("<group:(.*)>", '\\1', target_folder)
    rep = re.findall("(<group:(.*?)>)", target_folder)
    for r in rep:
        group_tags = get_file_tags_by_group(r[1],path)
        # print(group_tags)
        final_path = final_path.replace(r[0],group_tags[0] if group_tags else 'None')
    
    return final_path

    # rep = re.findall("<replace:(.*):(.*)>", newname)
    # newname = re.sub("<replace(.*?)>", '', newname)
    # for r in rep:
    #     newname = newname.replace(r[0], r[1])

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
    for rule in settings['rules']:
        rule_report, rule_details = apply_rule(rule, load_settings()['dryrun']) # TBD vN doesn't look optimal / had to use load_settings for testing, should be just settings
        #print(rule_report)
        report = {k: report.get(k, 0) + rule_report.get(k, 0) for k in set(report) | set(rule_report)}
        details.extend(rule_details)
    return report, details

def get_files_affected_by_rule(rule, allow_empty_conditions = False):
    #print("Rule: "+rule['name'])

    if (not 'conditions' in rule.keys() or not rule['conditions']) and not allow_empty_conditions:
        return([])
    found = []
    for f in rule['folders']:
        if Path(f).is_dir() or f == ALL_TAGGED_TEXT:
            found.extend(get_files_affected_by_rule_folder(rule, f, []))
        else:
            logging.error('Folder ' + f + ' in rule ' + rule['name'] + ' doesn\'t exist, skipping')
        #print(found)
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
        
    files = [get_actual_filename(f) for f in get_all_files_from_db()] if dirname == ALL_TAGGED_TEXT else os.listdir(dirname)
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
                        # print(fullname)
                        tags = get_tags(fullname)
                        # print(tags)
                        common_tags = [value for value in tags if value in c['tags']]                    
                        # print(common_tags)
                        if c['tag_switch'] == 'any':
                            condition_met = len(common_tags) > 0 # or better bool(common_tags)?
                        elif c['tag_switch'] == 'all':
                            condition_met = common_tags == c['tags'] and tags # tags must be not empty
                            # print(condition_met)
                        elif c['tag_switch'] == 'none':
                            condition_met = common_tags == []
                        elif c['tag_switch'] == 'no tags':
                            condition_met = tags == []
                        elif c['tag_switch'] == 'any tags':
                            condition_met = len(tags)>0
                        elif c['tag_switch'] == 'tags in group':
                            # print(get_tag_groups(fullname))
                            condition_met = c['tag_group'] in get_tag_groups(fullname)
                        # if condition_met:
                        #     print(fullname,tags,common_tags,c['tag_switch'])
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
            
            # Important: it recurses for 'Rename' and 'Tag' actions, but doesn't recurse for other actions if the folder matches the conditions
            # That's because the whole folder will be copied/moved/trashed and it doesn't make sense to check its files
            if (rule['action'] in ('Rename', 'Tag', 'Remove tags', 'Clear all tags') or not conditions_met) and os.path.isdir(fullname) and rule['recursive']:
            #if not conditions_met and os.path.isdir(fullname) and rule['recursive']:
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

def advanced_move(source_path, target_path, overwrite = False, copy = False):  # copy = Fale means move = TBD improve this
    # print('advanced move')
    # print(source_path)
    # print(target_path)
    # print(overwrite)
    # print(copy)
    if not os.path.exists(source_path):
        return False
    # TBD this may cause problems if some file is tagged inside the folder and the folder is moved/renamed - 
    # it will be considered as a different folder since size will be different
    if not os.path.exists(target_path):
        #print('path doesnt exist, simply moving')
        try:
            if not Path(target_path).parent.exists():
                os.makedirs(Path(target_path).parent)
            if copy:
                res = copy_file_or_dir(source_path, target_path)
            else:
                res = move(source_path, target_path)
            return res
        except Exception as e:
            #print(e)
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
            #return target_path # TBD maybe should return something else
        else:
            #print('its a file/dir with different size')
            if overwrite:
                try:
                    remove_file_or_dir(target_path)
                    if copy:
                        res = copy_file_or_dir(source_path, target_path)
                    else:
                        res = move(source_path, target_path)
                    return res
                except Exception as e:
                    #print(e)
                    logging.exception(e)
                    return False
            else:
                #print('getting new name')
                new_name = get_nonexistent_path(source_path, target_path)
                if new_name:
                    #print('got new name: ' + new_name)                        
                    try:
                        if copy:
                            res = copy_file_or_dir(source_path, new_name)
                        else:
                            res = move(source_path, new_name)
                        return res
                    except Exception as e:
                        #print(e)
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

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE files (id INTEGER PRIMARY KEY, filepath VARCHAR NOT NULL UNIQUE)")
    c.execute("CREATE TABLE tags (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE)")
    c.execute("CREATE TABLE file_tags (file_id INTEGER, tag_id INTEGER)")
    conn.commit()
    conn.close()        

def tag_set_color(tag, color):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()    
    c.execute("UPDATE tags set color = ? WHERE name = ?", (color,tag))
    conn.commit()
    conn.close()

def tag_get_color(tag):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()    
    c.execute("SELECT color FROM tags WHERE name = ?", (tag,))
    row = c.fetchone()[0]
    conn.close()
    return row

def create_tag(tag, group_id = 1):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()    
    c.execute("SELECT max(list_order) from tags WHERE tags.group_id=?",(group_id,))
    row = c.fetchone()[0]
    if row is None:
        count = 1
    else:
        count = row+1

    c.execute("INSERT INTO tags VALUES (null, ?, ?, null, ?)", (tag,count,group_id)) # TBD replace 1 here
    tag_id = c.lastrowid
    conn.commit()
    conn.close()
    return tag_id

def move_tag(tag, direction): # Moves tag up or down in lists
    tags = get_all_tags()
    if tag == tags[0] and direction == "up":
        print("it's at the top, can't move")
        return
    if tag == tags[-1] and direction == "down":
        print("it's at the bottom, can't move")
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    ind = tags.index(tag)
    if direction == "down":
        swap = tags[ind+1]
        tags[ind] = swap
        tags[ind+1] = tag
    elif direction == "up":
        swap = tags[ind-1]
        tags[ind] = swap
        tags[ind-1] = tag
    
    for t in tags:
        c.execute("UPDATE tags set list_order = ? WHERE name = ?", (tags.index(t)+1,t))

    conn.commit()
    conn.close()    

def rename_group(old_group, new_group):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tag_groups set name = ? WHERE name = ?", (new_group,old_group))
    conn.commit()
    conn.close()     

def rename_tag(old_tag, new_tag):
    tagged_files = get_files_by_tag(old_tag)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if new_tag in get_all_tags():
        delete_tag(old_tag)
    else:
        c.execute("UPDATE tags set name = ? WHERE name = ?", (new_tag,old_tag))
    conn.commit()
    conn.close()   
    # updating tagged files
    for f in tagged_files:
        add_tag(f,new_tag) 
    # updating rules and conditions
    settings = load_settings()
    for r in settings['rules']:  # TBD this should be also moved to lib?
        if old_tag in r['tags']:
            # print('updating',r['name'])
            r['tags'].remove(old_tag)
            r['tags'].append(new_tag)
        for c in r['conditions']:
            if c['type'] == 'tags' and old_tag in c['tags']:
                # print('updating condition for',r['name'])
                c['tags'].remove(old_tag)
                c['tags'].append(new_tag)
    save_settings(SETTINGS_FILE, settings)             

def set_tags(filename, tags): # TBD optimize this
    # print('set_tags',filename,tags)
    filename = os.path.normpath(filename).lower()
    # filename_lower = filename.lower() # this may be redundant, I'm being extra cautios here
    # print(filename_lower)
    # print('setting tags',filename,tags)
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # print(filename)
        # c.execute("SELECT id from files WHERE LOWER(filepath) = ?", (filename_lower,))
        c.execute("SELECT id from files WHERE filepath = ?", (filename,))
        row = c.fetchone()
        # print(row)
        if row is None:               
            c.execute("INSERT INTO files VALUES (null, ?)", (filename,))
            file_id = c.lastrowid   
        else:
            file_id = row[0]  
            c.execute("DELETE FROM file_tags WHERE file_tags.file_id = ?", (file_id,))        
        for t in tags:
            c.execute("SELECT id from tags WHERE name = ?", (t,))
            row = c.fetchone()
            if row is None:               
                # c.execute("INSERT INTO tags VALUES (null, ?)", (t,))
                # tag_id = c.lastrowid
                tag_id = create_tag(t)
            else:            
                tag_id = row[0] 
            c.execute("INSERT INTO file_tags VALUES (?,?)", (file_id,tag_id))
            #print('inserting tags for {}, {}'.format(file_id,tag_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.exception(e)
        return False

# set_tags('D:\dc_test\Projects\Seeds\seeds4.jpg',['Seeds'])

def get_tags(filename):
    filename = os.path.normpath(filename).lower()
    #filename = filename.lower()
    #print(type(filename))
    #print('getting tags for ' + filename)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # tags = [f[0] for f in c.execute("SELECT tags.name FROM file_tags JOIN tags on tag_id = tags.id WHERE file_tags.file_id = (SELECT id from files WHERE LOWER(filepath) = ?) order by tags.group_id, tags.list_order", (str(filename),))]
    tags = [f[0] for f in c.execute("SELECT tags.name FROM file_tags JOIN tags on tag_id = tags.id WHERE file_tags.file_id = (SELECT id from files WHERE filepath = ?) order by tags.group_id, tags.list_order", (filename,))]
    #print(filename)
    #print(tags)
    if not tags:
        c.execute("DELETE FROM files WHERE filepath = ?", (filename,))  
        conn.commit()
    conn.close()
    return tags

# returns list of tuples [(tag, group_id)]
def get_tags_by_group_ids(filename):
    filename = os.path.normpath(filename).lower()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tags = [f for f in c.execute("SELECT name, group_id FROM file_tags JOIN tags on tag_id = tags.id WHERE file_tags.file_id = (SELECT id from files WHERE filepath = ?)", (filename,))]
    if not tags:
        c.execute("DELETE FROM files WHERE filepath = ?", (filename,))  
        conn.commit()
    conn.close()
    return tags

# print(get_tags_by_group_ids(r'D:\DIM\WinFiles\Downloads\Tagged\Birthday.mp4_snapshot_00.19.000.jpg'))

def add_tags(filename, tags):
    cur_tags = get_tags(filename)
    set_tags(filename, list(set(tags + cur_tags)))

def add_tag(filename, tag):
    add_tags(filename, [tag])

def remove_tags(filename, tags):
    filename = os.path.normpath(filename).lower()
    # filename = filename.lower()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()    
    c.execute("SELECT id from files WHERE filepath = ?", (filename,))
    row = c.fetchone()
    if row is None:               
        c.execute("INSERT INTO files VALUES (null, ?)", (filename,))
        file_id = c.lastrowid   
    else:
        file_id = row[0]  
    for t in tags:
        c.execute("SELECT id from tags WHERE name = ?", (t,))
        tag_id = c.fetchone()[0] # TBD this may lead to crash
        c.execute("DELETE FROM file_tags WHERE file_tags.file_id = ? AND file_tags.tag_id = ?", (file_id,tag_id))  
    #tags = [f[0] for f in c.execute("SELECT tags.name FROM file_tags JOIN tags on tag_id = tags.id WHERE file_tags.file_id = (SELECT id from files WHERE filepath = ?)", (filename,))]
    conn.commit()
    conn.close()

def remove_all_tags(filename):
    filename = os.path.normpath(filename).lower()
    # filename = filename.lower()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()    
    # c.execute("SELECT id from files WHERE LOWER(filepath) = ?", (filename,))
    c.execute("SELECT id from files WHERE filepath = ?", (filename,))
    row = c.fetchone()
    #print(row)
    if row is None:
        return
    else:
        file_id = row[0]
        c.execute("DELETE FROM file_tags WHERE file_tags.file_id = ?", (file_id,))  
        c.execute("DELETE FROM files WHERE id = ?", (file_id,))  
        conn.commit()
    conn.close()   

def get_all_files_from_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    files = [f[0] for f in c.execute("SELECT filepath FROM files")]
    conn.close()
    return files

def get_all_tags():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tags = [f[0] for f in c.execute("SELECT name FROM tags ORDER by list_order")]
    conn.close()
    return tags

def get_all_tags_by_group_id(id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tags = [f[0] for f in c.execute("SELECT name FROM tags WHERE group_id=?",(id,))]
    conn.close()
    return tags    


def get_all_tag_groups():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    groups = [f[0] for f in c.execute("SELECT name FROM tag_groups ORDER by list_order")]
    conn.close()
    return groups

def get_tag_groups(filename):
    filename = os.path.normpath(filename).lower()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tags = [f[0] for f in c.execute("SELECT name from tag_groups WHERE id in (SELECT tags.group_id FROM file_tags JOIN tags on tag_id = tags.id WHERE file_tags.file_id = (SELECT id from files WHERE filepath = ?) order by tags.group_id)", (filename,))]
    conn.close()
    return tags

def get_files_by_tags(tags : []):
    if tags == []:
        return []
    all_files = get_files_by_tag(tags[0])
    if all_files:
        for i in range(1,len(tags)):
            all_files = list(set(all_files).intersection(set(get_files_by_tag(tags[i]))))
            if not all_files:
                return []
    else:
        return []
    return all_files

def get_files_by_tag(tag):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    files = [f[0] for f in c.execute("SELECT files.filepath FROM file_tags JOIN files on file_id = files.id WHERE file_tags.tag_id = (SELECT id from tags WHERE name = ?)", (tag,))]
    conn.close()
    return files

# print(get_files_by_tags(['Chains of Sanity','forever']))

def remove_tag(filename, tag):
    remove_tags(filename, [tag])

def delete_tag(tag): # Removes tag from the database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()    
    c.execute("DELETE FROM file_tags WHERE file_tags.tag_id IN (SELECT id from tags WHERE name = ?)", (tag,))
    c.execute("DELETE FROM tags WHERE name = ?", (tag,))
    conn.commit()
    conn.close()

def delete_group(group_id, keep_tags):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()    
    c.execute("DELETE FROM tag_groups WHERE id = ?", (group_id,))
    if keep_tags:
        # print('moving tags to default group')
        c.execute("UPDATE tags set group_id = 1 WHERE group_id = ?", (group_id,))
    else:
        # print('deleting tags and tagged files')
        c.execute("DELETE FROM file_tags WHERE file_tags.tag_id IN (SELECT id from tags WHERE group_id = ?)", (group_id,))
        c.execute("DELETE FROM tags WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()    

# returns all tags and groups with metadata - used for tag model generation
def get_tags_and_groups():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()    
    groups = c.execute("SELECT id, name, list_order, widget_type, name_shown FROM tag_groups ORDER BY list_order")
    tree = {}
    for g in groups.fetchall():
        # print(g)
        tree[g[1]] = {'id':g[0],'list_order':g[2],'widget_type':g[3],'name_shown':g[4],'type':'group', 'name':g[1]}
        tags = c.execute("SELECT id, name, list_order, color FROM tags WHERE group_id=? ORDER BY list_order", (g[0],))
        tree[g[1]]['tags'] = []
        for t in tags.fetchall():
            tree[g[1]]['tags'].append({'type':'tag','id':t[0],'name':t[1],'list_order':t[2],'color':t[3],'group_id':g[0]})
        # print(tags.fetchall())
    # print(tree)
    # c.execute("DELETE FROM tags WHERE name = ?", (tag,))
    # conn.commit()
    conn.close()    
    return tree

def create_group(name, widget_type=0, name_shown=1):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()    
    c.execute("SELECT max(list_order) from tag_groups")
    row = c.fetchone()[0]
    if row is None:
        count = 1
    else:
        count = row+1

    c.execute("INSERT INTO tag_groups VALUES (null, ?, ?, ?, ?)", (name,count,widget_type,name_shown))
    group_id = c.lastrowid
    conn.commit()
    conn.close()
    return group_id

def move_tag_to_group(tag_id,group_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT max(list_order) from tags where group_id=?", (group_id,))
    row = c.fetchone()[0]
    if row is None:
        count = 1
    else:
        count = row+1    
    c.execute("UPDATE tags set (group_id, list_order) = (?,?) WHERE id = ?", (group_id,count,tag_id))
    conn.commit()
    conn.close()

def move_tag_to_tag(tag1, tag2, position): # tags are in format {'name':name,'id':id,'list_order':list_order,'group_id':group_id}
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # print(tag1,tag2)
    c.execute("SELECT list_order,group_id from tags WHERE id = ?", (tag2['id'],))
    row = c.fetchone()
    new_list_order = row[0] if int(position)==1 else row[0]+1
    group = row[1]
    # print('group',group)    
    # print('new_list_order',new_list_order)
    # if tag1['group_id'] != tag2['group_id']:
    #     # print('different group, moving')
    #     c.execute("UPDATE tags set group_id = ? WHERE id = ?", (tag2['group_id'], tag1['id']))
    #     conn.commit()
    c.execute("SELECT id from tags WHERE (group_id,list_order) = (?,?)", (group,new_list_order))
    row = c.fetchone()
    if row is not None:
        # print('incrementing list_order')
        c.execute("UPDATE tags set list_order = list_order+1 WHERE group_id = ? and list_order >= ?", (group,new_list_order))
    c.execute("UPDATE tags set (list_order,group_id) = (?,?) WHERE id = ?", (new_list_order, group, tag1['id']))
    conn.commit()
    conn.close() 

def move_group_to_group(group1,group2,position):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT list_order from tag_groups WHERE id = ?", (group2['id'],))
    row = c.fetchone()
    new_list_order = row[0] if int(position)==1 else row[0]+1
    # print(new_list_order)
    c.execute("SELECT id from tag_groups WHERE list_order = ?", (new_list_order,))
    row = c.fetchone()
    if row is not None:
        # print(row[0])
        # print('incrementing list_order')
        c.execute("UPDATE tag_groups set list_order = list_order+1 WHERE list_order >= ?", (new_list_order,))
    c.execute("UPDATE tag_groups set list_order = ? WHERE id = ?", (new_list_order, group1['id']))
    conn.commit()
    conn.close()    

def get_file_tags_by_group(group, filename):
    filename = os.path.normpath(filename).lower()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM tag_groups WHERE name = ?", (group,))
    row = c.fetchone()
    tags = []
    if row is not None:
        group_id = row[0]
        tags = [f[0] for f in c.execute("SELECT tags.name FROM file_tags JOIN tags on tag_id = tags.id WHERE file_tags.file_id = (SELECT id from files WHERE filepath = ?) AND tags.group_id = ?", (filename,group_id))]
    conn.close()
    return tags

#print(get_file_tag_by_group('Default','D:\\DIM\\WinFiles\\Downloads\\1.png'))
# print(get_file_tags_by_group('Project','D:\\DIM\\WinFiles\\Downloads\\1.png'))
# print(resolve_path("abc/<type>/<group:Rating>/sdf/345", "D:\\DIM\\WinFiles\\Downloads\\1.png"))

# import unicodedata
# title = u"⭐️⭐️"
# path = unicodedata.normalize('NFKD', title).encode('utf8')
# os.mkdir(path)
# encode('ascii', 'replace'))

def check_files(): # TBD need to notify user about lost files (not just log this)!!
    files = get_all_files_from_db()
    if files:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        for f in files:
            if os.path.exists(f):
                # actual = get_actual_filename(f)
                actual = os.path.normpath(f).lower()
                if not actual:
                    actual = str(Path(f).resolve())  # TBD this is incorrect in case of symlinks
                if actual:
                    c.execute("UPDATE files SET filepath = ? WHERE filepath = ?", (actual,f))
            else:
                logging.warning('Tagged file doesn\'t exist, removing from database: '+f)
                c.execute("DELETE FROM files WHERE filepath = ?", (f,))  
        conn.commit()
        conn.close()

    # settings = load_settings(SETTINGS_FILE)
    # tags = get_all_tags_from_db()
    # if tags and settings['tags']:
    #     for t in tags:
    #         if t not in settings['tags']:
    #             delete_tag(t)
    # files = get_all_files_from_db()
    # if files:
    #     for f in files:
    #         get_tags(f) # this removes file from DB if it doesn't have tags
    
    # for t in settings['tags']:
    #     files = get_files_by_tag(t)
    #     if files:
    #         for f in files:
    #             if not Path(f).exists():
    #                 remove_all_tags(f)
    #                 logging.debug('Removed ' + str(f) + ' from tags table - file doesn\'t exist')
    #             else:
    #                 filename_tolower(f)
    #     else:
    #         delete_tag(t)

# def filename_tolower(filename): # TBD remove this in the future
#     filename = os.path.normpath(filename)
#     if filename != filename.lower():
#         tags = get_tags(filename, False)
#         tags_lower = get_tags(filename)
#         if tags:
#             if set(tags) != set(tags_lower):
#                 add_tags(filename.lower(), tags)
#                 remove_all_tags(filename)

def export_tags(dirname): #TBD revise this, add recursion
    try:
        if Path(dirname).is_dir():
            result = {}
            files = os.listdir(dirname)
            for f in files:
                fullname = os.path.join(dirname,f)
                tags = get_tags(fullname)
                if tags:
                    result[f] = tags
            json_file = os.path.join(dirname, str(Path(dirname).name) + '.json')
            with open(json_file, 'w') as jf:
                jsondump(result, jf, indent=4)
            return(str(json_file))
    except Exception as e:
        logging.exception(f'exception {e}')

def import_tags(dirname, tagsfile):
    if Path(dirname).is_dir():
        tags_imported = 0
        files_tagged = 0
        try:
            with open(tagsfile, 'r') as f:
                filetags = jsonload(f)
        except Exception as e:
            logging.exception(f'exception {e}')
            logging.error('Error on parsing the tag file')
            return
        if filetags:
            settings = load_settings(SETTINGS_FILE)            
            for k in filetags.keys():
                fullname = os.path.join(dirname, k)
                if Path(fullname).exists():
                    set_tags(fullname, filetags[k])
                    files_tagged+=1
                    if not set(filetags[k]).issubset(set(settings['tags'])):
                        tags = (t for t in filetags[k] if t not in settings['tags'])
                        for t in tags:
                            settings['tags'].append(t)
                            tags_imported+=1
        if tags_imported>0:
            save_settings(SETTINGS_FILE, settings)
        return "Files tagged: "+str(files_tagged)+", new tags imported: "+str(tags_imported)

    else:
        logging.error(str(dirname) + ' is not a valid folder')

def migrate_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("PRAGMA user_version")
    pragma = c.fetchone()[0]
    #logging.info("Database version:" + str(pragma))
    if (not pragma) or (pragma == 0):
        try:
            logging.info("Migration from 0 to 1")
            tags = load_settings(SETTINGS_FILE)['tags']
            db_tags = [f[0] for f in c.execute("SELECT name FROM tags")]
            logging.info("Adding missing tags from settings file")
            for t in [t for t in tags if t not in db_tags]:
                logging.info("Adding "+t)
                c.execute("INSERT INTO tags VALUES (null, ?)", (t,))
                #create_tag(t)

            settings = load_settings()
            settings['tags'] = []
            save_settings(SETTINGS_FILE, settings)

            c.execute("ALTER TABLE tags ADD COLUMN list_order INTEGER NOT NULL DEFAULT 1")        
            i=1
            for t in [f[0] for f in c.execute("SELECT name FROM tags")]:
                c.execute("UPDATE tags set list_order = ? WHERE name = ?", (i,t))
                i+=1
            #c.execute("DROP TABLE tags")
            #c.execute("CREATE TABLE tags (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE, list_order INTEGER NOT NULL UNIQUE)")

            c.execute("PRAGMA user_version = 1")
            logging.info("Database updated to version 1")
            pragma = 1
            # conn.commit()
        except Exception as e:
            logging.exception(e)

    if pragma == 1:
        try:
            logging.info("Migration from 1 to 2")
            logging.info("Adding color column")
            c.execute("ALTER TABLE tags ADD COLUMN color INTEGER")        
            # i=1
            # for t in [f[0] for f in c.execute("SELECT name FROM tags")]:
            #     c.execute("UPDATE tags set color = ? WHERE name = ?", (i,t))
            #     i+=1

            c.execute("PRAGMA user_version = 2")
            logging.info("Database updated to version 2")
            pragma = 2
        except Exception as e:
            logging.exception(e)
    
    if pragma == 2:
        try:
            logging.info("Migration from 2 to 3")
            logging.info("Adding groups table")
            c.execute("CREATE TABLE tag_groups (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE, list_order INTEGER NOT NULL, widget_type INTEGER NOT NULL DEFAULT 0, name_shown INTEGER DEFAULT 1)")
            c.execute("INSERT INTO tag_groups VALUES (1, 'Default', 1, 0, 0)")
            c.execute("ALTER TABLE tags ADD COLUMN group_id INTEGER NOT NULL DEFAULT 1")  
            for t in [f[0] for f in c.execute("SELECT id FROM tags")]:
                c.execute("UPDATE tags set group_id = 1 WHERE id = ?", (t,))
            c.execute("PRAGMA user_version = 3")
            logging.info("Database updated to version 3")
            pragma = 3
        except Exception as e:
            logging.exception(e)       

    conn.commit()
    conn.close()   

if not Path(APP_FOLDER).is_dir():
    Path(APP_FOLDER).mkdir()

if not Path(DB_FILE).exists():
    logging.info(r"Database doesn't exist, creating")
    try:
        init_db()
        migrate_db()        
    except Exception as e:
        logging.exception(e)
else:
    try:
        migrate_db()
    except Exception as e:
        logging.exception(e)

def get_actual_filename(name):
    dirs = name.split('\\')
    # disk letter
    test_name = [dirs[0].upper()]
    for d in dirs[1:]:
        test_name += ["%s[%s]" % (d[:-1], d[-1])]
    res = glob.glob('\\'.join(test_name))
    if not res:
        #File not found
        return os.path.normpath(Path(name).resolve()) # TBD this is a bit dangerous - will affect symlinks
    return os.path.normpath(res[0])

# def get_actual_filename2(path):
#     path = os.path.normpath(path).lower()
#     parts = path.split(os.sep)
#     result = parts[0].upper()
#     # check that root actually exists
#     if not os.path.exists(result):
#         return
#     for part in parts[1:]:
#         actual = next((item for item in os.listdir(result) if item.lower() == part), None)
#         if actual is None:
#             # path doesn't exist
#             return
#         result += os.sep + actual
#     return result


#migrate_to_db()

#remove_tag_global('trash')
#print(get_files_by_tag('trash'))

#print(get_files_affected_by_rule(get_rule_by_name('tttt')))
#apply_rule(get_rule_by_name('tttt'))

#filename_tolower(r'D:\DIM\WinFiles\Downloads\test.py')

# print(get_files_affected_by_rule(get_rule_by_name('Move tagged downloads to subfolder')))
#apply_rule(get_rule_by_name('Archive invoices'))
#pragma = migrate_db()
#print(bool(pragma))
#migrate_db()

# path = r"D:\Projects.other\Programming\DeClutter archive\test\test.txt"
# advanced_move(path,path)
check_files()   # TBD - remove this in the future?
# create_group('Rating')

# print(get_actual_filename2('d:\dim\winfiles\downloads\[free-scores.com]_field-john-nocturnes-8170.pdf'))

# p = Path('d:\dim\winfiles\downloads\[free-scores.com]_field-john-nocturnes-8170.pdf')
# print(p.resolve())
# print(Path(r'd:\dim\winfiles\downloads\test (0).txt').resolve())
# print(resolve_path('D:\dc_test\Projects\<group:Project>','D:\DIM\WinFiles\Downloads\EngUtiDbxug.jpg'))

# print(get_files_affected_by_rule(get_rule_by_name('Move to subfolder according to Store tag')))