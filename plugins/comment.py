import html

EXTRA_SCRIPTS = []
EXTRA_STYLESHEETS = []
EXTRA_FILES = []

def generate_content(content, flags):
    if "in-html" in flags and flags["in-html"].lower() == "true":
        return ["<!-- " + html.escape(content) + " -->"]
    else:
        return []
