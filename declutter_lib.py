# Contains the core logic of DeClutter app
from json import (load as jsonload, dump as jsondump)
import os
import re
import glob
from time import time
from shutil import copy2, move, copytree, rmtree
from pathlib import Path
import logging
from fnmatch import fnmatch
from send2trash import send2trash
from declutter_lib_core import SETTINGS_FILE, APP_FOLDER, VERSION, load_settings, save_settings, get_file_type, get_file_time, convert_to_days, get_folder_size, get_size, get_rule_by_name, get_rule_by_id, advanced_copy, copy_file_or_dir, remove_file_or_dir, advanced_move
from declutter_lib_tags import move_group_to_group, move_tag, move_tag_to_tag, move_tag_to_group, get_all_tag_groups, get_tags_and_groups, TAGS_CACHE, init_db, tag_set_color, tag_get_color, create_group, create_tag, remove_all_tags, remove_tag, remove_tags, rename_group, rename_tag, set_group_type, set_tags, load_settings, save_settings, get_tags, get_all_tags_by_group_id, get_all_tags_by_group_id, get_tags_by_group_ids, add_tag, add_tags, clear_tags_cache, get_all_files_from_db, get_all_tags, get_tag_groups, get_files_by_tags, get_files_by_tag, delete_tag, delete_group, get_file_tags_by_group, check_files, user_data_dir

# import ctypes as _ctypes
# from ctypes.wintypes import HWND as _HWND, HANDLE as _HANDLE,DWORD as _DWORD,LPCWSTR as _LPCWSTR,MAX_PATH as _MAX_PATH
# from ctypes import create_unicode_buffer as _cub

# VERSION = '1.12.1'
# APP_FOLDER = os.path.join(os.getenv('APPDATA'), "DeClutter")
LOG_FILE = os.path.join(APP_FOLDER, "DeClutter.log")
DB_FILE = os.path.join(APP_FOLDER, "DeClutter.db")
# SETTINGS_FILE = os.path.join(APP_FOLDER, "settings.json")
ALL_TAGGED_TEXT = 'All tagged files and folders'

logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler(filename=LOG_FILE, encoding='utf-8', mode='a+')],
                    format="%(asctime)-15s %(levelname)-8s %(message)s")


