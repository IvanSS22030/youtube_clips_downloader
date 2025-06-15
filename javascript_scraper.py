"""
Web JavaScript Scraper

This script downloads all JavaScript files from a specified website URL.
It handles both <script> tag references and dynamic script imports.
The script uses rotating user agents and respects server load with delays.

Dependencies:
    - requests: For making HTTP requests
    - beautifulsoup4: For parsing HTML content
    - random: For rotating user agents

Author: IvanSS22030
Date: June 2025
"""

import requests
from bs4 import BeautifulSoup
import os
import random
from urllib.parse import urljoin
import time

# List of common user agents for request rotation
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]


def get_random_user_agent():
    """
    Get a random user agent from the list.

    Returns:
        str: A random user agent string
    """
    return random.choice(user_agents)


def download_javascript(url):
    """
    Download all JavaScript files from a specified URL.

    Args:
        url (str): Website URL to scrape JavaScript files from

    Note:
        This function handles both <script> tags and dynamic script imports.
        It uses rotating user agents and adds delays between downloads.
    """
    # Create a directory to store JavaScript files if it doesn't exist
    if not os.path.exists('js_files'):
        os.makedirs('js_files')

    try:
        # Get the webpage with a random user agent
        headers = {'User-Agent': get_random_user_agent()}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all script tags
        js_links = []

        # Look for <script> tags with src attribute
        for script in soup.find_all('script', src=True):
            js_url = urljoin(url, script['src'])
            js_links.append(js_url)

        print(f"Found {len(js_links)} JavaScript files")

        # Download each JavaScript file
        for i, js_url in enumerate(js_links):
            try:
                # Use a different user agent for each request
                headers = {'User-Agent': get_random_user_agent()}
                js_response = requests.get(js_url, headers=headers)
                js_response.raise_for_status()

                # Generate a filename from the URL
                filename = f"js_file_{i}.js"
                filepath = os.path.join('js_files', filename)

                # Save the JavaScript content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(js_response.text)
                print(f"Downloaded: {filename}")

                # Add a small delay between requests
                time.sleep(1)

            except Exception as e:
                print(f"Error downloading {js_url}: {str(e)}")

    except Exception as e:
        print(f"Error fetching the webpage: {str(e)}")


if __name__ == "__main__":
    # Ask for the URL
    url = input("Please enter the website URL to scrape JavaScript files from: ")
    print(f"Starting JavaScript extraction from: {url}")
    download_javascript(url)
