from ... import routes, utils
from . import templates

def generate_catlist(config, posts, cat):
    out_file = utils.join_paths(
        config["blog"]["out"],
        routes.get_catlist_page(cat)
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
    selected_posts = []
    
    for post in posts:
        if cat in post.metadata.categories:
            selected_posts.append(post)
    
    with utils.create_open(out_file) as f:
        f.write(templates.create_catlist(
            blog_title=config["blog"]["title"],
            stylesheets=stylesheets,
            scripts=scripts,
            static_folder=routes.STATIC_FOLDER,
            socials=config["socials"],
            posts=reversed(selected_posts),
            get_post_route=routes.post_page,
            get_cat_route=routes.get_catlist_page,
            cat=cat.lower(),
        ))

def generate_catlists(config, posts):
    cats = set()
    
    for post in posts:
        for cat in post.metadata.categories:
            cats.add(cat)
            
    for cat in cats:
        generate_catlist(config, posts, cat)
