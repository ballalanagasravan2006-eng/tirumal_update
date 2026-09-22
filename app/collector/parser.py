import re
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

def parse_ttd_article(url: str, html_content: str) -> dict:
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract Title
    title = ""
    title_te = ""

    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)

    # Check if title has English and Telugu components (separated by -_- or | or ::)
    if "-_-" in title:
        parts = title.split("-_-")
        title = parts[0].strip()
        title_te = parts[1].strip() if len(parts) > 1 else ""
    elif "|" in title:
        parts = title.split("|")
        title = parts[0].strip()

    # Extract Published Date
    published_date = None
    time_tag = soup.find("time")
    if time_tag:
        published_date = time_tag.get("datetime") or time_tag.get_text(strip=True)
    
    if not published_date:
        date_meta = soup.find("meta", property="article:published_time")
        if date_meta:
            published_date = date_meta.get("content")

    # Extract Category
    category = "TTD Announcements"
    cat_tag = soup.find("a", href=re.compile(r"/category/"))
    if cat_tag:
        category = cat_tag.get_text(strip=True)

    # Extract Main Article Body
    article_text = ""
    entry_content = soup.find(class_=re.compile(r"entry-content|post-content|article-content|content"))
    if entry_content:
        paragraphs = entry_content.find_all("p")
        article_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    else:
        paragraphs = soup.find_all("p")
        article_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

    raw_excerpt = article_text[:250] + "..." if len(article_text) > 250 else article_text

    # Extract Images
    images = []
    og_img = soup.find("meta", property="og:image")
    if og_img and og_img.get("content"):
        images.append(urljoin(url, og_img["content"]))

    target_area = entry_content if entry_content else soup
    for img in target_area.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and not src.endswith(".svg") and "avatar" not in src:
            abs_url = urljoin(url, src)
            if abs_url not in images:
                images.append(abs_url)

    # Extract Videos
    videos = []
    for iframe in target_area.find_all("iframe"):
        src = iframe.get("src")
        if src and ("youtube" in src or "vimeo" in src or "svbc" in src):
            videos.append(urljoin(url, src))

    for video_tag in target_area.find_all("video"):
        src = video_tag.get("src")
        if src:
            videos.append(urljoin(url, src))
        for source_tag in video_tag.find_all("source"):
            if source_tag.get("src"):
                videos.append(urljoin(url, source_tag["src"]))

    # Content Hash
    hash_input = f"{title}||{article_text}".encode("utf-8")
    content_hash = hashlib.sha256(hash_input).hexdigest()

    return {
        "title": title,
        "title_te": title_te,
        "published_date": published_date,
        "category": category,
        "source_url": url,
        "article_text": article_text,
        "raw_excerpt": raw_excerpt,
        "content_hash": content_hash,
        "images": images,
        "videos": videos
    }
