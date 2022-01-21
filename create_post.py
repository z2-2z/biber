import os
import shutil

from . import pgp

class TemplateError(Exception):
    pass

HTML_DOC = """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <meta name="generator" content="biber">
        <title>{post_title}</title>
        <link rel="stylesheet" href="../../css/bootstrap.css"/>
        <link rel="stylesheet" href="../../css/general.css"/>
        <link rel="stylesheet" href="../../css/prism.css"/>
        <link rel="stylesheet" href="../../css/post/post.css"/>
        <script src="../../js/bootstrap.bundle.min.js"></script>
        <script src="../../js/prism.js"></script>
        <script src="../../js/polyfill.min.js"></script>
        <script>
            MathJax = {{
                tex: {{
                    inlineMath: [['$', '$']]
                }},
                chtml: {{
                    scale: 1.3
                }}
            }};
        </script>
        <script src="../../js/mathjax.min.js" id="MathJax-script" async></script>
    </head>
    <body>
        <div class="post-root container-fluid">
            <div class="title-container">
                <h3 id="post-title">{post_title}</h3>
            </div>
            <div class="post-content">
                {post_content}
            </div>
            
            <br/>
            <div class="post-footer">
                <span><a href="../../index.html">home</a></span>
                <span><a href="index.html.sig">signature</a></span>
            </div>
        </div>
    </body>
</html>
"""

def insert_image(token, *args):
    return f'''\
        <div class="post-figure">
            <center>
                <img class="unselectable" src="{token.content}"/>
    '''
    
def insert_start_description(*args):
    return '<p class="post-figure-description">'
    
def insert_end_description(*args):
    return '</p></center></div>'
    
def insert_heading(token, *args):
    if token.option == 2:
        return f'<h4>{token.content}</h4>'
    elif token.option == 3:
        return f'<h5>{token.content}</h5>'
    else:
        raise TemplateError(f"Invalid heading level {token.option}")

def parse_argstr(argstr):
    l = []
    args = {}
        
    for a in argstr.split(","):
        key, value = a.split("=", 1)
        args[key.strip()] = value
    
    return args

def insert_code(token, plugins, *args):
    option = token.option.strip()
    content = token.content
    
    if option:
        keyword = None
        args = {}
        
        if " " in option:
            keyword, argstr = option.split(" ", 1)
            args = parse_argstr(argstr)
        else:
            keyword = option
            
        if keyword in plugins:
            return plugins[keyword](content, args)
            
        raise TemplateError(f"Invalid code keyword '{keyword}'")
    else:
        return f'''<pre><code class="language-plain">{content}</code></pre>'''
        
def insert_quote(token, *args):
    return f'''\
        <div class="post-quote">
            <p>
                {token.content}
            </p>
        </div>
    '''
    
def insert_tag(token, *args):
    return f'''<code class="post-tag language-none">{token.content}</code>'''
    
def insert_linebreak(*args):
    return "<br/>"
    
def insert_bold(token, *args):
    return f'<b>{token.content}</b>'

def insert_italic(token, *args):
    return f'<i>{token.content}</i>'

def insert_link(token, *args):
    return f'<a href="{token.content}" target="_blank">{token.option}</a>'

def insert_text(token, *args):
    return token.content
    
def insert_unordered_list_start(*args):
    return '<ul>'
    
def insert_unordered_list_end(*args):
    return '</ul>'
    
def insert_ordered_list_start(*args):
    return '<ol>'
    
def insert_ordered_list_end(*args):
    return '</ol>'

def insert_item_start(*args):
    return '<li>'
    
def insert_item_end(*args):
    return '</li>'

handlers = {
    "heading" : insert_heading,
    "code" : insert_code,
    "quote" : insert_quote,
    "image" : insert_image,
    "tag" : insert_tag,
    "linebreak" : insert_linebreak,
    "bold" : insert_bold,
    "italic" : insert_italic,
    "link" : insert_link,
    "text" : insert_text,
    "unordered_list_start" : insert_unordered_list_start,
    "unordered_list_end" : insert_unordered_list_end,
    "ordered_list_start" : insert_ordered_list_start,
    "ordered_list_end" : insert_ordered_list_end,
    "item_start" : insert_item_start,
    "item_end" : insert_item_end,
    "start_description" : insert_start_description,
    "end_description" : insert_end_description
}

# External function for plugins
def tokenstream_to_html(tokens):
    html = []
    
    for token in tokens:
        if token.type == "code":
            raise TemplateError("code blocks are not allowed for plugins")
        
        html.append(handlers[token.type](token))
    
    return "".join(html)

def make_postdir(config, post):
    dir = os.path.join(config.get_blog("out"), "posts", f"{post.id}")
    os.makedirs(dir, mode=0o750, exist_ok=True)
    return dir

def create_post(config, post, plugins):
    content = []
    out_dir = make_postdir(config, post)
    out_file = os.path.join(out_dir, "index.html")
    
    if not os.path.isfile(out_file) or os.path.getmtime(post.filename) >= os.path.getmtime(out_file):
        print(f"Generating post {post.id}")
        
        post.load_content()
        
        for token in post.tokens():
            if token.type == "image":
                in_dir = os.path.dirname(post.filename)
                shutil.copyfile(os.path.join(in_dir, token.content), os.path.join(out_dir, token.content))
            
            content.append(handlers[token.type](token, plugins))
            
        with open(out_file, "w") as f:
            f.write(HTML_DOC.format(
                post_title=post.get_title(),
                post_content="".join(content)
            ))
        
        if "attachment" in post.meta:
            for infile in post.meta["attachment"]:
                outfile = os.path.join(out_dir, infile)
                infile = os.path.join(os.path.dirname(post.filename), infile)
                shutil.copyfile(infile, outfile)
        
    # Always sign
    
    if config.has_pgp() and config.get_pgp("sign-posts") == "true":
        pgp.create_detached_signature(config, out_file)
    
    
    if "sign" in post.meta:
        if not config.has_pgp():
            raise TemplateError("'sign' option given in post but no PGP key specified in config file")
        
        for infile in post.meta["sign"]:
            outfile = os.path.join(out_dir, infile)
            infile = os.path.join(os.path.dirname(post.filename), infile)
            
            if not os.path.isfile(outfile):
                shutil.copyfile(infile, outfile)
            
            pgp.create_detached_signature(config, outfile)
