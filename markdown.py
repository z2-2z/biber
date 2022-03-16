from . import elements
from . import utils

import markdown_it

def parse_heading(token, stream):
    levels = {
        "h1": 1,
        "h2": 2,
        "h3": 3,
        "h4": 4,
        "h5": 4,
        "h6": 4
    }
    
    if token.tag not in levels:
        raise ParsingException(f"Invalid heading type '{token.tag}'")
        
    element = elements.Heading(levels[token.tag])
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed heading")
            
        if token.type == "heading_close":
            break
        else:
            element.extend(parse_any(token, stream))
    
    return element
    
def parse_strong(token, stream):
    element = elements.Strong()
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed strong")
            
        if token.type == "strong_close":
            break
        else:
            element.extend(parse_any(token, stream))
    
    return element
    
def parse_paragraph(token, stream):
    element = elements.Paragraph()
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed paragraph")
        
        if token.type == "paragraph_close":
            break
        else:
            element.extend(parse_any(token, stream))
    
    return element
    
def parse_argstring(argstring):
    ret = {}
    
    while argstring:
        res, argstring = utils.next_escaped(argstring, " ")
        
        if "=" not in res:
            raise ParsingException("Invalid plugin arguments")
            
        name, value = res.split("=", 1)
        ret[name] = value
        
    return ret
    
def parse_codeblock(token, stream):
    if not token.info:
        return elements.Block(token.content)
    else:
        name, *argstring = token.info.strip().split(" ", 1)
        args = {}
        if argstring:
            args = parse_argstring(argstring[0])
        return elements.PluginInvocation(name, args, token.content)

def parse_list_item(token, stream):
    element = elements.ListItem()
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed list item")
        
        if token.type == "list_item_close":
            break
        else:
            element.extend(parse_any(token, stream))
    
    return element

def parse_list(token, stream):
    element = None
    
    if token.type == "bullet_list_open":
        element = elements.UnorderedList()
    elif token.type == "ordered_list_open":
        element = elements.OrderedList()
    else:
        raise ParsingException(f"Invalid list type: {token.type}")
        
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed list")
            
        if token.type == "bullet_list_close" or token.type == "ordered_list_close":
            break
        else:
            element.items.append(parse_list_item(token, stream))
            
    return element
    
def parse_blockquote(token, stream):
    element = elements.Quote()
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed blockquote")
            
        if token.type == "blockquote_close":
            break
        else:
            element.extend(parse_any(token, stream))
    
    return element
    
def parse_linebreak(token, stream):
    return elements.LineBreak()

def parse_emphasis(token, stream):
    element = elements.Emphasis(len(token.markup))
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed emphasis")
            
        if token.type == "em_close":
            break
        else:
            element.extend(parse_any(token, stream))
            
    return element
    
def parse_tag(token, stream):
    return elements.Tag(token.content)
    
def parse_link(token, stream):
    element = elements.Link(token.attrs["href"])
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed link")
            
        if token.type == "link_close":
            break
        else:
            element.extend(parse_any(token, stream))
    
    return element
    
def parse_image(token, stream):
    alt = []
    
    if "alt" not in token.attrs or token.children:
        substream = iter(token.children)
        for child in substream:
            alt.extend(parse_any(child, substream))
    else:
        alt.append(elements.Text(token.attrs["alt"]))
    
    return elements.Image(token.attrs["src"], alt)

def parse_th(token, stream):
    element = elements.Th()
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed th")
            
        if token.type == "th_close":
            break
        else:
            element.extend(parse_any(token, stream))
    
    return element

def parse_td(token, stream):
    element = elements.Td()
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed td")
            
        if token.type == "td_close":
            break
        else:
            element.extend(parse_any(token, stream))
    
    return element

def parse_tr(token, stream):
    element = elements.Trow()
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed tr")
            
        if token.type == "tr_close":
            break
        elif token.type == "th_open":
            element.append(parse_th(token, stream))
        elif token.type == "td_open":
            element.append(parse_td(token, stream))
        else:
            raise ParsingException(f"Unexpected markdown element in tr: {token.type}")
    
    return element

def parse_thead(token, stream):
    ret = None
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed thead")
            
        if token.type == "thead_close":
            break
        elif token.type == "tr_open":
            if ret is not None:
                raise ParsingException(f"Got more than one row in thead")
                
            ret = parse_tr(token, stream)
        else:
            raise ParsingException(f"Unexpected markdown element in thead: {token.type}")
    
    return ret
    
def parse_tbody(token, stream):
    ret = []
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed tbody")
            
        if token.type == "tbody_close":
            break
        elif token.type == "tr_open":
            ret.append(parse_tr(token, stream))
        else:
            raise ParsingException(f"Unexpected markdown element in tbody: {token.type}")
    
    return ret

def parse_table(token, stream):
    element = elements.Table()
    
    while True:
        try:
            token = next(stream)
        except StopIteration:
            raise ParsingException(f"Unclosed table")
            
        if token.type == "table_close":
            break
        elif token.type == "thead_open":
            element.head = parse_thead(token, stream)
        elif token.type == "tbody_open":
            element.body = parse_tbody(token, stream)
        else:
            raise ParsingException(f"Unexpected markdown element in table: {token.type}")
    
    return element

ANY_ITEMS = {
    "heading_open" : parse_heading,
    "paragraph_open" : parse_paragraph,
    "code_block" : parse_codeblock,
    "fence": parse_codeblock,
    "bullet_list_open" : parse_list,
    "ordered_list_open" : parse_list,
    "blockquote_open" : parse_blockquote,
    "softbreak": parse_linebreak,
    "hardbreak": parse_linebreak,
    "text": lambda x,_: elements.Text(x.content),
    "strong_open": parse_strong,
    "em_open": parse_emphasis,
    "code_inline": parse_tag,
    "link_open": parse_link,
    "image": parse_image,
    "table_open" : parse_table,
}
IGNORED_ITEMS = [
    "hr",
    "html_block",
    "html_inline"
]
def parse_any(token, stream):
    if token.type in IGNORED_ITEMS:
        return []
    elif token.type not in ANY_ITEMS:
        print(token)
        raise ParsingException(f"Unknown markdown element: {token.type}")
    
    return [ ANY_ITEMS[token.type](token, stream) ]

def token_stream(tokens):
    # DEBUG:
    #def get_types(it):
    #    return list(map(lambda x: x.type if x.type != "inline" else get_types(x.children), it))
    #print(get_types(tokens))
    
    for token in tokens:
        if token.hidden:
            continue
            
        if token.type == "inline":
            for child in token_stream(token.children):
                yield child
        else:
            yield token

def parse_markdown(content):
    ret = []
    md = markdown_it.MarkdownIt("commonmark", {
        "typographer": True
    })
    md.enable(["replacements", "smartquotes", "table"])
    stream = iter(token_stream(md.parse(content)))
    
    for token in stream:
        ret.extend(parse_any(token, stream))
    
    return ret
