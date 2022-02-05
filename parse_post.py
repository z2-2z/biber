import datetime

import commonmark

"""
This file offers the functionality to
parse a single .post file.
The structure of a .post file is as follows:
1. Metadata in the form of "<keyword>: <value>"
   Supported keywords are: author, category, date
2. A post title denoted with a single '#' like in markdown
3. Commonmark (not markdown!) content that gets translated to HTML
"""

class ParsingError(Exception):
    pass

# A list of all commonmark token types
all_types = [
    "heading",
    "code",
    "quote",
    "image",
    "tag",
    "linebreak",
    "bold",
    "italic",
    "link",
    "text",
    "unordered_list_start",
    "unordered_list_end",
    "ordered_list_start",
    "ordered_list_end",
    "item_start",
    "item_end",
    "start_description",
    "end_description"
]

# A list of metadata that MUST appear
# in a .post file
must_have_meta = [
    "author",
    "date",
    "category"
]

class Token:
    def __init__(self, type, content=None, option=None):
        if type not in all_types:
            raise ParsingError(f"Invalid Token type: {type}")
        
        self.type = type
        self.option = option
        self.content = content
    
    def __repr__(self):
        option = self.option
        content = self.content
        
        if isinstance(self.option, str):
            option = "\"" + option.replace("\n", "\\n") +  "\""
            
        if isinstance(self.content, str):
            content =  "\"" + content.replace("\n", "\\n") +  "\""
            
        return f"Token(type={self.type}, option={option}, content={content})"

class Post:
    def __init__(self, filename, pos, tokens, id, meta):
        self._author = meta["author"]
        self._date = None
        self._category = None
        self.filename = filename
        self._pos = pos
        self.id = id
        self.meta = meta
        
        self.set_date(meta["date"])
        self.set_category(meta["category"])
        del self.meta["author"]
        del self.meta["date"]
        del self.meta["category"]
        
        if tokens[0].type != "heading" or tokens[0].option != 1:
            raise ParsingError("First element must be post heading")
        
        self._title = tokens[0].content
        
        self._content = None
    
    def set_date(self, date):
        day, month, year = map(int, date.split("."))
        self._date = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc)
        
    def set_category(self, cat):
        self._category = cat.upper()
        
    def get_title(self):
        return self._title
        
    def get_author(self):
        return self._author
        
    def get_date(self):
        return self._date
        
    def get_category(self):
        return self._category
        
    def tokens(self):
        return iter(self._content)
        
    def load_content(self):
        with open(self.filename) as f:
            f.seek(self._pos)
            self._content = parse_md(f.read())
            
    def date_str(self):
        return self._date.strftime("%d. %b %Y")
        
    def link(self):
        return f"posts/{self.id}/index.html"

def get_metadata(f):
    meta = {}
    
    while True:
        line = f.readline()[:-1]
        
        if not line:
            break
            
        if ": " not in line:
            raise ParsingError(f"Malformed input")
            
        key, value = line.split(": ", 1)
        
        if key in ["sign", "attachment"]:
            meta[key] = list( map(str.strip, value.strip().split(",")) )
        else:
            meta[key] = value
    
    for key in must_have_meta:
        if key not in meta:
            raise ParsingError(f"{key} is missing in post metadata")
    
    return meta

def parse_md(content):
    nesting_level = 0
    tokens = []
    ast = commonmark.Parser().parse(content)
    in_description = False
    
    it = iter(ast.walker())
    
    for node, entering in it:
        if node.t not in ["list", "item"] and not entering:
            continue
        
        if node.t == "linebreak":
            tokens.append(Token("linebreak"))
        
        elif node.t == "heading":
            if node.level >= 4:
                raise ParsingError(f"Only heading levels 1 - 3 are supported")
                
            text = ""
            
            for node, entering in it:
                if node.t == "heading" and not entering:
                    break
                    
                if node.t == "text":
                    text += node.literal
                
            if text is None:
                raise ParsingError("Got no heading text")
                
            tokens.append(Token(f"heading", text, node.level))
                
        elif node.t == "code_block":
            tokens.append(Token("code", node.literal, node.info))
            
        elif node.t == "block_quote":
            content = ""
            
            for node, entering in it:
                if node.t == "block_quote" and not entering:
                    break
                
                if node.t == "text":
                    content += node.literal
                elif node.t == "softbreak":
                    content += " "
            
            tokens.append(Token("quote", content))
            
        elif node.t == "image":
            link = node.destination
            
            for node, entering in it:
                if node.t == "image" and not entering:
                    break
            
            tokens.append(Token("image", link))
            tokens.append(Token("start_description"))
            in_description = True
            
        elif node.t == "code":
            tokens.append(Token("tag", node.literal))
            
        elif node.t == "html_inline":
            html = node.literal
            
            if html in ["<br>", "<br/>"]:
                if in_description:
                    tokens.append(Token("end_description"))
                    in_description = False
                else:
                    tokens.append(Token("linebreak", None))
            else:
                raise ParsingError("Invalid inline html")
                
        elif node.t == "strong":
            text = None
            
            for node, entering in it:
                if node.t == "strong" and not entering:
                    break
                    
                if node.t == "text":
                    text = node.literal
            
            if text is None:
                raise ParsingError("No bold text detected")
            
            tokens.append(Token("bold", text))
            
        elif node.t == "emph":
            text = None
            
            for node, entering in it:
                if node.t == "emph" and not entering:
                    break
                    
                if node.t == "text":
                    text = node.literal
            
            if text is None:
                raise ParsingError("No italic text detected")
            
            tokens.append(Token("italic", text))
            
        elif node.t == "link":
            text = None
            
            for node, entering in it:
                if node.t == "link" and not entering:
                    break
                
                if node.t == "text":
                    text = node.literal
                    
            if text is None:
                raise ParsingError("No link text detected")
                
            tokens.append(Token("link", node.destination, text))
            
        elif node.t in ["text", "html_block"]:
            if tokens and tokens[-1].type == "text":
                tokens[-1].content += node.literal
            else:
                tokens.append(Token("text", node.literal))
            
        elif node.t == "softbreak":
            if tokens[-1].type == "text":
                tokens[-1].content += " "
            
        elif node.t == "list" and node.list_data["type"] == "bullet":
            if entering:
                if nesting_level > 0:
                    tokens.append(Token("item_end"))
                
                nesting_level += 1
                tokens.append(Token("unordered_list_start"))
            else:
                nesting_level -= 1
                tokens.append(Token("unordered_list_end"))
            
        elif node.t == "list" and node.list_data["type"] == "ordered":
            if entering:
                if nesting_level > 0:
                    tokens.append(Token("item_end"))
                
                nesting_level += 1
                tokens.append(Token("ordered_list_start"))
            else:
                nesting_level -= 1
                tokens.append(Token("ordered_list_end"))
                
        elif node.t == "item":
            if entering:
                tokens.append(Token("item_start"))
            elif tokens[-1].type not in ["ordered_list_end", "unordered_list_end"]:
                tokens.append(Token("item_end"))
                
    if in_description:
        tokens.append(Token("end_description"))
                
    return tokens

def parse_post_file(filename, id):
    tokens = None
    meta = None
    pos = None
    
    with open(filename) as f:
        meta = get_metadata(f)
        tokens = parse_md(f.readline())
        pos = f.tell()
            
    return Post(filename, pos, tokens, id, meta)
