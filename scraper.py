import os
import requests
from bs4 import BeautifulSoup
import pdfkit

REFERENCE_PAGE = "https://www.patreon.com/posts/frequently-asked-43097481"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_post_links(reference_url):
    resp = requests.get(reference_url)
    soup = BeautifulSoup(resp.content, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "patreon.com/posts/" in href:
            links.append(href)
    return list(set(links))  # deduplicate

def fetch_post_content(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    # You may need to adjust the selector below based on Patreon’s HTML structure
    main_content = soup.find("div", class_="sc-cvbbAY")  # Example class; inspect and update!
    if not main_content:
        return None, None
    title = soup.title.text.strip().replace("/", "-")
    return title, str(main_content)

def save_pdf(title, html_content):
    if not html_content:
        return
    filename = f"{title[:50]}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)
    pdfkit.from_string(html_content, output_path)

def main():
    links = get_post_links(REFERENCE_PAGE)
    for link in links:
        title, content = fetch_post_content(link)
        if title and content:
            print(f"Saving: {title}")
            save_pdf(title, content)

if __name__ == "__main__":
    main()
