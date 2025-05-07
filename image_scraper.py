"""
Web Image Scraper

This script downloads all images from a specified website URL.
It handles both regular image tags and background images in CSS.
The script respects server load by adding delays between requests.

Dependencies:
    - requests: For making HTTP requests
    - beautifulsoup4: For parsing HTML content
    - urllib: For URL handling and joining

Author: IvanSS22030
Date: May 2025
"""

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import time


def create_directory(directory):
    """
    Create a directory if it doesn't exist.

    Args:
        directory (str): Path of the directory to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def is_valid_image_url(url):
    """
    Check if a URL points to a valid image file.

    Args:
        url (str): URL to check

    Returns:
        bool: True if URL ends with a valid image extension
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    return any(url.lower().endswith(ext) for ext in image_extensions)


def download_images(url, output_dir):
    """
    Download all images from a specified URL.

    Args:
        url (str): Website URL to scrape images from
        output_dir (str): Directory where images will be saved

    Note:
        This function handles both <img> tags and CSS background-images.
        It adds a delay between downloads to be respectful to the server.
    """
    # User agents to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Create images directory
    create_directory(output_dir)

    try:
        # Fetch the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all image tags
        img_tags = soup.find_all('img')

        # Find all elements with background-image in style
        bg_elements = soup.find_all(lambda tag: tag.get(
            'style') and 'background-image' in tag.get('style'))

        downloaded_urls = set()
        count = 0

        # Process regular image tags
        for img in img_tags:
            img_url = img.get('src') or img.get('data-src')
            if img_url:
                img_url = urljoin(url, img_url)
                if is_valid_image_url(img_url) and img_url not in downloaded_urls:
                    try:
                        # Download the image
                        img_response = requests.get(img_url, headers=headers)
                        img_response.raise_for_status()

                        # Generate filename from URL
                        filename = f"image_{count}_{os.path.basename(urlparse(img_url).path)}"
                        if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            filename += '.jpg'

                        # Save the image
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)

                        print(f"Downloaded: {filename}")
                        downloaded_urls.add(img_url)
                        count += 1

                        # Add a small delay to be respectful to the server
                        time.sleep(0.5)

                    except Exception as e:
                        print(f"Error downloading {img_url}: {str(e)}")

        # Process background images
        for element in bg_elements:
            style = element.get('style')
            if 'url(' in style:
                bg_url = style.split('url(')[1].split(')')[
                    0].strip("'").strip('"')
                bg_url = urljoin(url, bg_url)
                if is_valid_image_url(bg_url) and bg_url not in downloaded_urls:
                    try:
                        # Download the background image
                        img_response = requests.get(bg_url, headers=headers)
                        img_response.raise_for_status()

                        # Generate filename
                        filename = f"bg_image_{count}_{os.path.basename(urlparse(bg_url).path)}"
                        if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            filename += '.jpg'

                        # Save the image
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)

                        print(f"Downloaded: {filename}")
                        downloaded_urls.add(bg_url)
                        count += 1

                        # Add a small delay
                        time.sleep(0.5)

                    except Exception as e:
                        print(f"Error downloading {bg_url}: {str(e)}")

        print(f"\nDownloaded {count} images to {output_dir}")

    except Exception as e:
        print(f"Error fetching the webpage: {str(e)}")


if __name__ == "__main__":
    target_url = "https://www.konami.com/games/castlevania/eu/en/"
    output_directory = "images"
    download_images(target_url, output_directory)
