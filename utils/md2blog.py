from flask import Flask, render_template
from style import blog, add_ellipsis, extract_markdown, readingTime, get_url, extract_metadata_and_markdown, sha256, get_img, html_timestamp
import os, random
from bs4 import BeautifulSoup
from datetime import datetime
basedir = os.path.dirname(os.path.abspath(__file__))

inpath = os.path.join(basedir, '..', 'md')
outdir = os.path.join(basedir, '..', 'posts')
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(os.path.join(basedir, '..'), 'static'))

def index(title, description, data, keywords, url, tags, timestamp=None):
    post_date = datetime.now() if timestamp is None else timestamp
    b = blog(user='ThefCraft',
        userPNG='c5f67cbc-b58f-46cc-864a-5e48b2a6d582.jpg',
        userFollowers='00',
        userDescription='Explore the dynamic fusion of mathematics and computing through the eyes of ThefCraft, a B.Tech. student at IIT Patna. Delve into the depths of algorithms, data analysis, artificial intelligence, deep learning and computational techniques in this captivating blog. Join ThefCraft on a journey of innovation and discovery at the intersection of two powerful disciplines.',
        title=add_ellipsis(title),
        subtitle=add_ellipsis(description),
        post_date=f"{post_date.strftime('%b %d, %Y')}",
        read_time=f'{readingTime(data)} min',
        reactions={
            'claps': random.randint(1, 999),
            'Responds': str(random.randint(1, 999))
        },
        tags=tags)
    b.add(extract_markdown(data))
    
    
    return render_template('blogNewUser.html', 
                           title=add_ellipsis(b.title),
                           headingHTML = b.getHeadingHTML(),
                           contentHTML = b.html, 
                           rootFooterHTML = b.getRootFooterHTML(),
                           data=b.html,
                           author='ThefCraft',
                           img = get_img(data),
                           keywords = keywords,
                           description = add_ellipsis(description),
                           post_date=post_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                           url=f'https://blog.thefcraft.site/posts/{url}', 
                           domain='blog.thefcraft.site'
                        )

if __name__ == '__main__': 
    import argparse
    parser = argparse.ArgumentParser(description='Convert markdown to HTML')
    parser.add_argument('--force', action='store_true', help='Force generation.')
    args = parser.parse_args()
    for md_name in os.listdir(inpath):
        try:
            with open(os.path.join(inpath, md_name), 'r', encoding='utf') as f:
                data = f.read()
                metadata, md = extract_metadata_and_markdown(data)
                assert  metadata.get('layout') == 'post'

                title = metadata['title']
                description = metadata.get('description')
                tags = metadata['tags']
            
            url = get_url(title, key=sha256(title), blog_id=int(md_name.removesuffix('.md')), short_url=True) 
            outpath = os.path.join(outdir, url)
            timestamp = None
            if os.path.exists(outpath): 
                try:
                    with open(os.path.join(outpath, 'sha256.hash'), 'rb') as fhash: hash_read = fhash.read()
                except FileNotFoundError: ...
                else:
                    if hash_read == sha256(data):
                        print(f"ALREADY EXISTS : {url}")
                        if not args.force:
                            continue
                    print(f"UPDATING EXISTS : {url}")
                    with open(os.path.join(outpath, 'index.html'), 'r', encoding='utf') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                    timestamp = html_timestamp(soup)
                finally:
                    with open(os.path.join(outpath, 'sha256.hash'), 'wb') as fhash: fhash.write(sha256(data))
                
            with app.app_context(): 
                if not os.path.exists(outpath): os.makedirs(outpath)
                with open(os.path.join(outpath, 'index.html'), 'w', encoding='utf') as f:
                    f.write(index(title, description, md, keywords = 'keywords in head of the post', url=url, tags=tags, timestamp=timestamp))
                with open(os.path.join(outpath, 'sha256.hash'), 'wb') as fhash: fhash.write(sha256(data))
                
            if not timestamp: print(f"CREATED : {url}")
        except KeyboardInterrupt: break
        # except Exception as e:
        #     print(f"ERROR : {url}")
    