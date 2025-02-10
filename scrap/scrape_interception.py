import json
import re
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def clean_text_per_line(text):
    """
    Cleans text on a per‑line basis:
      - Splits the text into lines.
      - Trims left/right whitespace from each line.
      - Discards empty lines.
    """
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    if len(cleaned_lines) > 1:
        return "\n".join(cleaned_lines)
    elif cleaned_lines:
        return cleaned_lines[0]
    else:
        return ""


def intercept_requests(page):
    """
    Registers an event handler to print details for outgoing requests
    whose URL contains 'fetch_data'.
    """

    def handle_request(request):
        if "fetch_data" in request.url:
            print("\n=== API Request Detected ===")
            print("URL:", request.url)
            print("Method:", request.method)
            post_data = request.post_data or "None"
            print("Post Data:", post_data)
            print("============================\n")

    page.on("request", handle_request)


def intercept_responses(page):
    """
    Registers an event handler to process responses from API calls whose URL
    contains 'fetch_data'. The handler retrieves the raw content and sends it for parsing.
    """

    def handle_response(response):
        if "fetch_data" in response.url:
            print("\n=== API Response Detected ===")
            print("URL:", response.url)
            print("Status:", response.status)
            try:
                # Get the raw response content.
                content = response.text()
                print("Raw Response Content (first 500 characters):")
                print(content[:500])
                # Parse and extract the desired content.
                process_api_response(content)
            except Exception as e:
                print("Error reading response content:", e)

    page.on("response", handle_response)


def process_api_response(api_response):
    """
    Parses the API response.

    If the response is valid JSON, extract the 'product_list' field, which contains
    the HTML snippet with the content. Then parse that HTML with BeautifulSoup and extract the text.
    If JSON parsing fails, fall back to processing the raw response.
    """
    html_content = api_response  # Default to the raw response.
    try:
        data = json.loads(api_response)
        if "product_list" in data:
            html_content = data["product_list"]
        else:
            print("Key 'product_list' not found in JSON. Using raw response.")
    except json.JSONDecodeError:
        print("Response is not valid JSON. Using raw response.")

    # Parse the HTML content and extract the text.
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text(separator="\n", strip=True)
    cleaned_text = clean_text_per_line(text_content)

    print("\n=== Parsed API Content ===")
    print(cleaned_text)
    print("=== End of Parsed API Content ===\n")


def analyze_js_assets(page):
    """
    Extracts JavaScript asset URLs from the page, fetches their content, and
    searches for occurrences of 'fetch_data' to help understand the API usage.
    """
    script_elements = page.query_selector_all("script[src]")
    js_urls = [
        script.get_attribute("src")
        for script in script_elements
        if script.get_attribute("src")
    ]

    print("\n=== Analyzing JavaScript Assets ===")
    for js_url in js_urls:
        full_js_url = urljoin(page.url, js_url)
        print(f"JS asset: {full_js_url}")
        try:
            response = page.request.get(full_js_url)
            if response.ok:
                js_content = response.text()
                if "fetch_data" in js_content:
                    print(f"--> Found 'fetch_data' in {full_js_url}")
                    match = re.search(
                        r".{0,100}fetch_data.{0,100}", js_content, re.DOTALL
                    )
                    snippet = (
                        match.group(0).replace("\n", " ")
                        if match
                        else "No snippet available"
                    )
                    print("Snippet:", snippet)
            else:
                print(f"Failed to load {full_js_url} (status code: {response.status})")
        except Exception as e:
            print(f"Error fetching JS asset {full_js_url}: {e}")
    print("=== End of JS Analysis ===\n")


def auto_paginate(page):
    """
    Checks for a 'next' pagination link on the page and clicks it.
    This function runs in a loop so you can see the new API calls and scraping
    in real time as you paginate.
    """
    while True:
        try:
            # Try to find the "next" pagination link using its attribute (adjust selector if needed)
            next_button = page.query_selector("a[rel='next']")
            if next_button:
                print("Clicking next pagination link...")
                next_button.click()
                # Wait for network requests (adjust timeout if needed)
                page.wait_for_load_state("networkidle", timeout=10000)
                # Allow time for the API response to be intercepted and processed
                time.sleep(2)
            else:
                # No next link found: wait a bit before checking again.
                print("No next pagination link found. Waiting...")
                time.sleep(2)
        except Exception as e:
            print("Error in auto_paginate:", e)
            break


def main():
    with sync_playwright() as p:
        # Launch the browser in headful mode so you can interact with it.
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Register request/response interceptors.
        intercept_requests(page)
        intercept_responses(page)

        # Navigate to the target page.
        start_url = "https://www.p2pconnect.in/"
        page.goto(start_url)
        page.wait_for_load_state("networkidle")

        # Analyze JavaScript assets for API clues.
        analyze_js_assets(page)

        print(
            "Now intercepting API calls and paginating automatically. Press Ctrl+C to exit."
        )
        try:
            # Run auto pagination indefinitely. As the page updates and you paginate,
            # the API interceptors will process and display new content in real time.
            auto_paginate(page)
        except KeyboardInterrupt:
            print("Exiting on user request...")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
