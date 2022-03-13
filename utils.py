import os
import shutil

# Join paths but convert absolute path
# components to relative path components
def join_paths(*parts):
    return os.path.join(parts[0], *map(lambda x: x[1:] if x[0] == "/" else x, parts[1:]))

# Given a path to a file, first create all containing
# folders and then create the file
def create_open(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, "w")
    
def next_escaped(input, sep, escape=[]):
    assert(len(sep) == 1)
    res = ""
    input = input.strip()
    
    i = 0
    while i < len(input):
        if input[i] == "\\":
            i += 1
            
            if i >= len(input):
                raise ParsingException("Invalid backslash in plugin arguments")
            
            if input[i] not in [sep, "\\", *escape]:
                raise ParsingException("Invalid escape sequence in plugin arguments")
        elif input[i] == sep:
            return (res, input[i + 1:])
        
        res += input[i]
        i += 1
    
    return (res, "")
    
def create_copy(src, dst):
    if os.path.isfile(dst):
        return
    
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
