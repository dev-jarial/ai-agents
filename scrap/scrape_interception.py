import json

import requests
from bs4 import BeautifulSoup

# Define your lists
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


def parse_product_list(html_content):
    """
    Uses BeautifulSoup to parse the HTML snippet in the 'product_list' field
    and returns the cleaned text.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def get_api_data(page, location, category, oem):
    """
    Sends a POST request to the API endpoint for the given page number and parameters.
    Returns the parsed JSON response (if successful) or None on error.
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
        print(f"Request error on page {page} for {category} | {location} | {oem}: {e}")
        return None

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(
                f"JSON decode error on page {page} for {category} | {location} | {oem}: {e}"
            )
            return None
    else:
        print(
            f"Request failed on page {page} for {category} | {location} | {oem}. Status code: {response.status_code}"
        )
        return None


def scrape_api():
    """
    Iterates through all solution categories, countries, and OEMs.
    For each combination, it scrapes all paginated API results,
    parses the content, and prints it.
    """
    for category in solution_categories:
        for location in countries:
            for oem in oems:
                print("\n==============================================")
                print(f"Scraping for Category: {category}")
                print(f"Location: {location}")
                print(f"OEM: {oem}")
                print("==============================================\n")
                page = 1
                while True:
                    print(f"--- Page {page} ---")
                    data = get_api_data(page, location, category, oem)
                    if not data:
                        print(
                            "No data returned or error occurred; moving to next combination.\n"
                        )
                        break

                    # Extract and parse the product_list HTML
                    product_html = data.get("product_list", "")
                    if product_html:
                        product_text = parse_product_list(product_html)
                        print(f"Content on Page {page}:\n{product_text}\n")
                    else:
                        print(f"No product content found on page {page}.\n")

                    # Check if a "next" link exists in the pagination HTML
                    pagination_html = data.get("pagination_link", "")
                    if 'rel="next"' in pagination_html:
                        page += 1
                    else:
                        print(
                            "No next page found. Finished pagination for this combination.\n"
                        )
                        break


if __name__ == "__main__":
    scrape_api()
