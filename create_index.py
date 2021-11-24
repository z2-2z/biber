import os
import datetime

class FeedError(Exception):
    pass

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
        {feed_meta}
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

def create_feed(link, config, posts):
    feed_size = config.get_blog("feed-size")
    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
    out_file = os.path.join(config.get_blog("out"), link)
    
    with open(out_file, "w") as feed:
        feed.write(f"""<?xml version="1.0" encoding="UTF-8" ?>
            <rss version="2.0">
                <channel>
                    <title>{config.get_blog("title")}</title>
                    <description></description>
                    <lastBuildDate>{now}</lastBuildDate>
                    <link>{config.get_blog("feed-domain")}</link>
                    <pubDate>{now}</pubDate>
                    <generator>biber</generator>
        """)
        
        for i in range(min(feed_size, len(posts))):
            date = posts[i].get_date().astimezone(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
            link = os.path.join(config.get_blog("feed-domain"), "posts", str(posts[i].id), "index.html")
            feed.write(f"""\
                    <item>
                        <title>{posts[i].get_title()}</title>
                        <description><a href="{link}">{posts[i].get_title()}</a></description>
                        <pubDate>{date}</pubDate>
                        <link>{link}</link>
                        <guid isPermaLink="false">{posts[i].id}</guid>
                        <category>{posts[i].get_category()}</category>
                        <author>{posts[i].get_author()}</author>
                    </item>
            """)
        
        feed.write("""
                </channel>
            </rss>
        """)

def create_index(config, posts):
    index_html = os.path.join(config.get_blog("out"), "index.html")
    socials = []
    table = []
    max_size = 0
    feed_meta = ""
    
    for type, link, img in config.get_socials():
        if type == "RSS":
            if config.get_blog("feed-domain") is None:
                continue
            
            create_feed(link, config, posts)
            href = f"{config.get_blog('feed-domain')}/feed.xml"
            feed_meta = f"""<link rel="alternate" type="application/rss+xml" href="{href}" title="{config.get_blog('title')}"/>"""
            
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
            posts="".join(table),
            feed_meta=feed_meta
        ))
