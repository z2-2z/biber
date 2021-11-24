import os
import configparser

required_pgp_settings = [
    "key"
]
required_blog_settings = [
    "in",
    "out",
    "title"
]
enabled_socials = {
    "hackerone" : ("HackerOne", "https://hackerone.com/{handle}?type=user", "img/hackerone.png"),
    "github" :    ("Github",    "https://github.com/{handle}",              "img/github.png"),
    "twitter":    ("Twitter",   "https://twitter.com/{handle}",             "img/twitter.png"),
    "pubkey":     ("PGP",       "keys/{handle}.asc",                        "img/email.png"),
    "rss" :       ("RSS",       "feed.xml",                                 "img/feed.png")
}

class ConfigError(Exception):
    pass

class Config:
    def __init__(self):
        self._pgp = {}
        self._socials = []
        self._blog = {}
        
    def has_blog(self):
        return bool(self._blog)
    
    def has_socials(self):
        return bool(self._socials)
        
    def has_pgp(self):
        return bool(self._pgp)
        
    def get_pgp(self, key):
        return self._pgp[key]
        
    def get_socials(self):
        return self._socials
        
    def get_blog(self, key):
        return self._blog[key]

def parse_section_socials(biber_dir, section):
    ret = [
        enabled_socials["rss"]
    ]
    
    for key in section:
        value = section[key]
        key = key.lower()
        
        if key not in enabled_socials:
            raise ConfigError(f"Social not supported: '{key}'")
        
        ret.append((
            enabled_socials[key][0],
            enabled_socials[key][1].format(handle=value),
            enabled_socials[key][2]
        ))
    
    return ret

def parse_section_pgp(section):
    pgp = {
        "dir" : None,
        "key" : None,
        "binary" : None,
        "sign-posts" : "false"
    }
    
    for key in section:
        if key not in pgp:
            raise ConfigError(f"Invalid value in PGP section: '{key}'")
            
        pgp[key] = section[key]
    
    for req in required_pgp_settings:
        if pgp[req] is None:
            raise ConfigError(f"Required PGP configuration value is missing: '{req}'")
            
    return pgp

def parse_section_blog(section):
    blog = {
        "in" : None,
        "out" : None,
        "title" : None,
        "plugins" : None,
        "feed-size" : 25,
        "feed-domain" : None
    }
    
    for key in section:
        if key not in blog:
            raise ConfigError(f"Invalid value in Blog section: '{key}'")
            
        blog[key] = section[key]
        
        if key == "feed-size":
            blog[key] = int(blog[key])
    
    for req in required_blog_settings:
        if blog[req] is None:
            raise ConfigError(f"Required configuration value in section 'Blog' is missing: '{req}'")
            
    return blog

def parse_config(biber_dir, filename):
    ret = Config()
    config = configparser.ConfigParser(delimiters=(":",), comment_prefixes=("#",), default_section="SKIP", interpolation=None)
    config.read(filename)
    
    for section in config:
        if section == "SKIP":
            continue
        elif section.lower() == "socials":
            ret._socials = parse_section_socials(biber_dir, config[section])
        elif section.lower() == "pgp":
            ret._pgp = parse_section_pgp(config[section])
        elif section.lower() == "blog":
            ret._blog = parse_section_blog(config[section])
        else:
            raise ConfigError(f"Invalid section name: '{section}'")
            
    if not ret.has_blog():
        raise ConfigError(f"The section 'Blog' is required but not set in the configuration file")
        
    return ret
