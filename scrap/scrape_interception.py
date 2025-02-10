import hashlib
import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def clean_text_per_line(text):
    """
    Cleans text on a per‑line basis:
      - Splits the text into lines.
      - Strips leading/trailing whitespace from each line.
      - Discards empty lines.
    Returns the joined lines.
    """
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(cleaned_lines)


def scrape_page_content(page):
    """
    Gets the HTML content of the current page, parses it with BeautifulSoup,
    extracts the visible text, and cleans it.
    """
    html_content = page.content()
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return clean_text_per_line(text)


def get_page_hash(page):
    """
    Returns a SHA-256 hash of the current page's HTML content.
    This is used to detect if the page content has changed.
    """
    html_content = page.content()
    return hashlib.sha256(html_content.encode("utf-8")).hexdigest()


def main():
    with sync_playwright() as p:
        # Launch Chromium in headful mode so you can manually navigate.
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        start_url = input("Enter the URL to scrape: ").strip()
        page.goto(start_url)
        page.wait_for_load_state("networkidle")

        # Set to keep track of page content hashes already scraped.
        scraped_hashes = set()
        last_hash = None

        print("\nNow monitoring the page for content changes.")
        print(
            "You can manually navigate or click on pagination links in the browser window."
        )
        print(
            "Any new content will be scraped and printed below. Press Ctrl+C to exit.\n"
        )

        try:
            while True:
                # Wait briefly before checking for changes.
                time.sleep(2)
                current_hash = get_page_hash(page)
                # If the page content has changed compared to last check
                if current_hash != last_hash:
                    # And if we haven't already scraped this version:
                    if current_hash not in scraped_hashes:
                        print(
                            "\n--- New Content Detected at URL: {} ---".format(page.url)
                        )
                        content = scrape_page_content(page)
                        print(content)
                        scraped_hashes.add(current_hash)
                    else:
                        print("\nContent already scraped, skipping...")
                    last_hash = current_hash
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
