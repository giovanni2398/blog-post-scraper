# Patreon Blog Post Scraper

A Python bot that scrapes public posts from a Patreon blog and saves each post as a formatted PDF. This tool uses Selenium to drive a web browser, allowing it to handle dynamic content and bypass anti-scraping measures like Cloudflare challenges. The scraped PDFs can then be optionally merged into a single document.

This tool is designed to help you collect, archive, and later summarize or study Patreon blog content, for example, by uploading the resulting PDFs to an LLM chat or a note-taking application.

## Features

- Uses Selenium to reliably scrape content from Patreon, handling JavaScript and Cloudflare.
- Scrapes post links from a specified Patreon index/reference page.
- Downloads the content of each public post (text and basic formatting).
- Generates a separate PDF for each post.
- Includes a separate script (`merge-pdfs.py`) to combine all generated PDFs into one file.

## How It Works

1. **`scraper_selenium.py`**:
   - Initializes a Selenium-controlled web browser (Chrome).
   - Navigates to the specified Patreon `REFERENCE_PAGE`.
   - Waits for the page to load (including any Cloudflare challenges) and extracts all individual post URLs.
   - For each post URL:
     - Navigates to the post.
     - Waits for content to load.
     - Extracts the main post content and title.
     - Sanitizes the title to create a valid filename.
     - Saves the post content as an HTML file (for debugging/inspection) and then converts it to a PDF using `pdfkit`.
   - PDFs are stored in the `OUTPUT_DIR` (default: `output/`).
2. **`merge-pdfs.py`** (Optional):
   - Scans the `OUTPUT_DIR` for all `.pdf` files.
   - Merges them into a single PDF file (default: `merged_output.pdf`).

## Requirements

- Python 3.7+
- Google Chrome browser installed.
- **wkhtmltopdf**: This is crucial for PDF generation. You must install it and ensure the script can find the executable.
  - Download from [wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html).
  - After installation, you **must** update the `WKHTMLTOPDF_PATH` variable in `scraper_selenium.py` with the full path to `wkhtmltopdf.exe` (e.g., `r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"`).

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/giovanni2398/blog-post-scraper.git
   cd blog-post-scraper
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   This will install `selenium`, `webdriver-manager`, `beautifulsoup4`, `pdfkit`, and `pypdf`.

3. **Install wkhtmltopdf:**

   - Download and install `wkhtmltopdf` from [wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html).

4. **Configure `scraper_selenium.py`:**

   - Open `scraper_selenium.py`.
   - Locate the `WKHTMLTOPDF_PATH` variable near the top of the file.
   - Update its value with the full path to your `wkhtmltopdf.exe` installation. For example:

     ```python
     WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
     ```

   - Optionally, change the `REFERENCE_PAGE` URL to the Patreon page you want to scrape.

## Usage

1. **Run the scraper:**

   ```bash
   python scraper_selenium.py
   ```

   This will open a Chrome browser window (unless configured for headless mode) and start scraping. PDFs will be saved in the `output/` directory.

2. **Merge PDFs (Optional):**
   After the scraper has finished and generated individual PDFs, you can merge them:

   ```bash
   python merge-pdfs.py
   ```

   This will create `merged_output.pdf` in the project's root directory.

## Configuration (in `scraper_selenium.py`)

- **`REFERENCE_PAGE`**: URL of the Patreon page containing links to the blog posts you want to scrape (e.g., an archive page or a tag page).
- **`OUTPUT_DIR`**: Directory where the individual PDF files will be saved (default: `"output"`).
- **`WKHTMLTOPDF_PATH`**: **Crucial.** The full path to your `wkhtmltopdf.exe` executable.

## Troubleshooting

- **`No wkhtmltopdf executable found` error:** Ensure `wkhtmltopdf` is installed and the `WKHTMLTOPDF_PATH` in `scraper_selenium.py` is set correctly to the _full path_ of `wkhtmltopdf.exe`.
- **Cloudflare issues / No content found:** Selenium should handle most Cloudflare challenges. If issues persist, the Patreon site structure might have changed, or anti-scraping measures might have become more aggressive. The `time.sleep()` values in the script might need adjustment for slower connections or more complex pages.
- **Invalid filenames:** The script attempts to sanitize filenames by removing characters like `|`, `/`, `\`, etc. If you still encounter filename errors, further sanitization logic might be needed in the `sanitize_filename` function.
- **Selenium WebDriver errors:** `webdriver-manager` should automatically download and manage ChromeDriver. If you see errors related to ChromeDriver, ensure you have an internet connection when running the script for the first time, or check for compatibility issues between your Chrome browser version and ChromeDriver.

## Disclaimer

- This tool is intended for personal, educational, or research purposes only.
- Always respect content creators' terms of service and Patreon's policies. Consider supporting creators directly on Patreon.
- Web scraping can be a legally gray area and may violate the terms of service of websites. Use this tool responsibly and at your own risk.
- The effectiveness of this scraper depends on the structure of Patreon's website, which can change. If the script stops working, it may need updates to adapt to new site structures or anti-scraping measures.

## License

MIT License (Refer to `LICENSE` file for details).
