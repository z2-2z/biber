import os

HTML_DOC = """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <meta name="generator" content="biber">
        <title>{blog_title}</title>
        <link rel="stylesheet" href="css/bootstrap.css"/>
        <link rel="stylesheet" href="css/general.css"/>
        <link rel="stylesheet" href="css/index/index.css"/>
        <script src="js/bootstrap.bundle.min.js"></script>
    </head>
    <body>
        <div class="container">
            <div class="title-container">
                <span id="blog-title">{blog_title}</span>
            </div>
            <div class="social-list">
                {socials}
            </div>
            <div class="d-flex flex-row justify-content-center">
                <table>
                    <tbody>
                        {posts}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
</html>
"""

HTML_SOCIAL = """\
<div class="social-entry">
    <a class="social-link" href="{link}" target="_blank">
        <img class="social-img" src="{image}">
    </a>
</div>
"""

HTML_POST = """\
<tr>
    <td align="left" class="post-category">[{category}]{pad}</td>
    <td align="left" class="post-title"><a href="{link}">{title}</a></td>
    <td align="left" class="post-date">{date}</td>
</tr>
"""

def create_index(config, posts):
    index_html = os.path.join(config.get_blog("out"), "index.html")
    socials = []
    table = []
    max_size = 0
    
    for _, link, img in config.get_socials():
        socials.append(HTML_SOCIAL.format(link=link, image=img))
    
    for post in posts:
        if len(post.get_category()) > max_size:
            max_size = len(post.get_category())
    
    max_size += 1
    
    for post in posts:
        date_str = post.get_date().strftime("%d. %b %Y")
        table.append(HTML_POST.format(
            category=post.get_category(),
            pad="&nbsp;" * (max_size - len(post.get_category())),
            link=f"posts/{post.id}/index.html",
            title=post.get_title(),
            date=date_str
        ))
    
    with open(index_html, "w") as f:
        f.write(HTML_DOC.format(
            blog_title=config.get_blog("title"),
            socials="".join(socials),
            posts="".join(table)
        ))
