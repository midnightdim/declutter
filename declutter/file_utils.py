import glob
import os
import re
from shutil import copy2, copytree, move, rmtree
from pathlib import Path
from fnmatch import fnmatch
from .config import load_settings
import logging

def get_file_time(filename, date_type=0):
    if Path(filename).exists():
        if date_type == 0:  # earliest of modified & created
            return min(os.path.getmtime(filename), os.path.getctime(filename))
        elif date_type == 1:  # modified
            return os.path.getmtime(filename)
        elif date_type == 2:  # created
            return os.path.getctime(filename)
        elif date_type == 3:  # latest of modified & created
            return max(os.path.getmtime(filename), os.path.getctime(filename))
        elif date_type == 4:  # last access
            return os.path.getatime(filename)
    else:
        logging.error('File not found: ' + filename)

def convert_to_days(value, units):
    if units == 'days':
        return value
    elif units == 'weeks':
        return value * 7
    elif units == 'months':
        return value * 30.43  # TBD vN this is a bit rough
    elif units == 'years':
        return value * 365.25  # TBD vN this is a bit rough

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
        # print(os.path.getsize(filepath))
        return os.path.getsize(filepath)
    else:
        return 0  # TBD maybe return an error?
    
def get_file_type(path):
    settings = load_settings()
    for ft in settings['file_types']:
        for p in settings['file_types'][ft].split(','):
            if fnmatch(path, p.strip()):
                return ft
    return 'Other'

def advanced_copy(source_path, target_path, overwrite=False):
    return advanced_move(source_path, target_path, overwrite, True)


def copy_file_or_dir(source_path, target_path):
    if Path(source_path).is_file():
        res = copy2(source_path, target_path)
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


# copy = False means move = TBD improve this
def advanced_move(source_path, target_path, overwrite=False, copy=False):
    # print('advanced move')
    # print(source_path)
    # print(target_path)
    # print(overwrite)
    # print(copy)
    if not os.path.exists(source_path):
        return False
    if not os.path.exists(target_path):
        # p Target path doesnt exist, simply moving/copying
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
        # print('sps ' + str(get_size(source_path)))
        # print('tps ' + str(get_size(target_path)))
        # file/folder with the same size exists
        if get_size(source_path) == get_size(target_path):
            # print('its file/dir with the same size, skipping')
            # remove_file_or_dir(source_path)
            if not copy:
                # if we're moving the file/folder and it's already there just delete the source file/folder
                remove_file_or_dir(source_path)
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
