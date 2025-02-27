import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter

# Configure the content filter (kept as is)
prune_filter = PruningContentFilter(
    threshold=0.9,
    threshold_type="fixed",
    min_word_threshold=5,
)

# Update browser configuration: non-headless and using a common user agent
browser_conf = BrowserConfig(
    headless=False,
)

# Update the crawler run configuration:
# If your version supports waiting for JavaScript to load, set a delay (e.g., js_wait_time)
config = CrawlerRunConfig(
    exclude_external_links=True,
    content_filter=prune_filter,
    wait_for_images=False,
    image_description_min_word_threshold=False,
    # This is an example parameter – check your documentation for the exact name
    js_code="window.scrollTo(0, document.body.scrollHeight);",
)


async def home_scrape(url):
    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(url=url, config=config)

        # Optionally, wait a few extra seconds for any delayed JS execution or challenge resolution
        await asyncio.sleep(5)

        print(result)
        if result.success:
            # Print out the raw markdown content
            print("\n", result.markdown_v2.raw_markdown, "\n")
            internal_links = result.links.get("internal", [])
            for link in internal_links:
                link.pop("title", None)
                link.pop("base_domain", None)
            print("\nInternal links found:", internal_links, "\n")
        else:
            print("Scraping was not successful.")


async def main(url: str):
    await home_scrape(url=url)


if __name__ == "__main__":
    web_site = "https://www.g2.com/products/lds-infotech/reviews"
    asyncio.run(main(url=web_site))
