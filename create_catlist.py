import os

from . import create_index

def make_catdir(config):
    dir = os.path.join(config.get_blog("out"), "category")
    os.makedirs(dir, mode=0o750, exist_ok=True)
    return dir
    
def create_entries(posts):
    ret = ""
    
    for post in posts:
        ret += create_index.HTML_POST.format(
            category=post.get_category(),
            link=post.link(),
            title=post.get_title(),
            date=post.date_str(),
            pad="&nbsp;",
            urlbase="../"
        )
    
    return ret
    
def create_socials(config):
    ret = ""
    feed_meta = ""
    
    for type, link, img in config.get_socials():
        if type == "RSS":
            if config.get_blog("feed-domain") is None:
                continue
            
            href = f"{config.get_blog('feed-domain')}/feed.xml"
            feed_meta = create_index.HTML_FEED.format(href=href, title=config.get_blog('title'))
            
            
        # All socials with local links:
        if type in ["RSS", "PGP"]:
            link = "../" + link
            
        ret += create_index.HTML_SOCIAL.format(urlbase="../", link=link, image=img)
    
    return feed_meta, ret

def create_catlist(config, posts):
    outdir = make_catdir(config)
    all_cats = {}
    
    for post in posts:
        cat = post.get_category()
        
        if cat in all_cats:
            all_cats[cat].append(post)
        else:
            all_cats[cat] = [post]
    
    for cat in all_cats:
        outfile = os.path.join(outdir, f"{cat}.html")
        
        with open(outfile, "w") as f:
            feed_meta, socials = create_socials(config)
            f.write(create_index.HTML_DOC.format(
                urlbase="../",
                blog_title=config.get_blog("title"),
                posts=create_entries(all_cats[cat]),
                socials=socials,
                feed_meta=feed_meta
            ))
        
