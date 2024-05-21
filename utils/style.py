from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from werkzeug.utils import secure_filename
from secrets import token_bytes
import hashlib
import os
import re
import html
import yaml
import uuid
import shortuuid
import markdown2
from bs4 import BeautifulSoup

def sha256(data):
    return hashlib.sha256(data.encode('utf') if isinstance(data, str) else data).digest()

def extract_markdown(data:str):
    data = data
    
    # Define the pattern to search for
    pattern = r"```(\w*)\n([\s\S]*?)\n```"
    
    # replacement = r'<pre><code class="\1">\2</code></pre>'
    # modified_content = re.sub(pattern, replacement, data)
    modified_content = re.sub(pattern, lambda mch: f'<pre><code class="{mch.group(1)}">{html.escape(mch.group(2))}</code></pre>', data)
    
    
    
    pattern = r"!\[(.*?)\][ ]*\((.*?)\)"
    replacement = r'![\1](\2) <figcaption>\1</figcaption>'
    modified_content = re.sub(pattern, replacement, modified_content)
    

    # # Regular expression pattern to find URLs with varying schemes
    # modified_content = re.sub(r'!\[(.*?)\]\((.*?)\)', r' ![\1](\2) ', modified_content)
    # matches = re.finditer(r'(\(?\s*https?://\S+\s*\)?)', modified_content)
    # formated_text = modified_content
    # for mth in matches:
    #     url = mth.group(1)
    #     if not re.match(r'(\(.*?\))', url):
    #         formated_text = formated_text.replace(url, f' [{url}]() ')
    # modified_content = formated_text

    
    return markdown2.markdown(modified_content).replace('<hr />', '<div class="separator"><span>• • •</span></div>')


