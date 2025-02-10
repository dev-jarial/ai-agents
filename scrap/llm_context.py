# scrape the all possile html, that able to load on the browser and also depth crawling, uses shrink the
# context to save the tokens and process data fast for chatbot etc.

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_internal_links(url, html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    internal_links = set()
    base_domain = urlparse(url).netloc

    # Extract links from <a> tags
    for anchor in soup.find_all("a", href=True):
        link = anchor["href"]
        full_link = urljoin(url, link)
        if urlparse(full_link).netloc == base_domain:
            internal_links.add(full_link)

    # Optionally, extract links from <iframe> tags
    for iframe in soup.find_all("iframe", src=True):
        link = iframe["src"]
        full_link = urljoin(url, link)
        if urlparse(full_link).netloc == base_domain:
            internal_links.add(full_link)

    return list(internal_links)


def crawl_page(page, url, visited, max_depth, current_depth):
    if url in visited or current_depth > max_depth:
        return
    visited.add(url)
    print(f"\nCrawling URL: {url} (Depth: {current_depth})")

    try:
        # Navigate to the URL and wait for the network to be idle
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return

    # Get the full HTML content from the page
    html_content = page.content()

    # Use BeautifulSoup to extract the text from the HTML content
    soup = BeautifulSoup(html_content, "html.parser")
    raw_text = soup.get_text(separator="\n")

    # Clean the text to remove weird spacing and ensure it's on one line (if needed)
    cleaned_text = clean_text(raw_text)
    print(f"Extracted Text Content from {url}:\n{cleaned_text}\n")

    if current_depth >= max_depth:
        return

    # Extract and print the number of internal links found
    internal_links = extract_internal_links(url, html_content)
    print(f"Found {len(internal_links)} internal link(s) on {url}.")

    # Recursively crawl each internal link (if not visited)
    for link in internal_links:
        if link not in visited:
            crawl_page(page, link, visited, max_depth, current_depth + 1)


def main():
    start_url = input("Enter the starting URL: ").strip()
    try:
        max_depth = int(input("Enter maximum crawl depth (e.g., 2): "))
    except ValueError:
        print("Invalid depth value. Using default depth of 2.")
        max_depth = 2

    visited = set()

    with sync_playwright() as p:
        # Launch a headless Chromium browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Start crawling from the given URL
        crawl_page(page, start_url, visited, max_depth, current_depth=0)

        browser.close()


if __name__ == "__main__":
    main()
