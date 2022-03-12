
RSS_FEED = "/feed.xml"
STATIC_FOLDER = "/"
KEY_FOLDER = "/keys/"
    
def post_folder(post):
    return f"/posts/{post.id}/"
    
def post_page(post):
    return post_folder(post) + "index.html"