def apply_rule(rule, dryrun=False):
    report = {'copied': 0, 'moved': 0, 'moved to subfolder': 0, 'deleted': 0,
              'trashed': 0, 'tagged': 0, 'untagged': 0, 'cleared tags': 0, 'renamed': 0}
    details = []
    if rule['enabled']:
        files = get_files_affected_by_rule(rule)
        if files:
            logging.debug(
                "Processing rule" + (" [DRYRUN mode]" if dryrun else "") + ": " + rule['name'])
            for f in files:
                msg = ""
                p = Path(f)
                if rule['action'] == 'Copy':
                    target_folder = resolve_path(rule['target_folder'], p)
                    target = Path(target_folder) / str(p).replace(':', '') if ('keep_folder_structure' in rule.keys(
                    ) and rule['keep_folder_structure']) else Path(target_folder) / p.name
                    try:
                        if p.is_dir():
                            if target.is_dir():
                                # TBD replaces only if size differs
                                if get_size(target) != get_size(f):
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
                                    # TBD will probably crash if target exists!
                                    result = copytree(f, target)
                                    # hide_dc(result) # TBD only for sidecar files
                                msg = "Copied " + f + " to " + str(result)
                                report['copied'] += 1
                        else:
                            if target.is_file() and os.stat(target).st_size == os.stat(f).st_size:  # TBD comparing sizes may be not enough
                                msg = "File " + f + " already exists in the target location and has the same size, skipping"
                                # result = target
                            else:
                                if not dryrun:
                                    # if not Path(target.parent).is_dir():
                                    #     os.makedirs(target.parent)
                                    # result = copy2(f, target)
                                    result = advanced_copy(
                                        f, target, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                                else:
                                    msg = "Copied " + f + " to " + str(result)
                                if result:
                                    report['copied'] += 1
                                    msg = "Copied " + f + " to " + str(result)
                        if rule['keep_tags']:
                            tags = get_tags(f)
                            if set_tags(result, tags):
                                # logging.info("Copied tags for " + f)
                                msg += ", tags copied too"
                            else:
                                msg += ", tags not copied"
                                # logging.info("not copying tags for " + f)
                    except Exception as e:
                        logging.exception(f'exception {e}')
                elif rule['action'] == 'Move':
                    if not dryrun:
                        tags = get_tags(f)
                        target_folder = resolve_path(rule['target_folder'], p)
                        # print(p)
                        # print(target_folder)
                        target = Path(target_folder) / str(p).replace(':', '') if ('keep_folder_structure' in rule.keys(
                        ) and rule['keep_folder_structure']) else Path(target_folder) / p.name
                        try:
                            # if not Path(target.parent).is_dir():
                            #     os.makedirs(target.parent)
                            # result = move(f, target)
                            result = advanced_move(
                                f, target, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                            if result:
                                msg = "Moved " + f + " to " + str(result)
                                report['moved'] += 1
                                remove_all_tags(f)
                                # TBD implement removing tags if keep_tags == False
                                if rule['keep_tags'] and tags:
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
                        newname = rule['name_pattern'].replace(
                            '<filename>', p.name)
                        newname = newname.replace('<folder>', p.parent.name)
                        # TBD what if there are multiple replace tokens?
                        rep = re.findall("<replace:(.*):(.*)>", newname)
                        newname = re.sub("<replace(.*?)>", '', newname)
                        # print(rep)
                        for r in rep:
                            newname = newname.replace(r[0], r[1])
                        # print(newname)
                        if not dryrun:
                            try:
                                # os.chdir(p.parent)
                                # os.rename(p.name, newname) #TBD what if file exists?
                                # print('renaming ' + str(p) + ' to ' + str(Path(p.parent) / newname))
                                result = advanced_move(p, Path(
                                    p.parent) / newname, (rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                                if result:
                                    newfullname = Path(p.parent / newname)
                                    if newfullname.is_dir():  # if renamed a folder check if its children are in the list, and if they are update their paths
                                        for i in range(len(files)):
                                            if p in Path(files[i]).parents:
                                                files[i] = files[i].replace(
                                                    str(p), str(newfullname))
                                    # tf = get_tag_file_path(f) # TBD bring this back for sidecar files
                                    # if tf.is_file():
                                    #     os.chdir(tf.parent)
                                    #     os.rename(tf.name, newname + '.json')
                                    tags = get_tags(f)
                                    if tags:
                                        remove_all_tags(f)
                                        set_tags(newfullname, tags)
                                    report['renamed'] += 1
                                    msg = 'Renamed ' + f + ' to ' + str(result)
                            except Exception as e:
                                logging.exception(e)
                        else:
                            msg = 'Renamed ' + f + ' to ' + newname
                    else:
                        msg = 'Error: name pattern is missing for rule ' + \
                            rule['name']
                        logging.error(
                            "Name pattern is missing for rule " + rule['name'])
                elif rule['action'] == 'Move to subfolder':
                    # print('here')
                    tags = get_tags(f)
                    target_subfolder = resolve_path(
                        rule['target_subfolder'], p)
                    # print(f,tags,target_subfolder)
                    if p.parent.name != target_subfolder:  # check if we're not already in the subfolder
                        # target = Path(rule['target_subfolder']) / p.name
                        if not dryrun:
                            result = advanced_move(f, p.parent / Path(target_subfolder) / p.name, (
                                rule['overwrite_switch'] == 'overwrite') if 'overwrite_switch' in rule.keys() else False)
                            if result:
                                remove_all_tags(f)
                                report['moved to subfolder'] += 1
                                msg = "Moved " + f + " to subfolder: " + \
                                    str(target_subfolder)

                                # TBD implement removing tags if keep_tags == False
                                if rule['keep_tags'] and tags:
                                    set_tags(result, tags)
                                    msg += ", with tags"
                            # print("going to copy" + f + " to " + rule['target_folder'])
                        else:
                            msg = "Moved " + f + " to subfolder: " + \
                                str(target_subfolder)
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
                    # if not dryrun:
                    if rule['tags'] and not set(rule['tags']).issubset(set(get_tags(f))):
                        add_tags(f, rule['tags'])
                        msg = "Tagged " + f + " with " + str(rule['tags'])
                        report['tagged'] += 1
                elif rule['action'] == 'Remove tags':
                    # if not dryrun:
                    if rule['tags'] and set(rule['tags']).issubset(set(get_tags(f))):
                        remove_tags(f, rule['tags'])
                        msg = "Removed these tags from  " + \
                            f + ": " + str(rule['tags'])
                        report['untagged'] += 1
                elif rule['action'] == 'Clear all tags':
                    # if not dryrun:
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
        group_tags = get_file_tags_by_group(r[1], path)
        # print(group_tags)
        final_path = final_path.replace(
            r[0], group_tags[0] if group_tags else 'None')

    return final_path


def apply_all_rules(settings):
    report = {}
    details = []
    for rule in settings['rules']:
        # TBD vN doesn't look optimal / had to use load_settings for testing, should be just settings
        rule_report, rule_details = apply_rule(rule, load_settings()['dryrun'])
        # print(rule_report)
        report = {k: report.get(k, 0) + rule_report.get(k, 0)
                  for k in set(report) | set(rule_report)}
        details.extend(rule_details)
    return report, details

def get_files_affected_by_rule(rule, allow_empty_conditions=False):
    if (not 'conditions' in rule.keys() or not rule['conditions']) and not allow_empty_conditions:
        return ([])
    found = []
    for f in rule['folders']:
        if Path(f).is_dir() or f == ALL_TAGGED_TEXT:
            found.extend(get_files_affected_by_rule_folder(rule, f, []))
        else:
            logging.error('Folder ' + f + ' in rule ' +
                          rule['name'] + ' doesn\'t exist, skipping')
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
            sorted_files = {k: v for k, v in sorted(
                unsorted_files.items(), key=lambda item: -item[1])}
            target_list = list(sorted_files)[int(rule['ignore_N']):]
            result.extend(target_list)

        return result
    else:
        return sorted(list(set(found)))  # returning only unique results
    # return found


def get_files_affected_by_rule_folder(rule, dirname, files_found=[]):
    check_files()  # this is required to clean up the missing or incorrect file paths, TBD optimize this
    files = [get_actual_filename(f) for f in get_all_files_from_db()] if dirname == ALL_TAGGED_TEXT else os.listdir(
        dirname)  # TBD not sure if we need get_actual_filename() here
    out_files = files_found
    for f in files:
        if f != '.dc':  # ignoring .dc folder TBD can be removed for now and brough back for sidecar files
            fullname = os.path.join(dirname, f)
            if rule['action'] == 'Move to subfolder' and ((Path(fullname).parent).name == rule['target_subfolder'] or (Path(fullname).is_dir() and f == rule['target_subfolder'])):
                conditions_met = False
            else:
                conditions_met = False if rule['condition_switch'] == 'any' else True
                conditions_met = True if rule['action'] == 'Filter' and rule['conditions'] == [
                ] else conditions_met  # return all files in tagger when no filters are added
                for c in rule['conditions']:
                    condition_met = False
                    if c['type'] == 'tags':
                        # print(fullname)
                        tags = get_tags(fullname)
                        # print(tags)
                        common_tags = [
                            value for value in tags if value in c['tags']]
                        # print(common_tags)
                        if c['tag_switch'] == 'any':
                            # or better bool(common_tags)?
                            condition_met = len(common_tags) > 0
                        elif c['tag_switch'] == 'all':
                            # print(tags,common_tags)
                            condition_met = set(common_tags) == set(
                                c['tags']) and tags  # tags must be not empty
                            # print(condition_met)
                        elif c['tag_switch'] == 'none':
                            condition_met = common_tags == []
                        elif c['tag_switch'] == 'no tags':
                            condition_met = tags == []
                        elif c['tag_switch'] == 'any tags':
                            condition_met = len(tags) > 0
                        elif c['tag_switch'] == 'tags in group':
                            # print(get_tag_groups(fullname))
                            condition_met = c['tag_group'] in get_tag_groups(
                                fullname)
                        # if condition_met:
                        #     print(fullname,tags,common_tags,c['tag_switch'])
                    elif c['type'] == 'date':
                        try:
                            settings = load_settings(SETTINGS_FILE)
                            if c['age_switch'] == '>=':
                                if (float(time()) - get_file_time(fullname, settings['date_type']))/(3600*24) >= convert_to_days(float(c['age']), c['age_units']):
                                    condition_met = True
                            elif c['age_switch'] == '<':
                                if (float(time()) - get_file_time(fullname, settings['date_type']))/(3600*24) < convert_to_days(float(c['age']), c['age_units']):
                                    condition_met = True
                        except Exception as e:
                            logging.exception(e)
                    # elif c['type'] == 'newest N' and os.path.isfile(fullname): # TBD delete this!
                    #     condition_met = True
                    elif c['type'] == 'size' and os.path.isfile(fullname):
                        factor = {'B': 1, 'KB': 1024 ** 1, 'MB': 1024 **
                                  2, 'GB': 1024 ** 3, 'TB': 1024 ** 4}
                        fsize = os.stat(fullname).st_size
                        target_size = float(c['size']) * \
                            factor[c['size_units']]
                        if c['size_switch'] == '>=':
                            condition_met = fsize >= target_size
                        elif c['size_switch'] == '<':
                            condition_met = fsize < target_size
                    elif c['type'] == 'name':
                        if not 'name_switch' in c.keys():  # TBD this is temporary to support old conditions that don't have this switch yet
                            c['name_switch'] = 'matches'
                        # TBD need to reflect this in help - it works like this: 'matches any' or 'doesn't match all'
                        for m in c['filemask'].split(','):
                            condition_met = condition_met or fnmatch(
                                f, m.strip())
                            if condition_met:
                                break
                        condition_met = condition_met == (
                            c['name_switch'] == 'matches')
                    elif c['type'] == 'type' and os.path.isfile(fullname):
                        condition_met = (get_file_type(fullname) == c['file_type']) == (
                            c['file_type_switch'] == 'is')

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

            # print(fullname)
            # print(conditions_met)
            if conditions_met:
                out_files.append(os.path.normpath(fullname))

            # Important: it recurses for 'Rename' and 'Tag' actions, but doesn't recurse for other actions if the folder matches the conditions
            # That's because the whole folder will be copied/moved/trashed and it doesn't make sense to check its files
            if (rule['action'] in ('Rename', 'Tag', 'Remove tags', 'Clear all tags') or not conditions_met) and os.path.isdir(fullname) and rule['recursive']:
                # if not conditions_met and os.path.isdir(fullname) and rule['recursive']:
                get_files_affected_by_rule_folder(rule, fullname, out_files)
    return out_files


def get_nonexistent_path(src, dst):
    if not os.path.exists(dst):  # based on how we call it we should never get here
        return dst
    filename, file_extension = os.path.splitext(dst)
    match = re.findall(r"^(.+)\s\((\d+)\)$", filename)
    i = 1
    if match:  # filename already has (i) in it
        filename = match[0][0]
        i = int(match[0][1])+1

    new_fname = "{} ({}){}".format(filename, i, file_extension)
    while os.path.exists(new_fname):
        if get_size(src) == get_size(new_fname):
            return False
        i += 1
        new_fname = "{} ({}){}".format(filename, i, file_extension)
    return new_fname

# else:
#     try:
#         migrate_db()
#     except Exception as e:
#         logging.exception(e)


def get_actual_filename(name):
    dirs = name.split('\\')
    # disk letter
    test_name = [dirs[0].upper()]
    for d in dirs[1:]:
        test_name += ["%s[%s]" % (d[:-1], d[-1])]
    res = ""
    try:
        res = glob.glob('\\'.join(test_name))
    except Exception as e:
        logging.exception(e)
    if not res:
        # File not found
        # TBD this is a bit dangerous - will affect symlinks
        return os.path.normpath(Path(name).resolve())
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

# def get_startup_shortcut_path():
#     _SHGetFolderPath = _ctypes.windll.shell32.SHGetFolderPathW
#     _SHGetFolderPath.argtypes = [_HWND, _ctypes.c_int, _HANDLE, _DWORD, _LPCWSTR]
#     auPathBuffer = _cub(_MAX_PATH)
#     exit_code=_SHGetFolderPath(0, 24, 0, 0, auPathBuffer) # 24 is the code for Startup folder for All Users
#     # print(auPathBuffer.value)

#     # pythoncom.CoInitialize() # remove the '#' at the beginning of the line if running in a thread.
#     return os.path.join(auPathBuffer.value, 'DeClutter.lnk')


# check_files()
# init_db()
