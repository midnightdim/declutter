import json
import os
import logging
from shutil import copy2, move, copytree, rmtree
from pathlib import Path
import subprocess

def remove_all_tags_in_folder(dirname):
    for f in next(os.walk(dirname))[1]:
        fullname = os.path.join(dirname,f)    
        if f == '.dc':
            try:
                rmtree(fullname)
            except Exception as e:
                logging.exception(e)
        else:
            remove_all_tags_in_folder(fullname)

def get_files_by_tag_sc(dirname, tag, files_found = [], recursive = True):
    files = files_found
    tag_folder = os.path.join(dirname, ".dc")
    if os.path.isdir(tag_folder):
        tag_files = next(os.walk(tag_folder))[2]
        for f in tag_files:
            fullname = os.path.join(tag_folder, f)
            filename = os.path.join(dirname,f[:-5])
            if os.path.isfile(filename) or os.path.isdir(filename):
                try:
                    with open(str(fullname)) as json_file:
                        data = json.load(json_file)
                        if tag in data['tags']:
                            files.append(filename)
                except Exception as e:
                    logging.exception(f'exception {e}')
                    logging.warning("Removing tag file cause it seems to be corrupt: " + fullname) # TBD this doesn't look very safe
                    os.remove(fullname)
            else:
                logging.warning("Deleting this tag file since no corresponding file was found: " + fullname)
                os.remove(fullname)
    if recursive:
        for d in next(os.walk(dirname))[1]:
            if d != ".dc": # ignoring tag folders
                fullname = os.path.join(dirname,d)
                #print(fullname)
                get_files_by_tag_sc(fullname, tag, files, recursive)
    return files

def get_tag_file_path(f):
    p = Path(f)
    return Path(p.parent) / ".dc" / (str(p.name) + ".json")

def get_tags_sc(filename):
    try:  # TBD this fails silently in some cases, maybe we should notify user
        if Path(filename).exists():
            if not get_tag_file_path(filename).is_file():
                return []
            else:
                with open(get_tag_file_path(filename), 'r') as f:
                    t = json.load(f)['tags']
                    return t if t else []
        else:
            logging.error('File not found: ' + filename)                  
            return []
    except Exception as e:
        logging.exception(e)
        return []  

def add_tags_sc(filename, tags): # returns false if file already has these tags
    if Path(filename).exists():
        if set(tags).issubset(get_tags_sc(filename)):
            return False
        else:
            set_tags_sc(filename, list(set(tags+get_tags_sc(filename))))
            return True
    else:
        logging.error('File not found: ' + filename)
        return False  # TBD vN maybe should return something else

def add_tag_sc(filename, tag):
    return add_tags_sc(filename, [tag])

def remove_tags_sc(filename, tags): #TBD this is extremely inefficient!
    for t in tags:
        remove_tag_sc(filename, t)

def remove_tag_sc(filename, tag): # TBD upgrade this
    if Path(filename).exists():
        cur_tags = get_tags_sc(filename)
        if tag in cur_tags:
            cur_tags.remove(tag)
        # print("## remove_tag ## cur_tags: " + str(cur_tags))    
        set_tags_sc(filename, cur_tags) 
    else:
        logging.error('File not found: ' + filename)        

def set_tags_sc(filename, tags):
    if Path(filename).is_file() or Path(filename).is_dir():
        if set(get_tags_sc(filename)) != set(tags):
            tag_folder = os.path.join(os.path.dirname(filename), ".dc")
            if not os.path.isdir(tag_folder):
                try:
                    logging.info("Creating folder: " + tag_folder)
                    os.mkdir(tag_folder)
                    subprocess.check_call(["attrib", "+H", tag_folder])
                except Exception as e:
                    logging.exception(f'exception {e}')
            tagfile = get_tag_file_path(filename)
            if tagfile.is_file():
                subprocess.check_call(["attrib", "-H", tagfile])
            try:
                with open(tagfile, 'w+') as f:   # had to use w+ instead of w because of restrictions with hidden files
                    output = {'tags': tags}
                    json.dump(output, f)
                subprocess.check_call(["attrib", "+H", tagfile])
                return True
            except Exception as e:
                logging.exception(f'exception {e}')
                return False
        else:
            return False
    else:
        logging.error('File not found: ' + filename)
        return False

def hide_dc(dirname):
    for f in os.listdir(dirname):
        fullname = os.path.join(dirname, f)
        if os.path.isdir(fullname):
            if f == ".dc":
                subprocess.check_call(["attrib", "+H", fullname])
                hide_files(fullname)
            else:
                hide_dc(fullname)

def hide_files(dirname):
    for f in os.listdir(dirname):
        subprocess.check_call(["attrib", "+H", os.path.join(dirname, f)])