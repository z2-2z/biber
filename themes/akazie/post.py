from ... import routes, utils, elements
from . import templates

def generate_post(post, tree, config, plugins):
    out_file = utils.join_paths(
        config["blog"]["out"],
        routes.post_page(post)
    )
    
    stylesheets = [
        utils.join_paths(routes.STATIC_FOLDER, "css", "bootstrap.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "common.css"),
        utils.join_paths(routes.STATIC_FOLDER, "css", "post.css"),
    ]
    scripts = [
        utils.join_paths(routes.STATIC_FOLDER, "js", "jquery.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "bootstrap.bundle.min.js"),
        utils.join_paths(routes.STATIC_FOLDER, "js", "init_bootstrap.js"),
    ]
    elements = ["<b>yeet</b>"]
    
    with utils.create_open(out_file) as f:
        f.write(templates.create_post(
            title=post.metadata.title,
            stylesheets=stylesheets,
            scripts=scripts,
            static_folder=routes.STATIC_FOLDER,
            blog_title=config["blog"]["title"],
            socials=config["socials"],
            post_listing=routes.POST_LISTING_PAGE,
            elements=elements,
            post_date=post.metadata.date.strftime("%d %b. %Y"),
            categories=map(lambda x: (x, routes.get_catlist_page(x)), post.metadata.categories)
        ))
