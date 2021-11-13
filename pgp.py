import subprocess

PROG = "gpg"

def run(cmd):
    return subprocess.run(
        cmd,
        check=True
    )

def dump_public_key(config, outfile, key):
    cmdline = [PROG]
    
    if config.has_pgp():
        if config.get_pgp("binary") is not None:
            cmdline[0] = config.get_pgp("binary")
            
        if config.get_pgp("dir") is not None:
            cmdline.extend(["--homedir", config.get_pgp("dir")])
            
    cmdline.extend(["--armor", "--yes", "-q", "--output", outfile, "--export", key])
    run(cmdline)

def create_detached_signature(config, file):
    outfile = f"{file}.sig"
    cmdline = [PROG]
    
    print(f"Signing {file}")
    
    if config.has_pgp():
        if config.get_pgp("binary") is not None:
            cmdline[0] = config.get_pgp("binary")
            
        if config.get_pgp("dir") is not None:
            cmdline.extend(["--homedir", config.get_pgp("dir")])
            
        if config.get_pgp("key") is not None:
            cmdline.extend(["--default-key", config.get_pgp("key")])
    
    cmdline.extend(["--armor", "--yes", "-q", "--output", outfile, "--detach-sign", file])
    run(cmdline)
