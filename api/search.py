from llm_integrations import get_llm
import requests
import os
import trafilatura
import json
import uuid



API_URL = "https://api.scrapingdog.com/google/"
SCRAPE_DOG_API = os.getenv("SCRAPE_DOG_API")
SYSTEM_INSTRUCTION = '''System instruction: Give an effective search query to search on Google based on the user's question.
                        Search query should specify social media links (youtube, facebook, instagram, reddit, quora, x.com, etc.) to exclude. '''

# app = FirecrawlApp(api_key=FIRECRAWL_API)


def get_search_query(question):
    return get_llm().invoke(SYSTEM_INSTRUCTION + "\n\n" + question)

def get_search_results(query):
    params = {
        "api_key": SCRAPE_DOG_API,
        "query": query,
        "results": 10,
        "country": "vn",
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

    # Scrape all URLs
    contents = scrape_urls(urls)

    results = [
        {
            "content": content,
            "name": name,
            "summary": summary,
            "url": url,
        } 
        for content, name, summary, url in zip(contents, names, summaries, urls)
    ]

    path = save_data_to_unique_file(results)

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

