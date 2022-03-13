import os
import sys
import multiprocessing
import locale
import importlib

from . import errors as biber_errors
from . import config as biber_config
from . import posts as biber_posts
from . import markdown

def list_importable_modules(dir):
    for entry in os.listdir(dir):
        if entry == "__pycache__":
            continue
        
        full_name = os.path.join(dir, entry)
        
        if os.path.isdir(full_name):
            yield entry
        elif entry.endswith(".py"):
            yield entry[:-3]

def load_plugins_from_dir(dir):
    ret = {}
    
    sys.path.insert(0, dir)
    
    for name in list_importable_modules(dir):
        mod = importlib.import_module(name)
        
        # check if the plugin has all the necessary attributes
        if not hasattr(mod, "generate_content") or not callable(mod.generate_content):
            raise biber_errors.BiberException(f"Plugin {name} has an invalid generate_content attribute")
        if not hasattr(mod, "EXTRA_SCRIPTS"):
            raise biber_errors.BiberException(f"Plugin {name} has no EXTRA_SCRIPTS attribute")
        if not hasattr(mod, "EXTRA_STYLESHEETS"):
            raise biber_errors.BiberException(f"Plugin {name} has no EXTRA_STYLESHEETS attribute")
        if not hasattr(mod, "EXTRA_FILES"):
            raise biber_errors.BiberException(f"Plugin {name} has no EXTRA_FILES attribute")
        
        ret[name] = mod
    
    del sys.path[0]
    
    return ret

def create_posts(config, plugins, posts):
    for post in posts:
        try:
            elements = markdown.parse_markdown(post.get_markdown())
        except markdown.ParsingException as e:
            raise biber_errors.BiberException(f"Parsing error in {post.filename}: {e}")
        
        config["blog"]["theme"].generate_post(post, elements, config, plugins)

#TODO: command line argument to use locale of system not en_US
#TODO: command line argument -f to force regeneration
#TODO: command line argument -j for threads
def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config file>")
        exit(1)
    
    try:
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')
    
    nthreads = 4
    
    config = biber_config.parse(sys.argv[1])
    posts = biber_posts.create_post_listing(config, True)
    theme = config["blog"]["theme"]
    plugins = {}
    
    if config["blog"]["plugins"] is not None:
        plugins = load_plugins_from_dir(config["blog"]["plugins"])
    
    if len(posts) == 0:
        return
    elif len(posts) <= nthreads:
        nthreads = 1
    
    bucket_size = (len(posts) + nthreads - 1) // nthreads
    
    theme.initialize()
    
    workers = []
    for i in range(0, len(posts), bucket_size):
        proc = multiprocessing.Process(
            target=create_posts,
            args=(config, plugins, posts[i : i + bucket_size])
        )
        proc.start()
        workers.append(proc)
    
    for proc in workers:
        proc.join()
    
    theme.copy_static_files(config)
    theme.generate_index(posts, config)
    theme.generate_catlist(posts, config)

if __name__ == "__main__":
    try:
        main()
    except biber_errors.BiberException as e:
        print(e, file=sys.stderr)
