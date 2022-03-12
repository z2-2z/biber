
import os
import sys
import shutil

from ... import utils, routes

def copy_static_files(config):
    input_dir = utils.join_paths(
        os.path.dirname(sys.modules["biber"].__path__[0]),
        "biber",
        "themes",
        "akazie",
        "static"
    )
    output_dir = utils.join_paths(
        config["blog"]["out"],
        routes.STATIC_FOLDER
    )
    
    shutil.copytree(input_dir, output_dir, dirs_exist_ok=True)
