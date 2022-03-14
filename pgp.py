import subprocess
import os

PROG = "gpg"

def run(cmd):
    return subprocess.run(
        cmd,
        check=True
    )

def dump_public_key(config, outfile, key):
    cmdline = [PROG]
    
    if config.has_pgp():
        if config["pgp"]["binary"] is not None:
            cmdline[0] = config["pgp"]["binary"]
            
        if config["pgp"]["dir"] is not None:
            cmdline.extend(["--homedir", config["pgp"]["dir"]])
    
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    cmdline.extend(["--armor", "--yes", "-q", "--output", outfile, "--export", key])
    run(cmdline)

def create_detached_signature(config, file):
    outfile = f"{file}.sig"
    cmdline = [PROG]
    
    if config.has_pgp():
        if config["pgp"]["binary"] is not None:
            cmdline[0] = config["pgp"]["binary"]
            
        if config["pgp"]["dir"] is not None:
            cmdline.extend(["--homedir", config["pgp"]["dir"]])
            
        if config["pgp"]["key"] is not None:
            cmdline.extend(["--default-key", config["pgp"]["key"]])
    
    cmdline.extend(["--armor", "--yes", "-q", "--output", outfile, "--detach-sign", file])
    run(cmdline)
