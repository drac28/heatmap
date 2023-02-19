import os
import re

def input_int(text):
    while True:
        try:
            in_int = int(input(text))
            break
        except KeyboardInterrupt:
            break
        except:
            pass
    return in_int

def mkdir(path):
    if not os.path.exists(path+"/output"):
        os.mkdir(path+"/output")
    if not os.path.exists(path+"/working"):
        os.mkdir(path+"/working")
    

def name_len(file):
    basename = os.path.splitext(os.path.basename(file))[0]
    name = ""
    for char in basename:
        try:
            int(char)
            name += char
        except:
            print(name)
            return len(name)
    return len(name)

def fill_to_max(file, max_len):
    if name_len(file) == 0:
        return file
    while name_len(file) < max_len:
        file = "0"+file
    return file

def rename_folder(folder):
    files = os.listdir()
    if len(files) < 10:
        max_len = 1
    elif len(files) < 100:
        max_len = 2
    elif len(files) < 1000:
        max_len = 3
    else:
        max_len = 0

    for file in files:
        new_name = fill_to_max(file, max_len)
        os.rename(file, new_name)

def folder_start(folder, basefolder):
    value = os.listdir()
    files = []
    folders = []
    for file in value:
        if os.path.isdir(folder+"/"+file):
            folders.append(file)
        else:
            files.append(file)

    rename_folder(folder)

    for folder in folders:
        os.chdir(folder)
        rename_folder(folder)
        os.chdir("..")

def rename(folder):
    os.chdir(folder)
    folder_start(folder, folder)

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)
    return l

def remove(path):
    files = os.listdir(path)
    for file in files:
        try:
            for file1 in os.listdir(path+"/"+file):
                os.remove(path+"/"+file+"/"+file1)
            os.rmdir(path+"/"+file)
        except:
            os.remove(path+"/"+file)
    os.rmdir(path)