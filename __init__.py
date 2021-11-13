class PluginError(Exception):
    pass

from .parse_post import parse_md as _parse_md
from .create_post import tokenstream_to_html as _tokenstream_to_html

def md_to_html(content):
    return _tokenstream_to_html(_parse_md(content))
