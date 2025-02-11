import asyncio
import json
import os

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
open_ai_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"]
client = OpenAI()


class CompanyDetails(BaseModel):
    company_name: str
    email_id: str
    mobile_number: str
    general_contact_number: str
    address: str
    locations_offices: list[str]
    categories: list[str]
    products: list[str]
    industry_types: list[str]
    number_of_years: int
    number_of_customers: int
    number_of_employees: int
    customer_names: list[str]
    case_studies: list[str]
    product_brochure: str
    client_testimonials: list[str]
    OEMs: list[str]
    company_profile: str
    management_details: list[str]
    google_rating: int


async def main():
    browser_conf = BrowserConfig(headless=False)  # or False to see the browser
    run_conf = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(url="https://www.ldsinfotech.com", config=run_conf)
        details = result.markdown

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Please provide the following company information. If any information is missing, leave it empty or null:

                        company_name: (String - the name of the company)
                        email_id: (String - company email)
                        mobile_number: (String - mobile contact number)
                        general_contact_number: (String - general office contact number)
                        address: (String - company address)
                        locations_offices: (List of strings - list of office locations)
                        categories: (List of strings - business categories)
                        products: (List of strings - list of products offered by the company)
                        industry_types: (List of strings - list of industries the company operates in like e.g.: IT and networking, health care, education etc.)
                        number_of_years: (Integer - how many years the company has been in operation)
                        number_of_customers: (Integer - number of customers the company serves)
                        number_of_employees: (Integer - number of employees working in the company)
                        customer_names: (List of strings - names of key customers)
                        case_studies: (List of strings - case studies showcasing the company’s work)
                        product_brochure: (String - link or reference to product brochure)
                        client_testimonials: (List of strings - testimonials from clients)
                        OEMs: (List of strings - original equipment manufacturers associated with the company)
                        company_profile: (String - brief description of the company)
                        management_details: (List of strings - names and titles of key management team members)
                        google_rating: (Integer - average Google rating of the company)""",
            },
            {
                "role": "user",
                "content": f"Here is information about the company: \n\n{details}",
            },
        ],
        response_format=CompanyDetails,
    )
    print(completion.choices[0])
    event = completion.choices[0].message.parsed
    event_dict = event.model_dump()
    event_dict_json = json.dumps(event_dict)
    print(event_dict_json)


if __name__ == "__main__":
    asyncio.run(main())
