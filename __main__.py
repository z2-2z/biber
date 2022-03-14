import os
import sys
import locale
import importlib
import datetime

from . import errors as biber_errors
from . import config as biber_config
from . import posts as biber_posts
from . import markdown, routes, utils, pgp

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

def generate_feed(config, posts):
    if not config.has_feed():
        return
    if config["blog"]["domain"] is None:
        raise biber_errors.BiberException("Configuration is set to generate an RSS feed but no domain is given")
    
    out_file = utils.join_paths(
        config["blog"]["out"],
        routes.RSS_FEED
    )
    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
    
    with utils.create_open(out_file) as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>')
        f.write('<rss version="2.0">')
        f.write('<channel>')
        f.write(f'<title>{config["blog"]["title"]}</title>')
        f.write('<description></description>')
        f.write(f'<lastBuildDate>{now}</lastBuildDate>')
        f.write(f'<link>{config["blog"]["domain"]}{routes.RSS_FEED}</link>')
        f.write(f'<pubDate>{now}</pubDate>')
        f.write('<generator>biber 2.0</generator>')
        
        for post in posts:
            date = post.metadata.date.astimezone(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
            url = config["blog"]["domain"] + routes.post_page(post)
            f.write('<item>')
            f.write(f'<title>{post.metadata.title}</title>')
            f.write(f'<description>{post.metadata.title}: <a href="{url}">{url}</a></description>')
            f.write(f'<pubDate>{date}</pubDate>')
            
            for cat in post.metadata.categories:
                f.write(f'<category>{cat}</category>')
            
            f.write(f'<author>{post.metadata.author}</author>')
            f.write(f'<link>{url}</link>')
            f.write('</item>')
            
        f.write('</channel>')
        f.write('</rss>')

#TODO: command line argument to use locale of system not en_US
#TODO: command line argument -f to force regeneration
def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config file>")
        exit(1)
    
    try:
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')
    
    config = biber_config.parse(sys.argv[1])
    posts = biber_posts.create_post_listing(config, True)
    theme = config["blog"]["theme"]
    plugins = {}
    
    if config["blog"]["plugins"] is not None:
        plugins = load_plugins_from_dir(config["blog"]["plugins"])
    
    theme.initialize()
    create_posts(config, plugins, posts)
    theme.generate_pages(config, posts)
    generate_feed(config, reversed(posts[-config["feed"]["size"]:]))
    
    #TODO: sign stuff
    for social in config["socials"]:
        if social.name == "E-Mail":
            key = social.url.split("/")[-1].split(".")[0]
            pgp.dump_public_key(
                config,
                utils.join_paths(config["blog"]["out"], social.url),
                key
            )

if __name__ == "__main__":
    try:
        main()
    except biber_errors.BiberException as e:
        print(e, file=sys.stderr)
