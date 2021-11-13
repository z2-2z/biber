from biber import PluginError

def generate_content(content, args):
    class_ = "post-latex"
    extra = "$"
    
    if "inline" in args and args["inline"] == "true":
        class_ = "post-latex-inline"
        extra = ""
    
    content = content.strip().replace(">", "\gt ").replace("<", "\lt ")
    
    return f'<span class="{class_}">${extra}{content}{extra}$</span>'
