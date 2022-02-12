from biber import PluginError, md_to_html

def parse_align(flags):
    ret = []
    if "align" not in flags:
        raise PluginError("table needs align argument")
    
    for opt in flags["align"].split("|"):
        opt = opt.strip()
        if opt == "l":
            ret.append("left")
        elif opt == "c":
            ret.append("center")
        elif opt == "r":
            ret.append("right")
        else:
            raise PluginError(f"Invalid alignment value in table: {opt}")
    
    return ret

def parse_style(flags):
    if "style" in flags:
        styles = {
            "striped" : "table-striped",
            "bordered" : "table-bordered",
            "small" : "table-sm"
        }
        
        if flags["style"] not in styles:
            raise PluginError(f"Invalid table style: {flags['style']}")
            
        return styles[flags["style"]]
    else:
        return ""

def parse_spacing(flags, cols):
    if "spacing" in flags:
        spacings = {
            "equal" : f"{100 // cols}%",
            "auto" : "auto"
        }
        
        if flags["spacing"] not in spacings:
            raise PluginError(f"Invalid table spacing: {flags['spacing']}")
            
        return spacings[flags["spacing"]]
    else:
        return "auto"

def generate_content(content, flags):
    head_rows = []
    body_rows = []
    aligns = parse_align(flags)
    style = parse_style(flags)
    spacing = parse_spacing(flags, len(aligns))
    
    separator = "|"
    if "separator" in flags:
        separator = flags["separator"]
        
        if len(separator) != 1:
            raise PluginError(f"Invalid separator: {separator}")
    
    for line in content.split("\n"):
        if not line.strip():
            continue
        elif line == "---":
            if head_rows:
                raise PluginError("head and body separator specified multiple times in table")
            head_rows = body_rows
            body_rows = []
            
        else:
            row = []
            
            for cell in line.split(f" {separator} "):
                row.append(md_to_html(cell))
            
            if len(row) != len(aligns):
                raise PluginError("Invalid column count in table")
            
            body_rows.append(row)
    
    table = f'<div class="table-responsive"><table class="table {style}">'
    
    if head_rows:
        table += '<thead>'
        for row in head_rows:
            table += '<tr>'
            for i, cell in enumerate(row):
                table += f'<td width="{spacing}" align="{aligns[i]}">{cell}</td>'
            table += '</tr>'
        table += '</thead>'
            
    if body_rows:
        table += '<tbody>'
        for row in body_rows:
            table += '<tr>'
            for i, cell in enumerate(row):
                table += f'<td width="{spacing}" align="{aligns[i]}">{cell}</td>'
            table += '</tr>'
        table += '</tbody>'
        
    return table + '</table></div>'
        
