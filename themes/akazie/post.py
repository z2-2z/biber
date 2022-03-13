from ... import routes, utils, elements, ThemeException
from . import templates

import os
import sys
import html
import shutil

used_images = set()
used_plugins = set()

def heading_to_html(heading):
    fmt_open_tag = "<h{}>"
    fmt_close_tag = "</h{}>"
    
    ret = [
        fmt_open_tag.format(heading.level + 1)
    ]
    
    for subel in heading:
        ret.extend(element_to_html(subel))
    
    ret.append(fmt_close_tag.format(heading.level + 1))
    return ret
    
def text_to_html(text):
    return [text]
    
def paragraph_to_html(paragraph):
    ret = ["<p>"]
    
    for subel in paragraph:
        ret.extend(element_to_html(subel))
    
    ret.append("</p>")
    return ret
    
def strong_to_html(strong):
    ret = ["<b>"]
    
    for subel in strong:
        ret.extend(element_to_html(subel))
    
    ret.append("</b>")
    return ret
    
def linebreak_to_html(linebreak):
    return ["<br>"]

def emphasis_to_html(emphasis):
    ret = ["<em>" * emphasis.strength]
    
    for subel in emphasis:
        ret.extend(element_to_html(subel))
    
    ret.append("</em>" * emphasis.strength)
    return ret
    
def block_to_html(block):
    global used_plugins
    used_plugins.add("code")
    
    return [
        '<pre><code class="language-none">'
        + html.escape(block)
        + '</code></pre>'
    ]
    
def plugin_to_html(block, plugins):
    global used_plugins
    used_plugins.add(block.name)
    
    # The "code" plugin is built in 
    if block.name == "code":
        try:
            lang = block.args["language"]
        except KeyError:
            lang = "plain"
            
        try:
            if block.args["line-numbers"] in ["yes", "true", "on", "show", "enable", "activate"]:
                lnos = "line-numbers"
            else:
                lnos = ""
        except KeyError:
            lnos = ""
        
        try:
            tmp = int(block.args["line-start"])
            lstart = str(tmp)
        except KeyError:
            lstart = "1"
        except ValueError:
            raise ThemeException(f"Invalid line-start argument: {block.args['line-start']}")
        
        return [
            f'<pre data-start="{lstart}" class="{lnos}"><code class="language-{lang}">'
            + html.escape(block.content)
            + '</code></pre>'
        ]
    else:
        if block.name not in plugins:
            raise ThemeException(f"Plugin {block.name} not found")
            
        return plugins[block.name].generate_content(block.content, block.args)

def unordered_list_to_html(element):
    ret = ["<ul>"]
    
    for item in element.items:
        if not isinstance(item, elements.ListItem):
            raise ThemeException(f"Items of unordered list are not classical list items")
        
        ret.append("<li>")
        
        for subel in item:
            ret.extend(element_to_html(subel))
        
        ret.append("</li>")
    
    ret.append("</ul>")
    return ret

def ordered_list_to_html(element):
    ret = ['<ol>']
    
    for item in element.items:
        if not isinstance(item, elements.ListItem):
            raise ThemeException(f"Items of unordered list are not classical list items")
        
        ret.append("<li>")
        
        for subel in item:
            ret.extend(element_to_html(subel))
        
        ret.append("</li>")
    
    ret.append("</ol>")
    return ret

def tag_to_html(element):
    return [
        '<code class="language-none">' + element + '</code>'
    ]
    
def quote_to_html(element):
    ret = ['<div class="quote">']
    
    for subel in element:
        ret.extend(element_to_html(subel))
    
    ret.append("</div>")
    return ret

def link_to_html(element):
    ret = [f'<a href="{element.href}" target="_blank">']
    
    for subel in element:
        ret.extend(element_to_html(subel))
    
    ret.append('</a>')
    return ret

def image_to_html(element):
    global used_images
    used_images.add(element.src)
    
    ret = [f'<center><img class="figure" src="{element.src}" alt="']
    
    for subel in element.alt:
        ret.extend(element_to_html(subel))
        
    ret.append('"></center>')
    return ret

