from flask import Flask, render_template
from style import add_ellipsis, extract_markdown, readingTime, get_url, html_readingTime, html_postDate, html_title, html_img, html_desc, html_tag, get_url_by_name
import os, json
from datetime import datetime
basedir = os.path.dirname(os.path.abspath(__file__))
RUN_SERVER = False
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(os.path.join(basedir, '..'), 'static'))

keywords = 'Blogifyr, free blogging platform, diverse topics, community-driven, storytelling, articles, writers, readers, content discovery, online blogging, free content, digital publications, personal essays, opinion pieces, creative writing, technology, culture, lifestyle, education'

# inpath = ''
outdir = os.path.join(basedir, '..\\posts')

def Trending(n=3):
    blogs = [(os.path.join(outdir, i, 'index.html'), i) for i in os.listdir(outdir) if os.path.isdir(os.path.join(outdir, i))]
    blogs = blogs[:n]
    posts = [{'url': f'/posts/{url}',
              'idx': "{:02}".format(idx+1),
              'title': f"{html_title(b)}",
              'date': f"{html_postDate(b)}",
              'length': f'{html_readingTime(b)} min',
              'author': 'ThefCraft',
              'author_url': '/about',
              'author_img': 'c5f67cbc-b58f-46cc-864a-5e48b2a6d582.jpg'} for idx, (b, url) in enumerate(blogs)]
    return posts

allTags = []

def updateAndReturnTags(self):
    allTags.extend(self)
    return self

def get_tags():
    tags = [{
            'name': name,
            'url': name,
    } for name in set(allTags)]
    return tags
def TrendingTags(n=9):
    return list(set(allTags))[:n]

def get_posts():
    blogs = [(os.path.join(outdir, i, 'index.html'), i) for i in os.listdir(outdir) if os.path.isdir(os.path.join(outdir, i))]
    posts = [{'url': f'/posts/{url}',
                  'title': add_ellipsis(html_title(b)),
                  'subtitle': add_ellipsis(html_desc(b)),
                  'img': html_img(b),
                  'tag': html_tag(b)[0],
                  'tag_url': f'/tag/{get_url_by_name(html_tag(b)[0])}',
                  'tags': updateAndReturnTags(html_tag(b)),
                  'date': f"{html_postDate(b)}",
                  'length': f'{html_readingTime(b)} min',
                  'author': 'ThefCraft',
                  'author_url': '/about',
                  'author_img': 'c5f67cbc-b58f-46cc-864a-5e48b2a6d582.jpg'} for b, url in blogs]
    return posts

def update_sitemap():
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
    xmlns:xhtml="http://www.w3.org/1999/xhtml"
    xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0"
    xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
    xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
    <url>
        <loc>https://blog.thefcraft.site/</loc>
        <changefreq>daily</changefreq>
        <priority>1</priority>
        <lastmod>{datetime.now().strftime("%Y-%m-%dT%H:%M:%S+05:30")}</lastmod>
    </url>
    <url>
        <loc>https://blog.thefcraft.site/posts/</loc>
        <changefreq>monthly</changefreq>
        <priority>1</priority>
    </url>
    <url>
        <loc>https://blog.thefcraft.site/about/</loc>
        <changefreq>monthly</changefreq>
        <priority>1</priority>
    </url>
        <url>
        <loc>https://blog.thefcraft.site/privacy/</loc>
        <changefreq>monthly</changefreq>
        <priority>1</priority>
    </url>
        <url>
        <loc>https://blog.thefcraft.site/search/</loc>
        <changefreq>monthly</changefreq>
        <priority>1</priority>
    </url>
        <url>
        <loc>https://blog.thefcraft.site/terms/</loc>
        <changefreq>monthly</changefreq>
        <priority>1</priority>
    </url>
        <url>
        <loc>https://blog.thefcraft.site/user/ThefCraft/</loc>
        <changefreq>monthly</changefreq>
        <priority>1</priority>
    </url>
    <url>
        <loc>https://blog.thefcraft.site/posts/</loc>
        <changefreq>monthly</changefreq>
        <priority>1</priority>
    </url>'''
    for url in [name for name in os.listdir(outdir) if os.path.isdir(os.path.join(basedir, '..\\posts', name))]:
        xml+=f'''\n\t<url>
        <loc>https://blog.thefcraft.site/posts/{url}</loc>
        <changefreq>monthly</changefreq>
        <priority>1</priority>
    </url>'''
    
    xml+='\n</urlset>'

    with open(os.path.join(basedir, '..', 'sitemap.xml'), 'w') as f:
        f.write(xml)

def split_into_chunks(lst, chunk_size):
    """Splits a list into chunks of a given size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

 

def update_api():
    posts_chunks = split_into_chunks(get_posts(), 16)   
    for idx, chunk in enumerate(posts_chunks, 1):
        with open(os.path.join(basedir, '..', 'api', f'posts_{idx}.json'), 'w') as f: json.dump({
            "posts": chunk
        }, f)
    with open(os.path.join(basedir, '..', 'api', f'posts.json'), 'w') as f: json.dump({
            "posts_chunk": [f'posts_{idx}.json' for idx, chunk in enumerate(posts_chunks, 1)]
        }, f)
    with open(os.path.join(basedir, '..', 'api', 'tags.json'), 'w') as f: json.dump({
        "tags": get_tags()
    }, f)

def index():
    # DONT remove trending and home_posts here as if you remove it then this site is not accessible by bots anymore
    return render_template('newUser.html', 
                               trending=Trending(), 
                               trendingTags=TrendingTags(), 
                               home_posts=get_posts(), 
                               keywords = keywords,
                               url='https://blog.thefcraft.site/', 
                               domain='blog.thefcraft.site')

if __name__ == '__main__':
    update_api()
    with app.app_context(): 
        with open(os.path.join(os.path.join(basedir), '..\\index.html'), 'w', encoding='utf') as f:
            f.write(index())
    update_sitemap()
        
    if RUN_SERVER: app.run(debug=True, host='127.0.0.1', port=8088)
    
    
    
    
    
    
    
    