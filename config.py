import os
import configparser

from .errors import BiberException
from . import routes
from . import themes

# If the PGP section is used in the config
# file, the following options MUST be set.
REQUIRED_PGP_SETTINGS = [
    "key"
]

# These are all mandatory settings for the
# Blog section of the config file.
REQUIRED_BLOG_SETTINGS = [
    "in",
    "out",
    "title",
    "domain",
    "theme"
]

THEMES = {
    "akazie" : themes.akazie
}

class Social:
    def __init__(self, format_url, icon, name):
        self._format_url = format_url
        self.icon = icon
        self.url = None
        self.name = name
        
    def build_url(self, value):
        self.url = self._format_url.format(value)

# These are all socials that are currently supported
ENABLED_SOCIALS = {
    "hackerone": Social("https://hackerone.com/{}?type=user", f"{routes.STATIC_FOLDER}img/hackerone.png", "HackerOne"),
    "github": Social("https://github.com/{}", f"{routes.STATIC_FOLDER}img/github.png", "Github"),
    "twitter": Social("https://twitter.com/{}", f"{routes.STATIC_FOLDER}img/twitter.png", "Twitter"),
    "email": Social(routes.KEY_FOLDER + "{}.asc", f"{routes.STATIC_FOLDER}img/email.png", "E-Mail"),
    "rss": Social(routes.RSS_FEED, f"{routes.STATIC_FOLDER}img/feed.png", "RSS"),
}

class Config:
    def __init__(self):
        self._pgp = {
            "dir" : None,
            "key" : None,
            "binary" : None,
            "sign-posts" : False
        }
        self._socials = []
        self._blog = {
            "in" : None,
            "out" : None,
            "title" : None,
            "plugins" : None,
            "domain" : None,
            "theme" : None,
        }
        self._feed = {
            "size" : None
        }
    
    def has_blog(self):
        for req in REQUIRED_BLOG_SETTINGS:
            if self._blog[req] is None:
                return False
        return True
    
    def has_socials(self):
        return bool(self._socials)
        
    def has_pgp(self):
        for req in REQUIRED_PGP_SETTINGS:
            if self._gpg[req] is None:
                return False
        return True
        
    def has_feed(self):
        return self._feed["size"] is not None and self._feed["size"] > 0
        
    def __getitem__(self, key):
        if key.lower() == "blog":
            return self._blog
        elif key.lower() == "socials":
            return self._socials
        elif key.lower() == "pgp":
            return self._pgp
        elif key.lower() == "feed":
            return self._feed
        else:
            raise BiberException("No such section in config file: {}", key)
            
    def parse_socials(self, socials):
        if self._socials:
            raise BiberException("Two sections with the name 'Social' in config file")
            
        for name, value in socials.items():
            name = name.lower()
            
            if name not in ENABLED_SOCIALS:
                raise BiberException(f"Social not supported: '{name}'")
            
            social = ENABLED_SOCIALS[name]
            social.build_url(value)
            self._socials.append(social)
            
    def parse_pgp(self, pgp):
        for option in pgp:
            if option not in self._pgp:
                raise BiberException(f"Invalid option in PGP section: '{option}'")
                
            self._pgp[option] = pgp[option]
            
        for req in REQUIRED_PGP_SETTINGS:
            if self._pgp[req] is None:
                raise BiberException(f"Required PGP configuration value is missing: '{req}'")
                
    def parse_blog(self, blog):
        for option in blog:
            if option not in self._blog:
                raise BiberException(f"Invalid option in Blog section: '{option}'")
                
            if option == "theme":
                value = blog[option]
                
                if value not in THEMES:
                    raise BiberException(f"Invalid theme: {value}")
                    
                self._blog[option] = THEMES[value]
            else:
                self._blog[option] = blog[option]
            
        for req in REQUIRED_BLOG_SETTINGS:
            if self._blog[req] is None:
                raise BiberException(f"Mandatory option not set in Blog section: '{req}'")
                
    def parse_feed(self, feed):
        for option in feed:
            if option not in self._feed:
                raise BiberException(f"Invalid option in Feed section: '{option}'")
                
            if option == "size":
                self._feed["size"] = int(feed[option])
            else:
                self._feed[option] = feed[option]

def parse(filename):
    ret = Config()
    config = configparser.ConfigParser(
        delimiters=(":",),
        comment_prefixes=("#",),
        default_section="SKIP",
        interpolation=None
    )
    config.read(filename)
    
    for section in config:
        if section == "SKIP":
            continue
        elif section.lower() == "socials":
            ret.parse_socials(config[section])
        elif section.lower() == "pgp":
            ret.parse_pgp(config[section])
        elif section.lower() == "blog":
            ret.parse_blog(config[section])
        elif section.lower() == "feed":
            ret.parse_feed(config[section])
        else:
            raise BiberException(f"Invalid section name: '{section}'")
            
    if not ret.has_blog():
        raise BiberException(f"The section 'Blog' is required but not set in the configuration file")
    
    if ret.has_feed():
        social = ENABLED_SOCIALS["rss"]
        social.build_url("")
        ret["socials"].append(social)
        
    return ret
