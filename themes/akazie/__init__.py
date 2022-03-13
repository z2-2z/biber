
from .post import generate_post, element_to_html
from .templates import initialize

from .index import generate_index as _generate_index
from .catlist import generate_catlist as _generate_catlist
from .static import copy_static_files as _copy_static_files
from .postlist import generate_postlist as _generate_postlist

def generate_pages(config, posts):
    _generate_index(config, posts)
    _generate_catlist(config, posts)
    _generate_postlist(config, posts)
    _copy_static_files(config)
