import hashlib
import glob
import os
import re
from shutil import copy2, copytree, move, rmtree
from pathlib import Path
from fnmatch import fnmatch
from typing import Optional
from declutter.store import load_settings
import logging

# ---------- Hashing utilities ----------

CHUNK_SIZE = 128 * 1024  # 128KB

def quick_file_fingerprint(path: str) -> Optional[str]:
    """
    Fast, reasonably distinctive fingerprint using stdlib:
    - Hash file size and small samples from head and tail to avoid full reads for large files.
    Falls back to hashing the first CHUNK_SIZE if file is too small to have tail.
    """
    try:
        p = Path(path)
        if not p.is_file():
            return None
        size = p.stat().st_size

        h = hashlib.blake2b(digest_size=16)
        h.update(size.to_bytes(8, 'little'))

        with p.open('rb') as f:
            head = f.read(CHUNK_SIZE)
            h.update(head)
            if size > CHUNK_SIZE * 2:
                # read tail
                f.seek(max(size - CHUNK_SIZE, 0))
                tail = f.read(CHUNK_SIZE)
                h.update(tail)
        return h.hexdigest()
    except Exception as e:
        logging.exception(f"Failed to hash file {path}: {e}")
        return None

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
        return value * 30.43  # TBD implement a better conversion
    elif units == 'years':
        return value * 365.25  # TBD same here

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
        return os.path.getsize(filepath)
    else:
        return 0  # TBD add error handling
    
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


def advanced_move(source_path, target_path, overwrite=False, copy=False):
    """Moves or copies a file/directory from source_path to target_path with overwrite options."""
    if not os.path.exists(source_path):
        return False

    # Early-out: if source and target are the same file, skip
    try:
        if os.path.samefile(source_path, target_path):
            return target_path
    except Exception:
        if os.path.abspath(source_path) == os.path.abspath(target_path):
            return target_path

    if not os.path.exists(target_path):
        # Target path doesn't exist — normal move/copy
        try:
            if not Path(target_path).parent.exists():
                os.makedirs(Path(target_path).parent)
            if copy:
                return copy_file_or_dir(source_path, target_path)
            else:
                return move(source_path, target_path)
        except Exception as e:
            logging.exception(e)
            return False
    else:
        # Target exists — check size
        if get_size(source_path) == get_size(target_path):
            # Optional hash comparison to confirm identical content
            try:
                settings = load_settings()
                use_hash = settings.get('use_hash_on_conflict', False)
            except Exception:
                use_hash = False

            same_content = False
            if use_hash and Path(source_path).is_file() and Path(target_path).is_file():
                same_content = (
                    quick_file_fingerprint(source_path)
                    == quick_file_fingerprint(target_path)
                )
            else:
                # If hash check is off, assume identical if size matches
                same_content = True

            if same_content:
                if not copy:
                    remove_file_or_dir(source_path)
                return target_path
            else:
                # Sizes match but content differs — increment or overwrite
                if overwrite:
                    try:
                        remove_file_or_dir(target_path)
                        if copy:
                            return copy_file_or_dir(source_path, target_path)
                        else:
                            return move(source_path, target_path)
                    except Exception as e:
                        logging.exception(e)
                        return False
                else:
                    new_name = get_nonexistent_path(source_path, target_path)
                    if new_name:
                        try:
                            if copy:
                                return copy_file_or_dir(source_path, new_name)
                            else:
                                return move(source_path, new_name)
                        except Exception as e:
                            logging.exception(e)
                            return False
                    else:
                        return False
        else:
            # Different size — overwrite or increment
            if overwrite:
                try:
                    remove_file_or_dir(target_path)
                    if copy:
                        return copy_file_or_dir(source_path, target_path)
                    else:
                        return move(source_path, target_path)
                except Exception as e:
                    logging.exception(e)
                    return False
            else:
                new_name = get_nonexistent_path(source_path, target_path)
                if new_name:
                    try:
                        if copy:
                            return copy_file_or_dir(source_path, new_name)
                        else:
                            return move(source_path, new_name)
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
