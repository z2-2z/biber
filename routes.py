
RSS_FEED = "/feed.xml"
STATIC_FOLDER = "/"
KEY_FOLDER = "/keys/"
HOME_PAGE = "/index.html"
POST_LISTING = "/posts.html"
ALL_CATS_PAGE = "/categories.html"

def post_folder(post):
    return f"/posts/{post.id}/"
    
def post_page(post):
    return post_folder(post) + "index.html"
    
def get_catlist_page(cat):
    return f"/category/{cat.lower()}.html"

def plugin_folder(name):
    return f"/plugin/{name}/"
