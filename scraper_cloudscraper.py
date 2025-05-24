import os
import time
import random
import cloudscraper
from bs4 import BeautifulSoup
import pdfkit

# Configuration
REFERENCE_PAGE = "https://www.patreon.com/posts/frequently-asked-43097481"
OUTPUT_DIR = "output"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_post_links(reference_url):
    """Get all post links from the reference page using cloudscraper"""
    print(f"Fetching links from: {reference_url}")
    
    try:
        # Create a cloudscraper session
        scraper = cloudscraper.create_scraper(delay=10, browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        })
        
        # Get the page content
        resp = scraper.get(reference_url)
        print(f"Response status code: {resp.status_code}")
        
        # Save the HTML for inspection
        with open(os.path.join(OUTPUT_DIR, "reference_page.html"), "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"Saved reference page HTML for inspection to {os.path.join(OUTPUT_DIR, 'reference_page.html')}")
        
        if resp.status_code != 200:
            print(f"Failed to fetch reference page: {resp.status_code}")
            print(f"Response: {resp.text[:500]}...")
            return []
            
        # Parse the HTML
        soup = BeautifulSoup(resp.content, "html.parser")
        links = []
        
        # Extract all Patreon post links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "patreon.com/posts/" in href:
                links.append(href)
        
        # Deduplicate links
        unique_links = list(set(links))
        print(f"Found {len(unique_links)} unique post links")
        return unique_links
        
    except Exception as e:
        print(f"Error fetching post links: {str(e)}")
        return []

def fetch_post_content(url, scraper=None):
    """Fetch post content using cloudscraper"""
    print(f"Fetching content from: {url}")
    
    # Add delay to avoid rate limiting
    time.sleep(random.uniform(2, 5))
    
    try:
        # Create a new scraper if one wasn't provided
        if not scraper:
            scraper = cloudscraper.create_scraper(delay=10, browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            })
        
        # Get the page content
        resp = scraper.get(url)
        print(f"Response status code: {resp.status_code}")
        
        # Save the HTML for inspection
        page_name = url.split('/')[-1]
        html_filename = f"{page_name}.html"
        with open(os.path.join(OUTPUT_DIR, html_filename), "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"Saved post HTML for inspection to {os.path.join(OUTPUT_DIR, html_filename)}")
        
        if resp.status_code != 200:
            print(f"Failed to fetch post: {resp.status_code}")
            return None, None
            
        # Parse the HTML
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Print a sample of div classes to help identify the content
        print("Sample of HTML classes in the page:")
        for i, div in enumerate(soup.find_all("div", class_=True)):
            if i < 10:  # Only print first 10 classes
                print(f"Found div with class: {div.get('class', '')}")
            else:
                break
        
        # Try multiple selectors that might contain the main content
        selectors = [
            {"class_": "sc-2ee9b62c-0 emBANY"},  # Original selector
            {"class_": "sc-"},  # Any div with class starting with sc-
            {"data-tag": "post-content"},  # Using data-tag
            {"class_": "post-content"},  # Common class for post content
            {"class_": "post"},  # Common class for post content
            {"id": "content"}  # Common id for content
        ]
        
        main_content = None
        for selector in selectors:
            # Create keyword arguments for the find method
            kwargs = {}
            for key, value in selector.items():
                if key == "class_":
                    kwargs["class_"] = value
                else:
                    kwargs[key] = value
            
            found = soup.find("div", **kwargs)
            if found:
                main_content = found
                print(f"Found content with selector: {selector}")
                break
        
        print(f"Main content found: {main_content is not None}")
        
        if not main_content:
            # If all else fails, try to get the largest div by content length
            print("Trying to find the largest content div...")
            divs = soup.find_all("div")
            largest_div = None
            max_length = 0
            
            for div in divs:
                text_length = len(div.get_text(strip=True))
                if text_length > max_length:
                    max_length = text_length
                    largest_div = div
            
            if largest_div and max_length > 100:  # Ensure it has meaningful content
                main_content = largest_div
                print(f"Found largest div with text length: {max_length}")
        
        if not main_content:
            print("Could not find any suitable content div")
            return None, None
        
        post_text = main_content.get_text(strip=True) if main_content else ""
        print(f"Post text length: {len(post_text)}")
        
        if not post_text:
            print("Found post content div but it contains no text")
            return None, None
            
        title = soup.title.text.strip().replace("/", "-") if soup.title else "Untitled Post"
        print(f"Post title: {title}")
        
        # Add some basic styling to make the PDF look better
        styled_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                h1, h2, h3 {{ color: #333; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            {str(main_content)}
        </body>
        </html>
        """
        
        return title, styled_html
        
    except Exception as e:
        print(f"Error processing content: {str(e)}")
        return None, None

def save_pdf(title, html_content):
    """Save HTML content as PDF"""
    if not html_content:
        print("No HTML content to save")
        return
    
    # Save the HTML file first for inspection
    html_filename = f"{title[:50]}.html"
    html_path = os.path.join(OUTPUT_DIR, html_filename)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved HTML to: {html_path}")
    
    # Now convert to PDF
    filename = f"{title[:50]}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)
    print(f"Saving PDF to: {output_path}")
    
    try:
        pdfkit.from_string(html_content, output_path)
        print("PDF saved successfully")
    except Exception as e:
        print(f"Error saving PDF: {str(e)}")
        print("You may need to install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")

def main():
    try:
        # Create a cloudscraper session to reuse across requests
        scraper = cloudscraper.create_scraper(delay=10, browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        })
        
        # Get all post links
        links = get_post_links(REFERENCE_PAGE)
        if not links:
            print("No links found. Exiting.")
            return
            
        # Process each link
        for i, link in enumerate(links):
            print(f"\nProcessing link {i+1}/{len(links)}: {link}")
            try:
                title, content = fetch_post_content(link, scraper)
                if title and content:
                    print(f"Saving: {title}")
                    save_pdf(title, content)
                else:
                    print("Missing title or content, skipping...")
            except Exception as e:
                print(f"Error processing link {link}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Main error: {str(e)}")

if __name__ == "__main__":
    main() 