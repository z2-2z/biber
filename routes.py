
RSS_FEED = "/feed.xml"
STATIC_FOLDER = "/"
KEY_FOLDER = "/keys/"
POST_LISTING_PAGE = "/index.html"

def post_folder(post):
    return f"/posts/{post.id}/"
    
def post_page(post):
    return post_folder(post) + "index.html"
    
def get_catlist_page(cat):
    return f"/category/{cat.lower()}.html"
