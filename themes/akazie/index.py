from ... import routes, utils
from . import templates

def top_categories(config, posts):
    hits = {}
    
    for post in posts:
        for cat in post.metadata.categories:
            cat = cat.lower()
            
            if cat in hits:
                hits[cat] += 1
            else:
                hits[cat] = 1
                
    not_top_cats = sorted(hits.keys(), key=lambda x: hits[x], reverse=True)[5:]
    
    for name in not_top_cats:
        del hits[name]
        
    return hits

def generate_index(config, posts):
    out_file = utils.join_paths(
        config["blog"]["out"],
        routes.HOME_PAGE
    )
    stylesheets = [
        utils.join_paths(routes.STATIC_FOLDER, "css", "bootstrap.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "common.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "index.css"),
    ]
    scripts = [
        utils.join_paths(routes.STATIC_FOLDER, "js", "jquery.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "bootstrap.bundle.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "init_bootstrap.js"),
    ]
    top_cats = top_categories(config, posts)
    
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
            top_cats=top_cats.items(),
            cat_listing=routes.ALL_CATS_PAGE,
        ))
