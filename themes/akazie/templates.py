import os
import sys
import jinja2

environment = None

def initialize():
    global environment
    templates_dir = os.path.join(
        os.path.dirname(sys.modules["biber"].__path__[0]),
        "biber",
        "themes",
        "akazie",
        "templates"
    )
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_dir)
    )
    
def create_post(**kwargs):
    global environment
    template = environment.get_template("post.html")
    return template.render(kwargs)

def create_index(**kwargs):
    global environment
    template = environment.get_template("index.html")
    return template.render(kwargs)

def create_postlist(**kwargs):
    global environment
    template = environment.get_template("postlist.html")
    return template.render(kwargs)
    
def create_catlist(**kwargs):
    global environment
    template = environment.get_template("catlist.html")
    return template.render(kwargs)
