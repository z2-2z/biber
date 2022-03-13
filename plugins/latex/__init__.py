
import html

EXTRA_SCRIPTS = [
    "custom.js",
    "polyfill.min.js",
    "tex-mml-chtml.js",
]
EXTRA_STYLESHEETS = [
    "custom.css"
]
EXTRA_FILES = [
    "output/chtml/fonts/woff-v2/MathJax_Zero.woff",
    "output/chtml/fonts/woff-v2/MathJax_Math-Italic.woff",
    "output/chtml/fonts/woff-v2/MathJax_Main-Regular.woff",
    "output/chtml/fonts/woff-v2/MathJax_Size2-Regular.woff"
]

def generate_content(content, args):
    return [f'<span class="plugin-latex">$${html.escape(content)}$$</span>']
