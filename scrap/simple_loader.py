# for only scrape the visible content, not any depth or html parsing

from langchain_community.document_loaders import UnstructuredURLLoader


def get_urls():
    raw_input = input("Enter one or more URLs, separated by commas: ")
    # Split the input on commas and remove any extra whitespace.
    urls = [url.strip() for url in raw_input.split(",") if url.strip()]
    if not urls:
        raise ValueError("No valid URLs provided.")
    return urls


def load_and_print_content(urls):
    loader = UnstructuredURLLoader(urls=urls)

    try:
        documents = loader.load()
    except Exception as e:
        print(f"An error occurred while loading the documents: {e}")
        return

    # Iterate over the documents and print their content.
    for idx, doc in enumerate(documents, start=1):
        print(f"\n--- Content from URL {idx} ({urls[idx - 1]}) ---")
        print(doc.page_content)


def main():
    try:
        urls = get_urls()
        load_and_print_content(urls)
    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
