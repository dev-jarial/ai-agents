import concurrent.futures
import json
import threading

import requests
from bs4 import BeautifulSoup

# Define the lists of values
solution_categories = [
    "Analytics",
    "Application Development",
    "Artificial Intelligence",
    "Cloud",
    "CRM",
    "ERP",
    "Finance",
    "HRMS",
    "IT Security Services",
    "Sales & Marketing",
    "Software Licenses",
    "Supply Chain",
    "Others",
]

countries = [
    "Australia",
    "Canada",
    "India",
    "Israel",
    "Kenya",
    "Malaysia",
    "Mexico",
    "Nigeria",
    "South Africa",
    "Sri Lanka",
    "United Arab Emirates",
    "United Kingdom",
    "United States of America",
]

oems = [
    "Adobe",
    "AWS",
    "Crowd Strike",
    "Freshworks",
    "Google",
    "IBM",
    "Intuit",
    "Microsoft",
    "Oracle",
    "Quickbooks",
    "Redhat",
    "Sales Force",
    "SAP",
    "Tableau",
    "Tally",
    "VMware",
    "Zoho",
    "Others",
]

# A lock to synchronize printing from multiple threads.
print_lock = threading.Lock()


def parse_product_list(html_content):
    """
    Uses BeautifulSoup to parse the HTML snippet in the 'product_list'
    field and returns the cleaned text.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def get_api_data(page, location, category, oem):
    """
    Sends a POST request to the API endpoint for the given page number and parameters.
    Returns the parsed JSON response if successful or None if an error occurs.
    """
    url = f"https://p2pconnect.in/Home/fetch_data/{page}"
    payload = {
        "action": "fetch_data",
        "location[]": location,
        "category[]": category,
        "oem[]": oem,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(url, data=payload, headers=headers)
    except Exception as e:
        with print_lock:
            print(
                f"Request error on page {page} for {category} | {location} | {oem}: {e}"
            )
        return None

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError as e:
            with print_lock:
                print(
                    f"JSON decode error on page {page} for {category} | {location} | {oem}: {e}"
                )
            return None
    else:
        with print_lock:
            print(
                f"Request failed on page {page} for {category} | {location} | {oem}. Status code: {response.status_code}"
            )
        return None


def process_combination(category, location, oem):
    """
    For a given combination of solution category, location, and OEM,
    iterates through all paginated results, scrapes and prints the extracted content.
    """
    page = 1
    results = []  # You can optionally collect the results here.
    while True:
        data = get_api_data(page, location, category, oem)
        if not data:
            with print_lock:
                print(
                    f"[{category} | {location} | {oem}] No data returned or error on page {page}. Moving on."
                )
            break

        product_html = data.get("product_list", "")
        if product_html:
            product_text = parse_product_list(product_html)
            with print_lock:
                print(f"\n=== {category} | {location} | {oem} | Page {page} ===")
                print(product_text)
            results.append(product_text)
        else:
            with print_lock:
                print(
                    f"[{category} | {location} | {oem}] No product content found on page {page}."
                )

        # Check if there is a "next" page using the pagination HTML
        pagination_html = data.get("pagination_link", "")
        if 'rel="next"' in pagination_html:
            page += 1
        else:
            with print_lock:
                print(f"[{category} | {location} | {oem}] Finished pagination.")
            break
    return results


def main():
    # Build all combinations of (solution_category, country, oem)
    combinations = [
        (category, country, oem)
        for category in solution_categories
        for country in countries
        for oem in oems
    ]

    # Adjust max_workers based on your system and network bandwidth.
    max_workers = 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit a task for each combination
        future_to_combo = {
            executor.submit(process_combination, cat, loc, oem): (cat, loc, oem)
            for (cat, loc, oem) in combinations
        }

        # Process results as tasks complete.
        for future in concurrent.futures.as_completed(future_to_combo):
            combo = future_to_combo[future]
            try:
                # Each future returns the list of results (if needed)
                _ = future.result()
            except Exception as exc:
                with print_lock:
                    print(f"Combination {combo} generated an exception: {exc}")


if __name__ == "__main__":
    main()
