import os
import datetime

from .errors import BiberException
from . import routes
from . import utils

REQUIRED_METADATA = [
    "author",
    "date",
    "categories",
    "title"
]
ENABLED_METADATA = REQUIRED_METADATA + [
    "sign",
    "attachment"
]

class Metadata:
    def __init__(self, author, date, categories, title, sign=[], attachment=[]):
        self.author = author
        self.date = date
        self.categories = categories
        self.title = title
        self.sign = sign
        self.attachment = attachment

def metadata_parse_list(value):
    ret = []
    
    while value:
        res, value = utils.next_escaped(value, ",")
        ret.append(res)
    
    return ret

class Post:
    def __init__(self, filename):
        self.filename = filename
        self.start_pos = None
        self.id = None
        self.metadata = None
        
    def parse_metadata(self):
        data = {}
        lineno = 1
        
        with open(self.filename) as f:
            while True:
                line = f.readline().strip()
                
                if not line:
                    self.start_pos = f.tell()
                    break
                
                if ":" not in line:
                    raise BiberException(f"Invalid metadata line in post file {self.filename} line {lineno}")
                    
                key, value = line.split(":", 1)
                
                if key not in ENABLED_METADATA:
                    raise BiberException(f"Unknown metadata keyword '{key}' in post {self.filename}")
                elif key in data:
                    raise BiberException(f"Metadata keyword '{key}' specified twice in {self.filename}")
                
                value = value.strip()
                
                if key == "date":
                    if value.count(".") != 2:
                        raise BiberException(f"Invalid date in {self.filename}")
                    
                    day, month, year = value.split(".")
                    
                    try:
                        day = int(day)
                        month = int(month)
                        year = int(year)
                    except ValueError:
                        raise BiberException(f"Invalid date in {self.filename}")
                    
                    data[key] = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc)
                elif key == "categories":
                    cats = metadata_parse_list(value)
                    data[key] = list(map(str.upper, cats))
                elif key in ["sign", "attachment"]:
                    data[key] = metadata_parse_list(value)
                else:
                    data[key] = value
                    
                lineno += 1
                
        for req in REQUIRED_METADATA:
            if req not in data:
                raise BiberException(f"Metadata missing in {self.filename}: {req}")
                    
        self.metadata = Metadata(**data)
        
    def get_markdown(self):
        if self.start_pos is None:
            raise BiberException(f"Trying to read markdown content from post before reading the metadata")
        
        with open(self.filename) as f:
            f.seek(self.start_pos)
            return f.read()
        
def get_post_files(dirname):
    for entry in os.listdir(dirname):
        entry = os.path.join(dirname, entry)
        
        if os.path.isdir(entry):
            for file in get_post_files(entry):
                yield file
        elif entry.endswith(".post"):
            yield entry
        
def create_post_listing(config, force=False):
    ret = []
    
    for post_file in get_post_files(config["blog"]["in"]):
        post = Post(post_file)
        post.parse_metadata()
        ret.append(post)
    
    ret.sort(key=lambda x: x.metadata.date)
    
    for i in range(len(ret)):
        ret[i].id = i + 1
    
    # Don't render posts again that have not changed
    if not force:
        i = 0
        while i < len(ret):
            out_file = utils.join_paths(config["blog"]["out"], routes.post_page(ret[i]))

            try:
                if os.path.getmtime(ret[i].filename) < os.path.getmtime(out_file):
                    del ret[i]
                    continue
            except OSError:
                pass
            
            i += 1
    
    return ret
