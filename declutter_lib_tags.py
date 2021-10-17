import sqlite3, os, logging, datetime
from pathlib import Path

from declutter_lib import load_settings, save_settings, SETTINGS_FILE

TAGS_CACHE = {}
APP_FOLDER = os.path.join(os.getenv('APPDATA'), "DeClutter")
LOG_FILE = os.path.join(APP_FOLDER, "DeClutter.log")
DB_FILE = os.path.join(APP_FOLDER, "DeClutter.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE files (id INTEGER PRIMARY KEY, filepath VARCHAR NOT NULL UNIQUE)")
    c.execute("CREATE TABLE tags (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE, list_order INTEGER NOT NULL DEFAULT 1, color INTEGER, group_id INTEGER NOT NULL DEFAULT 1)")
    c.execute("CREATE TABLE file_tags (file_id INTEGER, tag_id INTEGER, timestamp INTEGER)")
    c.execute("CREATE TABLE tag_groups (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE, list_order INTEGER NOT NULL, widget_type INTEGER NOT NULL DEFAULT 0, name_shown INTEGER DEFAULT 1)")
    c.execute("INSERT INTO tag_groups VALUES (1, 'Default', 1, 0, 0)")

    # c.execute("CREATE TABLE tags (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE)")
    # c.execute("CREATE TABLE file_tags (file_id INTEGER, tag_id INTEGER)")
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
            c.execute("INSERT INTO file_tags VALUES (?,?,?)", (file_id,tag_id,datetime.datetime.now()))
            #print('inserting tags for {}, {}'.format(file_id,tag_id))
        conn.commit()
        conn.close()
        TAGS_CACHE[filename] = tags
        return True
    except Exception as e:
        logging.exception(e)
        return False

# set_tags('D:\dc_test\Projects\Seeds\seeds4.jpg',['Seeds'])

def get_tags(filename):
    filename = os.path.normpath(filename).lower()
    if filename in TAGS_CACHE.keys():
        return TAGS_CACHE[filename]
    #filename = filename.lower()
    #print(type(filename))
    # print('getting tags for ' + filename)
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
    TAGS_CACHE[filename] = tags
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

# removes specified tags from file
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
    if filename in TAGS_CACHE.keys():
        del TAGS_CACHE[filename]

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
    TAGS_CACHE[filename] = []

def clear_tags_cache():
    TAGS_CACHE = {}

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

def set_group_type(group, widget_type):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tag_groups SET widget_type = ? WHERE name = ?", (widget_type,group))
    conn.commit()
    conn.close()        

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

# def export_tags(dirname): #TBD revise this, add recursion
#     try:
#         if Path(dirname).is_dir():
#             result = {}
#             files = os.listdir(dirname)
#             for f in files:
#                 fullname = os.path.join(dirname,f)
#                 tags = get_tags(fullname)
#                 if tags:
#                     result[f] = tags
#             json_file = os.path.join(dirname, str(Path(dirname).name) + '.json')
#             with open(json_file, 'w') as jf:
#                 jsondump(result, jf, indent=4)
#             return(str(json_file))
#     except Exception as e:
#         logging.exception(f'exception {e}')

# def import_tags(dirname, tagsfile):
#     if Path(dirname).is_dir():
#         tags_imported = 0
#         files_tagged = 0
#         try:
#             with open(tagsfile, 'r') as f:
#                 filetags = jsonload(f)
#         except Exception as e:
#             logging.exception(f'exception {e}')
#             logging.error('Error on parsing the tag file')
#             return
#         if filetags:
#             settings = load_settings(SETTINGS_FILE)            
#             for k in filetags.keys():
#                 fullname = os.path.join(dirname, k)
#                 if Path(fullname).exists():
#                     set_tags(fullname, filetags[k])
#                     files_tagged+=1
#                     if not set(filetags[k]).issubset(set(settings['tags'])):
#                         tags = (t for t in filetags[k] if t not in settings['tags'])
#                         for t in tags:
#                             settings['tags'].append(t)
#                             tags_imported+=1
#         if tags_imported>0:
#             save_settings(SETTINGS_FILE, settings)
#         return "Files tagged: "+str(files_tagged)+", new tags imported: "+str(tags_imported)

#     else:
#         logging.error(str(dirname) + ' is not a valid folder')



    # def migrate_db():
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute("PRAGMA user_version")
#     pragma = c.fetchone()[0]
#     #logging.info("Database version:" + str(pragma))
#     if (not pragma) or (pragma == 0):
#         try:
#             logging.info("Migration from 0 to 1")
#             tags = load_settings(SETTINGS_FILE)['tags']
#             db_tags = [f[0] for f in c.execute("SELECT name FROM tags")]
#             logging.info("Adding missing tags from settings file")
#             for t in [t for t in tags if t not in db_tags]:
#                 logging.info("Adding "+t)
#                 c.execute("INSERT INTO tags VALUES (null, ?)", (t,))
#                 #create_tag(t)

#             settings = load_settings()
#             settings['tags'] = []
#             save_settings(SETTINGS_FILE, settings)

#             c.execute("ALTER TABLE tags ADD COLUMN list_order INTEGER NOT NULL DEFAULT 1")        
#             i=1
#             for t in [f[0] for f in c.execute("SELECT name FROM tags")]:
#                 c.execute("UPDATE tags set list_order = ? WHERE name = ?", (i,t))
#                 i+=1
#             #c.execute("DROP TABLE tags")
#             #c.execute("CREATE TABLE tags (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE, list_order INTEGER NOT NULL UNIQUE)")

#             c.execute("PRAGMA user_version = 1")
#             logging.info("Database updated to version 1")
#             pragma = 1
#             # conn.commit()
#         except Exception as e:
#             logging.exception(e)

#     if pragma == 1:
#         try:
#             logging.info("Migration from 1 to 2")
#             logging.info("Adding color column")
#             c.execute("ALTER TABLE tags ADD COLUMN color INTEGER")        
#             # i=1
#             # for t in [f[0] for f in c.execute("SELECT name FROM tags")]:
#             #     c.execute("UPDATE tags set color = ? WHERE name = ?", (i,t))
#             #     i+=1

#             c.execute("PRAGMA user_version = 2")
#             logging.info("Database updated to version 2")
#             pragma = 2
#         except Exception as e:
#             logging.exception(e)
    
#     if pragma == 2:
#         try:
#             logging.info("Migration from 2 to 3")
#             logging.info("Adding groups table")
#             c.execute("CREATE TABLE tag_groups (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE, list_order INTEGER NOT NULL, widget_type INTEGER NOT NULL DEFAULT 0, name_shown INTEGER DEFAULT 1)")
#             c.execute("INSERT INTO tag_groups VALUES (1, 'Default', 1, 0, 0)")
#             c.execute("ALTER TABLE tags ADD COLUMN group_id INTEGER NOT NULL DEFAULT 1")  
#             for t in [f[0] for f in c.execute("SELECT id FROM tags")]:
#                 c.execute("UPDATE tags set group_id = 1 WHERE id = ?", (t,))
#             c.execute("PRAGMA user_version = 3")
#             logging.info("Database updated to version 3")
#             pragma = 3
#         except Exception as e:
#             logging.exception(e)       

#     conn.commit()
#     conn.close()   

if not Path(DB_FILE).exists():
    logging.info(r"Database doesn't exist, creating")
    try:
        init_db()
        # migrate_db()        
    except Exception as e:
        logging.exception(e)

check_files() # TBD - remove this in the future?