def element_to_html(element, plugins=None):
    if not isinstance(element, elements.Element):
        raise ThemeException(f"Tried to convert an invalid element to html: {element}")
    
    if isinstance(element, elements.Heading):
        return heading_to_html(element)
    elif isinstance(element, elements.Text):
        return text_to_html(element)
    elif isinstance(element, elements.Paragraph):
        return paragraph_to_html(element)
    elif isinstance(element, elements.Strong):
        return strong_to_html(element)
    elif isinstance(element, elements.LineBreak):
        return linebreak_to_html(element)
    elif isinstance(element, elements.Emphasis):
        return emphasis_to_html(element)
    elif isinstance(element, elements.Block):
        return block_to_html(element)
    elif isinstance(element, elements.PluginInvocation):
        if plugins is None:
            raise ThemeException(f"Trying to invoke plugin without a valid plugin list")
        
        return plugin_to_html(element, plugins)
    elif isinstance(element, elements.UnorderedList):
        return unordered_list_to_html(element)
    elif isinstance(element, elements.OrderedList):
        return ordered_list_to_html(element)
    elif isinstance(element, elements.Tag):
        return tag_to_html(element)
    elif isinstance(element, elements.Quote):
        return quote_to_html(element)
    elif isinstance(element, elements.Link):
        return link_to_html(element)
    elif isinstance(element, elements.Image):
        return image_to_html(element)
    else:
        raise ThemeException(f"Invalid element: {type(element)}")

def handle_plugins(config, plugins):
    global used_plugins
    styles = []
    scripts = []
    
    if "code" in used_plugins:
        styles.append(utils.join_paths(routes.STATIC_FOLDER, "css", "prism.css"))
        scripts.append(utils.join_paths(routes.STATIC_FOLDER, "js", "prism.js"))
        used_plugins.remove("code")
    
    for name in used_plugins:
        plugin_dir = utils.join_paths(config["blog"]["plugins"], name)
        if not os.path.isdir(plugin_dir):
            plugin_dir = config["blog"]["plugins"]
        
        out_dir = utils.join_paths(config["blog"]["out"], routes.plugin_folder(name))
        
        for filename in plugins[name].EXTRA_SCRIPTS:
            utils.create_copy(
                utils.join_paths(plugin_dir, filename),
                utils.join_paths(out_dir, filename)
            )
            scripts.append(
                utils.join_paths(routes.plugin_folder(name), filename)
            )
            
        for filename in plugins[name].EXTRA_STYLESHEETS:
            utils.create_copy(
                utils.join_paths(plugin_dir, filename),
                utils.join_paths(out_dir, filename)
            )
            styles.append(
                utils.join_paths(routes.plugin_folder(name), filename)
            )
            
        for filename in plugins[name].EXTRA_FILES:
            utils.create_copy(
                utils.join_paths(plugin_dir, filename),
                utils.join_paths(out_dir, filename)
            )
    
    used_plugins.clear()
    
    return scripts, styles

def generate_post(post, tree, config, plugins):
    global used_images
    
    out_file = utils.join_paths(
        config["blog"]["out"],
        routes.post_page(post)
    )
    
    stylesheets = [
        utils.join_paths(routes.STATIC_FOLDER, "css", "bootstrap.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "common.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "post.css"),
    ]
    scripts = [
        utils.join_paths(routes.STATIC_FOLDER, "js", "jquery.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "bootstrap.bundle.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "init_bootstrap.js"),
    ]
    elements = []
    
    for element in tree:
        elements.extend(element_to_html(element, plugins))
    
    # Copy the plugin files and insert necessary script/style tags
    extra_scripts, extra_styles = handle_plugins(config, plugins)
    
    with utils.create_open(out_file) as f:
        f.write(templates.create_post(
            title=post.metadata.title,
            stylesheets=stylesheets + extra_styles,
            scripts=scripts + extra_scripts,
            static_folder=routes.STATIC_FOLDER,
            blog_title=config["blog"]["title"],
            socials=config["socials"],
            home_page=routes.HOME_PAGE,
            elements=elements,
            post_date=post.metadata.format_date(),
            categories=map(lambda x: (x, routes.get_catlist_page(x)), post.metadata.categories)
        ))
        
    for img in used_images:
        input = utils.join_paths(os.path.dirname(post.filename), img)
        output = utils.join_paths(os.path.dirname(out_file), img)
        utils.create_copy(input, output)
    used_images.clear()
    
    #TODO: handle sign
    
    for att in post.metadata.attachment:
        input_file = utils.join_paths(
            os.path.dirname(post.filename),
            att
        )
        output_file = utils.join_paths(
            config["blog"]["out"],
            routes.post_folder(post),
            att
        )
        utils.create_copy(input_file, output_file)
