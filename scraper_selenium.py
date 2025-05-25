import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pdfkit

# Configuration
REFERENCE_PAGE = "https://www.patreon.com/posts/frequently-asked-43097481"
OUTPUT_DIR = "output"

# !!! IMPORTANT: UPDATE THIS PATH !!!
# Find the path to your wkhtmltopdf.exe installation
# Example: WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def setup_driver():
    """Set up and return a Selenium webdriver"""
    print("Setting up Chrome webdriver...")
    
    # Configure Chrome options
    options = Options()
    # Uncomment the line below to run in headless mode (no browser window)
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Initialize Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def get_post_links(driver, reference_url):
    """Get all post links from the reference page using Selenium"""
    print(f"Fetching links from: {reference_url}")
    
    try:
        # Navigate to the reference page
        driver.get(reference_url)
        
        # Wait for Cloudflare challenge to resolve (may need to adjust time)
        print("Waiting for page to load and Cloudflare to resolve...")
        time.sleep(10)
        
        # Wait for the main content to load
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
        except Exception as e:
            print(f"Error waiting for page to load: {str(e)}")
        
        # Save the page source for debugging
        with open(os.path.join(OUTPUT_DIR, "reference_page.html"), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"Saved reference page HTML for inspection to {os.path.join(OUTPUT_DIR, 'reference_page.html')}")
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
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

def fetch_post_content(driver, url):
    """Fetch post content using Selenium"""
    print(f"Fetching content from: {url}")
    
    # Add delay to avoid rate limiting
    time.sleep(random.uniform(2, 5))
    
    try:
        # Navigate to the post URL
        driver.get(url)
        
        # Wait for Cloudflare challenge to resolve (may need to adjust time)
        print("Waiting for page to load and Cloudflare to resolve...")
        time.sleep(10)
        
        # Wait for the main content to load
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "div"))
            )
        except Exception as e:
            print(f"Error waiting for page to load: {str(e)}")
        
        # Save the HTML for debugging
        page_name = url.split('/')[-1]
        html_filename = f"{page_name}.html"
        with open(os.path.join(OUTPUT_DIR, html_filename), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"Saved post HTML for inspection to {os.path.join(OUTPUT_DIR, html_filename)}")
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
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

def sanitize_filename(filename):
    """Remove or replace characters that are invalid in Windows filenames."""
    # Characters to remove/replace: \ / : * ? " < > |
    # Replace / with - (already done in title extraction, but good to be safe)
    # Replace others with _ or remove them
    
    # Remove leading/trailing whitespace
    filename = filename.strip()
    
    # Replace problematic characters
    filename = filename.replace('|', '_')
    filename = filename.replace(':', '_')
    filename = filename.replace('?', '') # Often removed
    filename = filename.replace('*', '')
    filename = filename.replace('<', '_')
    filename = filename.replace('>', '_')
    filename = filename.replace('"', "'") # Replace double quotes with single
    filename = filename.replace('\\', '_') # Replace backslash
    filename = filename.replace('/', '-')   # Ensure forward slash is also handled
    
    # Limit filename length (common practice, though OS limits are usually higher)
    # Taking into account the .html or .pdf extension
    max_len = 250 # A bit less than typical max path component length
    if len(filename) > max_len - 5: # -5 for .html or .pdf
        filename = filename[:max_len - 5]
        
    return filename

def save_pdf(title, html_content):
    """Save HTML content as PDF"""
    if not html_content:
        print("No HTML content to save")
        return
    
    sanitized_title = sanitize_filename(title)
    
    # Save the HTML file first for inspection
    html_filename = f"{sanitized_title[:50]}.html" # Use sanitized_title
    html_path = os.path.join(OUTPUT_DIR, html_filename)
    
    try: # Add try-except for file writing
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved HTML to: {html_path}")
    except Exception as e:
        print(f"Error saving HTML file {html_path}: {str(e)}")
        return # Don't proceed to PDF if HTML saving failed

    # Now convert to PDF
    pdf_filename = f"{sanitized_title[:50]}.pdf" # Use sanitized_title
    output_path = os.path.join(OUTPUT_DIR, pdf_filename)
    print(f"Saving PDF to: {output_path}")
    
    try:
        # Pass the configuration to pdfkit
        config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
        pdfkit.from_string(html_content, output_path, configuration=config)
        print("PDF saved successfully")
    except Exception as e:
        print(f"Error saving PDF: {str(e)}")
        print("You may need to install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")

def main():
    try:
        # Set up Selenium webdriver
        driver = setup_driver()
        
        try:
            # Get all post links
            links = get_post_links(driver, REFERENCE_PAGE)
            if not links:
                print("No links found. Exiting.")
                return
                
            # Process each link
            for i, link in enumerate(links):
                print(f"\nProcessing link {i+1}/{len(links)}: {link}")
                try:
                    title, content = fetch_post_content(driver, link)
                    if title and content:
                        print(f"Saving: {title}")
                        save_pdf(title, content)
                    else:
                        print("Missing title or content, skipping...")
                except Exception as e:
                    print(f"Error processing link {link}: {str(e)}")
                    continue
        finally:
            # Always close the driver to free resources
            print("Closing webdriver...")
            driver.quit()
            
    except Exception as e:
        print(f"Main error: {str(e)}")

if __name__ == "__main__":
    main() 