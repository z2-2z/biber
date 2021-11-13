import sys
import os
import importlib

from . import parse_post
from . import parse_config
from . import create_dirs
from . import create_index
from . import create_post

class BiberError(Exception):
    pass

def load_plugins_from_dir(dir):
    ret = {}
    
    for name in os.listdir(dir):
        if len(name) <= 9 or not name.startswith("biber_") or not name.endswith(".py"):
            continue
            
        name = name[:-3]
        mod = importlib.import_module(name)
        
        if not hasattr(mod, "generate_content"):
            raise BiberError(f"Plugin {name} has no generate_content method")
            
        name = name[6:]
            
        ret[name] = mod.generate_content
        print(f"Loaded plugin: {name}")
        
    return ret

def load_plugins(biber_dir, config):
    internal_dir = os.path.join(biber_dir, "plugins")
    plugins = {}
    
    sys.path.insert(0, internal_dir)
    plugins.update(load_plugins_from_dir(internal_dir))
    del sys.path[0]
    
    if config.get_blog("plugins") is not None:
        sys.path.insert(0, config.get_blog("plugins"))
        plugins.update(load_plugins_from_dir(config.get_blog("plugins")))
        del sys.path[0]
    
    return plugins

def get_post_files(dirname):
    for entry in os.listdir(dirname):
        entry = os.path.join(dirname, entry)
        
        if os.path.isdir(entry):
            for sub in os.listdir(entry):
                sub = os.path.join(entry, sub)
                
                if sub.endswith(".post"):
                    yield sub
        elif entry.endswith(".post"):
            yield entry

def biber_main():
    biber_dir = os.path.dirname(sys.modules["biber"].__file__)
    
    if len(sys.argv) != 2:
        print(f"USAGE: biber <config file>")
        exit(1)
        
    config = parse_config.parse_config(biber_dir, sys.argv[1])
    posts = []
    plugins= load_plugins(biber_dir, config)
    
    for id, filename in enumerate(get_post_files(config.get_blog("in"))):
        posts.append(parse_post.parse_post_file(filename, 0))
    
    posts.sort(key=lambda x: x.get_date())
    for i in range(len(posts)):
        posts[i].id = i + 1
    
    posts.sort(key=lambda x: x.get_date(), reverse=True)
    
    create_dirs.create_standard_dirs(biber_dir, config)
    
    create_index.create_index(config, posts)
    
    while posts:
        create_post.create_post(config, posts[0], plugins)
        del posts[0]

if __name__ == "__main__":
    biber_main()
