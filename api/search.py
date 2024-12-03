from llm_integrations import get_llm
import requests
import os
import trafilatura
import json
import uuid



API_URL = "https://api.scrapingdog.com/google/"
SCRAPE_DOG_API = os.getenv("SCRAPE_DOG_API")
SYSTEM_INSTRUCTION = '''System instruction: Give an effective search query to search on Google based on the user's question.
                        Search query should specify social media links (youtube, facebook, instagram, etc.) to exclude. '''

# app = FirecrawlApp(api_key=FIRECRAWL_API)


def get_search_query(question):
    return get_llm().invoke(SYSTEM_INSTRUCTION + "\n\n" + question)

def get_search_results(query):
    params = {
        "api_key": SCRAPE_DOG_API,
        "query": query,
        "results": 10,
        "country": "vi",
        "page": 0
    }
    response = requests.get(API_URL, params=params)
    return response.json()


def scrape_urls(urls):
    for url in urls:
        try:
            print(f"Scraping URL: {url}")
            scrape_data = trafilatura.fetch_url(url)
            content = trafilatura.extract(scrape_data)
        except Exception as e:
            print(f"Error scraping URL {url}: {e}")
            content = ""
        yield content

def search_pipeline(question):
    # Log the current working directory
    print(f"Current working directory: {os.getcwd()}")

    query = get_search_query(question)
    search_results = get_search_results(query)
    urls = [result["link"] for result in search_results["organic_results"]]
    names = [result["title"] for result in search_results["organic_results"]]
    summaries = [result["snippet"] for result in search_results["organic_results"]]

    # Load existing URLs from data/all_urls.json
    try:
        with open('../data/all_urls.json', 'r') as json_file:
            existing_data = json.load(json_file)
            # Ensure existing_data is a list
            if isinstance(existing_data, list):
                existing_urls = {entry for entry in existing_data if isinstance(entry, str)}
            else:
                existing_urls = set()
    except FileNotFoundError:
        print("File not found: data/all_urls.json. Initializing with an empty list.")
        existing_data = []
        existing_urls = set()

    # Filter URLs that are not in existing_urls
    new_urls = [url for url in urls if url not in existing_urls]
    
    # If there are new URLs, append them to the existing data and write back to all_urls.json
    if new_urls:
        with open('../data/all_urls.json', 'w') as json_file:
            # Append new URLs to the existing data
            updated_data = existing_data + new_urls
            json.dump(updated_data, json_file, indent=4)
    else:
        return None
    new_names = [name for url, name in zip(urls, names) if url not in existing_urls]
    new_summaries = [summary for url, summary in zip(urls, summaries) if url not in existing_urls]

    # Scrape only new URLs
    contents = scrape_urls(new_urls)

    new_results = [
        {
            "content": content,
            "name": name,
            "summary": summary,
            "url": url,
        }
        for content, name, summary, url in zip(contents, new_names, new_summaries, new_urls)
    ]

    path = save_data_to_unique_file(new_results)

    return path

def save_data_to_unique_file(data, directory='../data'):
    """
    Save data to a unique file name and return the file path.

    Args:
        data (dict): The data to be saved.
        directory (str): The directory where the file will be saved.

    Returns:
        str: The path to the saved file.
    """
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Generate a unique file name
    unique_filename = f"{uuid.uuid4()}.json"
    file_path = os.path.join(directory, unique_filename)

    # Save the data to the file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

    return file_path