class IndexCipher:
    def __init__(self, key:str):
        # Apply SHA-256 hash function to the key
        self.hashed_key = hashlib.sha256(key.encode() if isinstance(key, str) else key).digest()
        
    def encode(self, idx:int, key=None)->str:
        return shortuuid.encode(self.encrypt_index(idx=idx, uudi_formated=True, key=key))    
    def decode(self, s:str, key=None)->int:
        return self.decrypt_index(shortuuid.decode(s), key=key)
    
    def encrypt_index(self, idx:int, uudi_formated=True, key=None)->str:
        hashed_key = hashlib.sha256(key.encode() if isinstance(key, str) else key).digest() if key else self.hashed_key
        # Convert the index to bytes
        if idx is None:
            idx_bytes = token_bytes(8)
        else:
            idx_bytes = str(idx).encode('utf-8')

        # Pad the plaintext to match the block size
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(idx_bytes) + padder.finalize()

        # Encrypt the padded plaintext
        cipher = Cipher(algorithms.AES(hashed_key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_idx = encryptor.update(padded_data) + encryptor.finalize()
        assert len(encrypted_idx) == 16
        # Convert the encrypted bytes to a UUID-like string
        hex_string = ''.join(['{:02x}'.format(byte) for byte in encrypted_idx])
        if uudi_formated:
            return uuid.UUID(f"{hex_string[:8]}-{hex_string[8:12]}-{hex_string[12:16]}-{hex_string[16:20]}-{hex_string[20:]}")
        else:
            return ''.join([hex_string[i:i+8] for i in range(0, len(hex_string), 8)])

    def decrypt_index(self, encrypted_id:str, key=None)->int:
        hashed_key = hashlib.sha256(key.encode() if isinstance(key, str) else key).digest() if key else self.hashed_key
        # Split the UUID-like string and convert to bytes
        encrypted_bytes = bytes.fromhex(str(encrypted_id).replace('-', ''))

        # Decrypt the encrypted bytes
        cipher = Cipher(algorithms.AES(hashed_key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_bytes) + decryptor.finalize()

        # Unpad the decrypted data
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

        # Convert bytes back to the original index
        original_idx = int(unpadded_data.decode('utf-8'))
        return original_idx


def readingTime(markdown_text: str, words_per_minute: int = 200):
    # Remove Markdown-style links and images from the text
    text = re.sub(r'!\[.*?\]\(.*?\)', '', markdown_text)  # Remove images
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)   # Remove links
    
    # Count the number of words in the text
    word_count = len(text.split())

    # Calculate reading time in minutes
    reading_time = word_count // words_per_minute
    return max(reading_time, 1)

def get_img(markdown_text):
    pattern = r"!\[.*?\][ ]*\((.*?)\)"
    match = re.search(pattern, markdown_text)
    return match.group(1) if match else None

def get_url_by_name(name:str):
    return secure_filename(name)

def get_img(markdown_text):
    pattern = r"!\[.*?\][ ]*\((.*?)\)"
    match = re.search(pattern, markdown_text)
    return match.group(1) if match else None

def add_ellipsis(text_content, max_len=100):
    if isinstance(text_content, str):
        return text_content[:max_len-1]+'...' if len(text_content)>=max_len else text_content
    else: 
        return text_content

def get_sub_title(markdown_text):
    html_content = markdown2.markdown(markdown_text)
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text()
    return add_ellipsis(text_content, 100)

def get_url(title:str, blog_id=None, key='secret_key', short_url=False)->str:
    url = title.lower()
    # Replace spaces with dashes
    url = url.replace(' ', '-')
    # Remove special characters
    url = re.sub(r'[^a-zA-Z0-9-]', '', url)
    if short_url:
        if isinstance(key, str):
            return f'{url}-{IndexCipher(str(key)).encrypt_index(blog_id, uudi_formated=False)[:8]}'
        else:
            return f'{url}-{IndexCipher(key).encrypt_index(blog_id, uudi_formated=False)[:8]}'
    
    if isinstance(key, str):
        return f'{url}-{IndexCipher(str(key)).encode(blog_id)}'
    else:
        return f'{url}-{IndexCipher(key).encode(blog_id)}'
def get_id(url:str, key)->int:
    return IndexCipher(str(key)).decode(url.split('-')[-1])
def check_url(url, blog, key:str)->bool:
    if not blog: return False
    return get_url(blog.title, blog_id=blog.id, key=key) == url

def extract_metadata_and_markdown(text):
    # Define the regular expression pattern to match text between '---' delimiters
    pattern = r'---\n(.*?)\n---'
    
    # Use re.findall to find all matches of the pattern in the text
    matches = re.findall(pattern, text, re.DOTALL)    
    assert len(matches) > 0
    
    metadata_content = matches[0]
    metadata = yaml.safe_load(metadata_content)
    md = re.sub(pattern, '', text, count=1, flags=re.DOTALL).lstrip()
    return (metadata, md)

def html_title(path):
    with open(path, 'r', encoding='utf') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        return soup.title.text
    
def html_postDate(path):
    with open(path, 'r', encoding='utf') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        txt = soup.find("div", {"id": "readTime"}).text
        return txt.split('·')[1].strip()
    
def html_readingTime(path):
    with open(path, 'r', encoding='utf') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        txt = soup.find("div", {"id": "readTime"}).text
        return [int(s) for s in txt.split('·')[0].strip().split() if s.isdigit()][0]

def html_img(path):
    with open(path, 'r', encoding='utf') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        first_image = soup.find("div", {"id": "content"}).find('img')
        if first_image:
            image_source = first_image['src']
            return image_source
        return None
def html_tag(path):
    with open(path, 'r', encoding='utf') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        tags = soup.find("div", {"id": "tag-footer"}).find_all('a')
        return [tag.text for tag in tags]

def html_desc(path):
    with open(path, 'r', encoding='utf') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        heading = soup.find("div", {"class": "heading"})
        desc = heading.find("h2")
        return desc.text if desc else None
    
class blog:
    def __init__(self, 
                 user=None,
                 userPNG=None,
                 userFollowers=None,
                 userDescription='',
                 title=None,
                 subtitle=None,
                 post_date=None,
                 read_time=None,
                 reactions={
                     'claps': '0',
                     'Responds': '0'
                 },
                 tags=[],
                 data=''
        ) -> None:
        
        self.title = title
        self.user = user if user else 'anonymous'
        self.userPNG = userPNG if userPNG else 'None.png'
        self.userFollowers = userFollowers if userFollowers else '--'
        self.userDescription = (userDescription if userDescription else '') if user else 'The author of this blog post is an anonymous contributor who prefers to remain unidentified. They have chosen to share their insights and thoughts without creating an account or revealing their identity. Despite their anonymity, their writing provides valuable information and perspectives on various topics.'
        self.subtitle = subtitle
        self.post_date = post_date
        self.read_time = read_time
        self.reactions = reactions
        self.tags = tags
        self.data = data
    
    @property
    def html(self): return self.data+self.getFooterHTML()
    
    def getHeadingHTML(self):
        html = f'<h1>{self.title}</h1>'
        if self.subtitle: html+=f'<h2 style="font-weight:300;" id="blog-desc">{self.subtitle}</h2>'
        html+=f'''<div class="heading-userData-container">
                <img alt="{self.user}" src="/static/userPNG/{self.userPNG}" width="44" height="44" loading="lazy">
                <div class="heading-userData">
                    <div>
                        <a href="/user/{get_url_by_name(self.user)}" id="userName">{self.user}</a> · <a href="#newsletter" class="follow">Follow</a>
                    </div>

                    <div style="font-size: 14px;" id="readTime">
                        {self.read_time} · {self.post_date}
                    </div>
                </div>
            </div>'''
        html+=f'''<div class="blog-reaction-div">
                <div class="blog-reaction">
                    <div>
                        <svg width="24" height="24" viewBox="0 0 24 24" aria-label="clap"><path fill-rule="evenodd" fill="currentColor" clip-rule="evenodd" d="M11.37.83L12 3.28l.63-2.45h-1.26zM13.92 3.95l1.52-2.1-1.18-.4-.34 2.5zM8.59 1.84l1.52 2.11-.34-2.5-1.18.4zM18.52 18.92a4.23 4.23 0 0 1-2.62 1.33l.41-.37c2.39-2.4 2.86-4.95 1.4-7.63l-.91-1.6-.8-1.67c-.25-.56-.19-.98.21-1.29a.7.7 0 0 1 .55-.13c.28.05.54.23.72.5l2.37 4.16c.97 1.62 1.14 4.23-1.33 6.7zm-11-.44l-4.15-4.15a.83.83 0 0 1 1.17-1.17l2.16 2.16a.37.37 0 0 0 .51-.52l-2.15-2.16L3.6 11.2a.83.83 0 0 1 1.17-1.17l3.43 3.44a.36.36 0 0 0 .52 0 .36.36 0 0 0 0-.52L5.29 9.51l-.97-.97a.83.83 0 0 1 0-1.16.84.84 0 0 1 1.17 0l.97.97 3.44 3.43a.36.36 0 0 0 .51 0 .37.37 0 0 0 0-.52L6.98 7.83a.82.82 0 0 1-.18-.9.82.82 0 0 1 .76-.51c.22 0 .43.09.58.24l5.8 5.79a.37.37 0 0 0 .58-.42L13.4 9.67c-.26-.56-.2-.98.2-1.29a.7.7 0 0 1 .55-.13c.28.05.55.23.73.5l2.2 3.86c1.3 2.38.87 4.59-1.29 6.75a4.65 4.65 0 0 1-4.19 1.37 7.73 7.73 0 0 1-4.07-2.25zm3.23-12.5l2.12 2.11c-.41.5-.47 1.17-.13 1.9l.22.46-3.52-3.53a.81.81 0 0 1-.1-.36c0-.23.09-.43.24-.59a.85.85 0 0 1 1.17 0zm7.36 1.7a1.86 1.86 0 0 0-1.23-.84 1.44 1.44 0 0 0-1.12.27c-.3.24-.5.55-.58.89-.25-.25-.57-.4-.91-.47-.28-.04-.56 0-.82.1l-2.18-2.18a1.56 1.56 0 0 0-2.2 0c-.2.2-.33.44-.4.7a1.56 1.56 0 0 0-2.63.75 1.6 1.6 0 0 0-2.23-.04 1.56 1.56 0 0 0 0 2.2c-.24.1-.5.24-.72.45a1.56 1.56 0 0 0 0 2.2l.52.52a1.56 1.56 0 0 0-.75 2.61L7 19a8.46 8.46 0 0 0 4.48 2.45 5.18 5.18 0 0 0 3.36-.5 4.89 4.89 0 0 0 4.2-1.51c2.75-2.77 2.54-5.74 1.43-7.59L18.1 7.68z"></path></svg>
                    </div>
                    <div>{self.reactions['claps']}</div>
                    <div style="margin-left: 16px;">
                        <svg width="24" height="24" viewBox="0 0 24 24" class="jp"><path d="M18 16.8a7.14 7.14 0 0 0 2.24-5.32c0-4.12-3.53-7.48-8.05-7.48C7.67 4 4 7.36 4 11.48c0 4.13 3.67 7.48 8.2 7.48a8.9 8.9 0 0 0 2.38-.32c.23.2.48.39.75.56 1.06.69 2.2 1.04 3.4 1.04.22 0 .4-.11.48-.29a.5.5 0 0 0-.04-.52 6.4 6.4 0 0 1-1.16-2.65v.02zm-3.12 1.06l-.06-.22-.32.1a8 8 0 0 1-2.3.33c-4.03 0-7.3-2.96-7.3-6.59S8.17 4.9 12.2 4.9c4 0 7.1 2.96 7.1 6.6 0 1.8-.6 3.47-2.02 4.72l-.2.16v.26l.02.3a6.74 6.74 0 0 0 .88 2.4 5.27 5.27 0 0 1-2.17-.86c-.28-.17-.72-.38-.94-.59l.01-.02z"></path></svg>
                    </div>
                    <div>{self.reactions['Responds']}</div>
                </div>
                <div class="blog-save-share">
                    <div id="speak-nav">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path fill-rule="evenodd" clip-rule="evenodd" d="M3 12a9 9 0 1 1 18 0 9 9 0 0 1-18 0zm9-10a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm3.38 10.42l-4.6 3.06a.5.5 0 0 1-.78-.41V8.93c0-.4.45-.63.78-.41l4.6 3.06c.3.2.3.64 0 .84z" fill="currentColor"></path></svg>
                    </div>
                    <div id="share-nav">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path fill-rule="evenodd" clip-rule="evenodd" d="M15.22 4.93a.42.42 0 0 1-.12.13h.01a.45.45 0 0 1-.29.08.52.52 0 0 1-.3-.13L12.5 3v7.07a.5.5 0 0 1-.5.5.5.5 0 0 1-.5-.5V3.02l-2 2a.45.45 0 0 1-.57.04h-.02a.4.4 0 0 1-.16-.3.4.4 0 0 1 .1-.32l2.8-2.8a.5.5 0 0 1 .7 0l2.8 2.8a.42.42 0 0 1 .07.5zm-.1.14zm.88 2h1.5a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-11a2 2 0 0 1-2-2v-10a2 2 0 0 1 2-2H8a.5.5 0 0 1 .35.14c.1.1.15.22.15.35a.5.5 0 0 1-.15.35.5.5 0 0 1-.35.15H6.4c-.5 0-.9.4-.9.9v10.2a.9.9 0 0 0 .9.9h11.2c.5 0 .9-.4.9-.9V8.96c0-.5-.4-.9-.9-.9H16a.5.5 0 0 1 0-1z" fill="currentColor"></path></svg>
                    </div>
                </div>
            </div>'''
        return html
    def getFooterHTML(self):
        # {''.join([f'<a href="/tag/{get_url_by_name(i)}">{i}</a>' for i in self.tags])}
        html = f'''<div class="tags" id="tag-footer">
                {''.join([f'<a href="/tag/{get_url_by_name(i)}">{i}</a>' for i in self.tags])}
            </div>'''
        html += f'''<div class="blog-reaction-div" id="reaction-footer" style="border:none">
                <div class="blog-reaction">
                    <div>
                        <svg width="24" height="24" viewBox="0 0 24 24" aria-label="clap"><path fill-rule="evenodd" fill="currentColor" clip-rule="evenodd" d="M11.37.83L12 3.28l.63-2.45h-1.26zM13.92 3.95l1.52-2.1-1.18-.4-.34 2.5zM8.59 1.84l1.52 2.11-.34-2.5-1.18.4zM18.52 18.92a4.23 4.23 0 0 1-2.62 1.33l.41-.37c2.39-2.4 2.86-4.95 1.4-7.63l-.91-1.6-.8-1.67c-.25-.56-.19-.98.21-1.29a.7.7 0 0 1 .55-.13c.28.05.54.23.72.5l2.37 4.16c.97 1.62 1.14 4.23-1.33 6.7zm-11-.44l-4.15-4.15a.83.83 0 0 1 1.17-1.17l2.16 2.16a.37.37 0 0 0 .51-.52l-2.15-2.16L3.6 11.2a.83.83 0 0 1 1.17-1.17l3.43 3.44a.36.36 0 0 0 .52 0 .36.36 0 0 0 0-.52L5.29 9.51l-.97-.97a.83.83 0 0 1 0-1.16.84.84 0 0 1 1.17 0l.97.97 3.44 3.43a.36.36 0 0 0 .51 0 .37.37 0 0 0 0-.52L6.98 7.83a.82.82 0 0 1-.18-.9.82.82 0 0 1 .76-.51c.22 0 .43.09.58.24l5.8 5.79a.37.37 0 0 0 .58-.42L13.4 9.67c-.26-.56-.2-.98.2-1.29a.7.7 0 0 1 .55-.13c.28.05.55.23.73.5l2.2 3.86c1.3 2.38.87 4.59-1.29 6.75a4.65 4.65 0 0 1-4.19 1.37 7.73 7.73 0 0 1-4.07-2.25zm3.23-12.5l2.12 2.11c-.41.5-.47 1.17-.13 1.9l.22.46-3.52-3.53a.81.81 0 0 1-.1-.36c0-.23.09-.43.24-.59a.85.85 0 0 1 1.17 0zm7.36 1.7a1.86 1.86 0 0 0-1.23-.84 1.44 1.44 0 0 0-1.12.27c-.3.24-.5.55-.58.89-.25-.25-.57-.4-.91-.47-.28-.04-.56 0-.82.1l-2.18-2.18a1.56 1.56 0 0 0-2.2 0c-.2.2-.33.44-.4.7a1.56 1.56 0 0 0-2.63.75 1.6 1.6 0 0 0-2.23-.04 1.56 1.56 0 0 0 0 2.2c-.24.1-.5.24-.72.45a1.56 1.56 0 0 0 0 2.2l.52.52a1.56 1.56 0 0 0-.75 2.61L7 19a8.46 8.46 0 0 0 4.48 2.45 5.18 5.18 0 0 0 3.36-.5 4.89 4.89 0 0 0 4.2-1.51c2.75-2.77 2.54-5.74 1.43-7.59L18.1 7.68z"></path></svg>
                    </div>
                    <div>{self.reactions['claps']}</div>
                    <div style="margin-left: 16px;">
                        <svg width="24" height="24" viewBox="0 0 24 24" class="jp"><path d="M18 16.8a7.14 7.14 0 0 0 2.24-5.32c0-4.12-3.53-7.48-8.05-7.48C7.67 4 4 7.36 4 11.48c0 4.13 3.67 7.48 8.2 7.48a8.9 8.9 0 0 0 2.38-.32c.23.2.48.39.75.56 1.06.69 2.2 1.04 3.4 1.04.22 0 .4-.11.48-.29a.5.5 0 0 0-.04-.52 6.4 6.4 0 0 1-1.16-2.65v.02zm-3.12 1.06l-.06-.22-.32.1a8 8 0 0 1-2.3.33c-4.03 0-7.3-2.96-7.3-6.59S8.17 4.9 12.2 4.9c4 0 7.1 2.96 7.1 6.6 0 1.8-.6 3.47-2.02 4.72l-.2.16v.26l.02.3a6.74 6.74 0 0 0 .88 2.4 5.27 5.27 0 0 1-2.17-.86c-.28-.17-.72-.38-.94-.59l.01-.02z"></path></svg>
                    </div>
                    <div>{self.reactions['Responds']}</div>
                </div>
                <div class="blog-save-share">
                    <div id="share-footer">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path fill-rule="evenodd" clip-rule="evenodd" d="M15.22 4.93a.42.42 0 0 1-.12.13h.01a.45.45 0 0 1-.29.08.52.52 0 0 1-.3-.13L12.5 3v7.07a.5.5 0 0 1-.5.5.5.5 0 0 1-.5-.5V3.02l-2 2a.45.45 0 0 1-.57.04h-.02a.4.4 0 0 1-.16-.3.4.4 0 0 1 .1-.32l2.8-2.8a.5.5 0 0 1 .7 0l2.8 2.8a.42.42 0 0 1 .07.5zm-.1.14zm.88 2h1.5a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-11a2 2 0 0 1-2-2v-10a2 2 0 0 1 2-2H8a.5.5 0 0 1 .35.14c.1.1.15.22.15.35a.5.5 0 0 1-.15.35.5.5 0 0 1-.35.15H6.4c-.5 0-.9.4-.9.9v10.2a.9.9 0 0 0 .9.9h11.2c.5 0 .9-.4.9-.9V8.96c0-.5-.4-.9-.9-.9H16a.5.5 0 0 1 0-1z" fill="currentColor"></path></svg>
                    </div>
                </div>
            </div>'''
        return html
    def getRootFooterHTML(self):
        html = f'''<div class="writer">
            <div class="writer-img">
                <img alt="{self.user}" src="/static/userPNG/{self.userPNG}" width="72" height="72" loading="lazy">
            </div>
            <div style="display: flex;flex-wrap: wrap; flex-direction: column;">
                <div style="padding-bottom: 1rem;">
                    <h2>Written by {self.user}</h2>
                    <div style="margin-bottom:8px;">
                        <a href="">{self.userFollowers} Followers</a>
                    </div>
                    <p>
                        {self.userDescription}
                    </p>
                </div>
                <div class="newsletter" id="newsletter">
                    <h2>Sign up for my newsletter</h2>
                    <p>Get notified when I post a new article. Unsubscribe at any time, and I promise not to send any spam :)</p>
                    <form action="https://formspree.io/f/mbjnelqe" method="POST">
                    <input type="email" id="email" name="EMAIL" autocomplete="email" required="" placeholder="Your email">
                    <button style="padding: 0px;" type="submit">
                        <div style="display:flex; align-items: center; padding: 4px 8px;">
                        Follow
                        <svg width="38" height="38" viewBox="0 0 38 38" fill="none" style="stroke: rgb(255, 255, 255);width: 36px;height: 36px;"><rect x="26.25" y="9.25" width="0.5" height="6.5" rx="0.25"></rect><rect x="29.75" y="12.25" width="0.5" height="6.5" rx="0.25" transform="rotate(90 29.75 12.25)"></rect><path d="M19.5 12.5h-7a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h13a1 1 0 0 0 1-1v-5"></path><path d="M11.5 14.5L19 20l4-3"></path></svg>
                        </div>
                    </button>
                    </form>
                </div>
            </div>
        </div>'''
        return html
    
    def img(self, src, figCaption:str=None, fullWidth:bool=False) -> None: # full width not supported yet
        # if fullWidth:
        #     self.data+=f'''<div style="margin-bottom: 50%;">
        #                         <div style="position: absolute; left: 0;"></div>
        #                     </div>'''
        self.data+=f'<img alt=""  width="100%"  loading="eager" role="presentation" src="{src}">'
        if figCaption:
            self.data+=f'<figcaption>{figCaption}</figcaption>'    
    def h(self, title, h_i=2):
        self.data+=f'<h{h_i}>{title}</h{h_i}>'
    def p(self, data):
        self.data+=f'<p>{data}</p>'
    
    def add(self, html): self.data+=html
    
    def __repr__(self) -> str: return self.html
