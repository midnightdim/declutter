import re
from fnmatch import fnmatch
import logging
import os
from pathlib import Path
from shutil import copytree, rmtree
from time import time
from send2trash import send2trash
from declutter.tags import add_tags, remove_tags
from declutter.config import ALL_TAGGED_TEXT
from declutter.store import load_settings
from declutter.file_utils import (get_file_time, convert_to_days, get_size, advanced_copy,
                         advanced_move, get_file_type, get_actual_filename)
from declutter.tags import (get_tags, set_tags, remove_all_tags, get_file_tags_by_group, get_tag_groups, 
                   check_files, get_all_files_from_db)

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
                                if not dryrun:
                                    # TBD will probably crash if target exists!
                                    result = copytree(f, target)
                                    # hide_dc(result) # TBD only for sidecar files
                                msg = "Copied " + f + " to " + str(result)
                                report['copied'] += 1
                        else:
                            if target.is_file() and os.stat(target).st_size == os.stat(f).st_size:  # TBD comparing sizes may be not enough
                                msg = "File " + f + " already exists in the target location and has the same size, skipping"
                            else:
                                if not dryrun:
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
                                msg += ", tags copied too"
                            else:
                                msg += ", tags not copied"
                    except Exception as e:
                        logging.exception(f'exception {e}')
                elif rule['action'] == 'Move':
                    if not dryrun:
                        tags = get_tags(f)
                        target_folder = resolve_path(rule['target_folder'], p)
                        target = Path(target_folder) / str(p).replace(':', '') if ('keep_folder_structure' in rule.keys(
                        ) and rule['keep_folder_structure']) else Path(target_folder) / p.name
                        try:
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
                        for r in rep:
                            newname = newname.replace(r[0], r[1])
                        if not dryrun:
                            try:
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
                    tags = get_tags(f)
                    target_subfolder = resolve_path(
                        rule['target_subfolder'], p)
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
                    if not dryrun:
                        if rule['tags'] and not set(rule['tags']).issubset(set(get_tags(f))):
                            add_tags(f, rule['tags'])
                            msg = "Tagged " + f + " with " + str(rule['tags'])
                            report['tagged'] += 1
                elif rule['action'] == 'Remove tags':
                    if not dryrun:                    
                    # Remove only the tags that exist on the file
                        if rule['tags']:
                            current_tags = set(get_tags(f))
                            tags_to_remove = list(current_tags.intersection(rule['tags']))
                            if tags_to_remove:
                                remove_tags(f, tags_to_remove)
                                msg = f"Removed these tags from {f}: {tags_to_remove}"
                                report['untagged'] += 1
                elif rule['action'] == 'Clear all tags':
                    if not dryrun:
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
        final_path = final_path.replace(
            r[0], group_tags[0] if group_tags else 'None')

    return final_path


def apply_all_rules(settings):
    report = {}
    details = []
    for rule in settings['rules']:
        # TBD doesn't look optimal / had to use load_settings for testing, should be just settings
        rule_report, rule_details = apply_rule(rule, load_settings()['dryrun'])
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



def get_files_affected_by_rule_folder(rule, dirname, files_found=None):
    check_files()  # this is required to clean up the missing or incorrect file paths, TBD optimize this
    files = [get_actual_filename(f) for f in get_all_files_from_db()] if dirname == ALL_TAGGED_TEXT else os.listdir(
        dirname)  # TBD not sure if we need get_actual_filename() here
    out_files = files_found if files_found is not None else []
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
                        tags = get_tags(fullname)
                        common_tags = [
                            value for value in tags if value in c['tags']]
                        if c['tag_switch'] == 'any':
                            # TBD or better bool(common_tags)?
                            condition_met = len(common_tags) > 0
                        elif c['tag_switch'] == 'all':
                            condition_met = set(common_tags) == set(
                                c['tags']) and tags  # tags must be not empty
                        elif c['tag_switch'] == 'none':
                            condition_met = common_tags == []
                        elif c['tag_switch'] == 'no tags':
                            condition_met = tags == []
                        elif c['tag_switch'] == 'any tags':
                            condition_met = len(tags) > 0
                        elif c['tag_switch'] == 'tags in group':
                            condition_met = c['tag_group'] in get_tag_groups(
                                fullname)

                    elif c['type'] == 'date':
                        try:
                            settings = load_settings()
                            if c['age_switch'] == '>=':
                                if (float(time()) - get_file_time(fullname, settings['date_type']))/(3600*24) >= convert_to_days(float(c['age']), c['age_units']):
                                    condition_met = True
                            elif c['age_switch'] == '<':
                                if (float(time()) - get_file_time(fullname, settings['date_type']))/(3600*24) < convert_to_days(float(c['age']), c['age_units']):
                                    condition_met = True
                        except Exception as e:
                            logging.exception(e)
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

            if conditions_met:
                out_files.append(os.path.normpath(fullname))

            # Important: it recurses for 'Rename' and 'Tag' actions, but doesn't recurse for other actions if the folder matches the conditions
            # That's because the whole folder will be copied/moved/trashed and it doesn't make sense to check its files
            if (rule['action'] in ('Rename', 'Tag', 'Remove tags', 'Clear all tags') or not conditions_met) and os.path.isdir(fullname) and rule['recursive']:
                # if not conditions_met and os.path.isdir(fullname) and rule['recursive']:
                get_files_affected_by_rule_folder(rule, fullname, out_files)
    return out_files

def get_rule_by_name(name):
    settings = load_settings()
    for r in settings['rules']:
        if r['name'] == name:
            return r

def get_rule_by_id(rule_id, rules=[]):
    if not rules:
        rules = load_settings()['rules']
    for r in rules:
        if int(r['id']) == rule_id:
            return r
