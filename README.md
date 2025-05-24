# Patreon Blog Post Scraper

A Python bot that scrapes public posts from a Patreon blog and saves each post as a formatted PDF. This tool is designed to help you collect, archive, and later summarize or study Patreon blog content by uploading the resulting PDFs to an LLM chat or note-taking tool.

## Current Status

**NOTE: This script currently encounters a Cloudflare protection challenge when trying to access Patreon. The simple requests-based approach is not sufficient for bypassing this protection.**

## Features

- Scrapes post links from a specified Patreon index/reference page.
- Downloads the content of each public post (text and images, with formatting).
- Generates a separate PDF for each post, preserving formatting and optionally including images.
- Skips comments to keep PDFs clean and focused.

## Use Case

Ideal for students, researchers, or creators who want to archive Patreon blog content for offline reading, study, or summarization with AI tools.

## How It Works

1. The bot fetches the reference page containing links to Patreon posts.
2. It extracts all post URLs from this page.
3. For each post, it downloads and parses the main content.
4. The content is saved as a PDF file (with formatting and images).
5. PDFs are stored in a designated output folder.

## Requirements

- Python 3.7+
- [requests](https://pypi.org/project/requests/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [pdfkit](https://pypi.org/project/pdfkit/) (requires [wkhtmltopdf](https://wkhtmltopdf.org/))
  - Alternative: [fpdf2](https://pypi.org/project/fpdf2/) or [reportlab](https://pypi.org/project/reportlab/)

## Dealing with Cloudflare Protection

Patreon uses Cloudflare to protect against automated scrapers. To bypass this protection, you'd need to:

1. **Use a headless browser**: Replace the simple `requests` approach with Selenium or Playwright which can execute JavaScript and solve Cloudflare challenges
2. **Consider the API**: Check if Patreon offers an official API for accessing content
3. **Use specialized libraries**: Libraries like `cloudscraper` are designed specifically to bypass Cloudflare, but success may vary

### Option 1: Using Selenium (Recommended for Learning)

To install Selenium and continue with this approach:

```bash
pip install selenium webdriver-manager
```

You would then modify the script to use Selenium instead of requests. Example:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Setup browser
options = Options()
options.add_argument("--headless")  # Run without opening a window
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Visit page
driver.get(REFERENCE_PAGE)
# Wait for Cloudflare to resolve
time.sleep(10)  # Adjust as needed

# Now the page should be loaded
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
# Continue with your scraping logic...
```

## Installation

```bash
git clone https://github.com/giovanni2398/blog-post-scraper.git
cd blog-post-scraper
pip install -r requirements.txt
```

Make sure to install `wkhtmltopdf` if you use `pdfkit` (see [instructions](https://wkhtmltopdf.org/downloads.html)).

## Usage

Edit the script to set your reference page URL, e.g.:

```python
REFERENCE_PAGE = "https://www.patreon.com/posts/frequently-asked-43097481"
```

Then run:

```bash
python scraper.py
```

All PDFs will be saved in the `output` directory (or as specified).

## Configuration

- **REFERENCE_PAGE**: URL of the Patreon page containing links to blog posts.
- **OUTPUT_DIR**: Directory to save PDF files.

## Example

The following reference page is supported:

- https://www.patreon.com/posts/frequently-asked-43097481

## License

MIT License

## Disclaimer

- Only works with public Patreon posts.
- For personal or educational use. Please respect content creators' terms and Patreon's policies.
- Web scraping may violate terms of service. Use responsibly and consider official APIs when available.
- This script is for educational purposes to demonstrate web scraping techniques.
