import os
import sys
import multiprocessing

from . import errors as biber_errors
from . import config as biber_config
from . import posts as biber_posts
from . import markdown

def create_posts(config, plugins, posts):
    for post in posts:
        try:
            elements = markdown.parse_markdown(post.get_markdown())
        except markdown.ParsingException as e:
            raise biber_errors.BiberException(f"Parsing error in {post.filename}: {e}")
        
        config["blog"]["theme"].generate_post(post, elements, config, plugins)

#TODO: command line argument -f to force regeneration
#TODO: command line argument -j for threads
def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config file>")
        exit(1)
    
    nthreads = 4
    
    config = biber_config.parse(sys.argv[1])
    posts = biber_posts.create_post_listing(config, True)
    plugins = None
    theme = config["blog"]["theme"]
    
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
