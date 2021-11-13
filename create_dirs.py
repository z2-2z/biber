import os
import shutil

from . import pgp

mode = 0o750
dirs = {
    "content/css" : "css",
    "content/img" : "img",
    "content/js"  : "js"
}

def recursive_copy(src_dir, dst_dir):
    for entry in os.listdir(src_dir):
        src = os.path.join(src_dir, entry)
        dst = os.path.join(dst_dir, entry)
        
        if os.path.isfile(src):
            shutil.copyfile(src, dst)
        else:
            os.makedirs(dst, mode=mode, exist_ok=True)
            recursive_copy(src, dst)

def create_standard_dirs(biber_dir, config):
    for src_dir, dst_dir in dirs.items():
        src_dir = os.path.join(biber_dir, src_dir)
        dst_dir = os.path.join(config.get_blog("out"), dst_dir)
        os.makedirs(dst_dir, mode=mode, exist_ok=True)
        recursive_copy(src_dir, dst_dir)
    
    os.makedirs(os.path.join(config.get_blog("out"), "keys"), mode=mode, exist_ok=True)
    
    for type, url, _ in config.get_socials():
        if type == "PGP":
            fpr = url.split("/")[1].split(".")[0]
            pgp.dump_public_key(config, os.path.join(config.get_blog("out"), url), fpr)
