# DeClutter

DeClutter is a desktop application built on PySide6. 
It has 2 main features:
- automated files processing based on rules
- tagger: a simple file manager that allows tagging files and folders with user defined tags

DeClutter doesn't magically clean up your file mess, but it provides a set of tools that can be incorporated into your file management and archiving policies.

Some common use cases are:
1. automated deletion of old files in Downloads folder
1. quick navigation by tags - it's much more intuitive than navigation by folder tree because we don't normally think in tree structures
1. you can organize files in your "Downloads" folder by automatically moving them to subfolders based on their type, date, etc.
1. you can set the "expiration time" for files (using tags) and DeClutter will delete them automatically when they expire
1. if you work on a project in a system that saves new versions with incremental numbers (like FL Studio or Reaper) you can automatically move older versions of project files to a subfolder, keeping only N recent versions 

The main window allows you to manage rules and open the tagger.
Each rule consists of:
- sources: which folders should be processed (you can also run rules across all tagged files)
- conditions: allows you to filter out files and folders based on file name mask, size, date, tags and type
- action: defines what DeClutter will do with the files that fall under the conditions - you can delete, trash, copy, move, rename, tag files (and more!)

Tagger is a simple file browser where you can:
- tag files
- view all tagged files
- filter files (using the same mechanism as rule conditions)
- preview media files
There are also tag groups and you can setup a group so that only one tag from this group can be applied to a file. This is useful when you want to define a "parameter" that can have only one value - for example, file rating, file expiration time, etc.

Tagger supports files drag-n-drop with Windows Explorer and between tagger windows (if you drag _from_ a tagger window this also preserves tags):
- if you drag to Windows Explorer you can use Shift key to move the file (by default it's going to be copied)
- if you drag to another tagger window you can use Ctrl key to copy the file (by default it's going to be moved)

DeClutter is primarily tested on Windows. It runs on MacOS, but hasn't been fully ported yet.
