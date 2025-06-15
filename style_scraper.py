"""
Web CSS Scraper

This script downloads all CSS files from a specified website URL.
It handles both <link> stylesheet references and @import rules.
The script uses rotating user agents and respects server load with delays.

Dependencies:
    - requests: For making HTTP requests
    - beautifulsoup4: For parsing HTML content
    - random: For rotating user agents

Author: IvanSS22030
Date: May 2025
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


def download_css(url):
    """
    Download all CSS files from a specified URL.

    Args:
        url (str): Website URL to scrape CSS files from

    Note:
        This function handles both <link> stylesheets and @import rules.
        It uses rotating user agents and adds delays between downloads.
    """
    # Create a directory to store CSS files if it doesn't exist
    if not os.path.exists('css_files'):
        os.makedirs('css_files')

    try:
        # Get the webpage with a random user agent
        headers = {'User-Agent': get_random_user_agent()}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all CSS links
        css_links = []

        # Look for <link> tags with rel="stylesheet"
        for link in soup.find_all('link', rel='stylesheet'):
            if 'href' in link.attrs:
                css_url = urljoin(url, link.attrs['href'])
                css_links.append(css_url)

        # Look for <style> tags that might have @import
        for style in soup.find_all('style'):
            if '@import' in style.text:
                # Basic parsing of @import rules
                imports = style.text.split('@import')
                for imp in imports:
                    if 'url(' in imp:
                        css_url = imp.split('url(')[1].split(')')[
                            0].strip("'").strip('"')
                        css_url = urljoin(url, css_url)
                        css_links.append(css_url)

        print(f"Found {len(css_links)} CSS files")

        # Download each CSS file
        for i, css_url in enumerate(css_links):
            try:
                # Use a different user agent for each request
                headers = {'User-Agent': get_random_user_agent()}
                css_response = requests.get(css_url, headers=headers)
                css_response.raise_for_status()

                # Generate a filename from the URL
                filename = f"css_file_{i}.css"
                filepath = os.path.join('css_files', filename)

                # Save the CSS content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(css_response.text)
                print(f"Downloaded: {filename}")

                # Add a small delay between requests
                time.sleep(1)

            except Exception as e:
                print(f"Error downloading {css_url}: {str(e)}")

    except Exception as e:
        print(f"Error fetching the webpage: {str(e)}")


if __name__ == "__main__":
    # Test URL
    url = ""
    print(f"Starting CSS extraction from: {url}")
    download_css("https://www.muhammadaamirmalik.com/")
