from ... import routes, utils
from . import templates

def generate_postlist(config, posts):
    out_file = utils.join_paths(
        config["blog"]["out"],
        routes.POST_LISTING
    )
    stylesheets = [
        utils.join_paths(routes.STATIC_FOLDER, "css", "bootstrap.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "common.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "postlist.css"),
    ]
    scripts = [
        utils.join_paths(routes.STATIC_FOLDER, "js", "jquery.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "bootstrap.bundle.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "init_bootstrap.js"),
    ]
    
    with utils.create_open(out_file) as f:
        f.write(templates.create_postlist(
            blog_title=config["blog"]["title"],
            stylesheets=stylesheets,
            scripts=scripts,
            static_folder=routes.STATIC_FOLDER,
            socials=config["socials"],
            posts=reversed(posts),
            get_post_route=routes.post_page,
            get_cat_route=routes.get_catlist_page,
        ))
