from ... import routes, utils
from . import templates

def category_hits(config, posts):
    hits = {}
    
    for post in posts:
        for cat in post.metadata.categories:
            cat = cat.lower()
            
            if cat in hits:
                hits[cat] += 1
            else:
                hits[cat] = 1
        
    return hits

def generate_index(config, posts):
    out_file = utils.join_paths(
        config["blog"]["out"],
        routes.HOME_PAGE
    )
    stylesheets = [
        utils.join_paths(routes.STATIC_FOLDER, "css", "bootstrap.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "common.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "listing.css"),
    ]
    scripts = [
        utils.join_paths(routes.STATIC_FOLDER, "js", "jquery.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "bootstrap.bundle.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "init_bootstrap.js"),
    ]
    cats = category_hits(config, posts)
    
    with utils.create_open(out_file) as f:
        f.write(templates.create_index(
            blog_title=config["blog"]["title"],
            stylesheets=stylesheets,
            scripts=scripts,
            static_folder=routes.STATIC_FOLDER,
            socials=config["socials"],
            posts=reversed(posts[-10:]),
            get_post_route=routes.post_page,
            get_cat_route=routes.get_catlist_page,
            post_listing=routes.POST_LISTING,
            cats=cats.items(),
        ))
